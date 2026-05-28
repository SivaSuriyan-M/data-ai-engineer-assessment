# pipeline.py
# Marketing News Pipeline
# Fetches articles from NewsAPI, transforms them, loads to BigQuery.

import os
import sys
import logging
import hashlib
import requests
from datetime import datetime, timedelta, timezone
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

import config

# ── Logging setup ────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── BigQuery schema ───────────────────────────────────────
BQ_SCHEMA = [
    bigquery.SchemaField("article_id",              "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("source_name",             "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("author",                  "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("title",                   "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("description",             "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("url",                     "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("published_at",            "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("content_length_chars",    "INTEGER",   mode="NULLABLE"),
    # ── Derived fields ────────────────────────────────────
    bigquery.SchemaField("article_age_hours",       "FLOAT",     mode="NULLABLE"),
    bigquery.SchemaField("recency_category",        "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("source_tier",             "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("keyword_in_title",        "BOOLEAN",   mode="NULLABLE"),
    bigquery.SchemaField("keyword_in_description",  "BOOLEAN",   mode="NULLABLE"),
    bigquery.SchemaField("relevance_score",         "INTEGER",   mode="NULLABLE"),
    bigquery.SchemaField("query_keyword",           "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("ingested_at",             "TIMESTAMP", mode="REQUIRED"),
]

# ── Trusted major news sources ────────────────────────────
TIER_1_SOURCES = {
    "the hindu", "hindustan times", "times of india", "ndtv",
    "the economic times", "livemint", "business standard",
    "bbc news", "reuters", "associated press", "techcrunch",
    "forbes", "entrepreneur", "marketing week", "campaign india",
}

# ── Step 1: Fetch ─────────────────────────────────────────
def fetch_articles(api_key: str, query: str) -> list[dict]:
    """
    Calls NewsAPI and returns a list of raw article dicts.
    Handles API errors gracefully — returns empty list on failure.
    """
    from_date = (
        datetime.now(timezone.utc) - timedelta(days=config.NEWS_FROM_DAYS_AGO)
    ).strftime("%Y-%m-%d")

    params = {
        "q":        query,
        "language": config.NEWS_LANGUAGE,
        "sortBy":   config.NEWS_SORT_BY,
        "pageSize": config.NEWS_PAGE_SIZE,
        "from":     from_date,
        "apiKey":   api_key,
    }

    log.info(f"Fetching articles | query='{query}' | from={from_date}")

    try:
        response = requests.get(
            config.NEWS_API_ENDPOINT,
            params=params,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            log.error(f"NewsAPI error: {data.get('message', 'unknown error')}")
            return []

        articles = data.get("articles", [])
        log.info(f"Fetched {len(articles)} articles successfully")
        return articles

    except requests.exceptions.ConnectionError:
        log.error("Connection error — check internet or NewsAPI may be down")
        return []
    except requests.exceptions.Timeout:
        log.error("Request timed out — NewsAPI did not respond in 15 seconds")
        return []
    except requests.exceptions.HTTPError as e:
        log.error(f"HTTP error: {e.response.status_code} — {e.response.text}")
        return []
    except Exception as e:
        log.error(f"Unexpected error during fetch: {e}")
        return []
    
    # ── Step 2: Transform ─────────────────────────────────────
def classify_source_tier(source_name: str) -> str:
    """
    Classifies source as Tier 1 (major outlet) or Tier 2 (other).
    """
    if not source_name:
        return "Unknown"
    return (
        "Tier 1 - Major Outlet"
        if source_name.lower() in TIER_1_SOURCES
        else "Tier 2 - Other"
    )


def calculate_recency_category(published_at: datetime) -> str:
    """
    Labels article freshness based on age.
    """
    now = datetime.now(timezone.utc)
    age_hours = (now - published_at).total_seconds() / 3600

    if age_hours <= 6:
        return "Breaking"
    elif age_hours <= 24:
        return "Today"
    elif age_hours <= 72:
        return "This Week"
    else:
        return "Older"


def calculate_relevance_score(title: str, description: str, keyword: str) -> int:
    """
    Scores article relevance 0-3 based on keyword presence.
    2 points if keyword in title, 1 point if in description.
    """
    score = 0
    keyword_lower = keyword.lower()

    if keyword_lower in (title or "").lower():
        score += 2
    if keyword_lower in (description or "").lower():
        score += 1

    return score

def transform_articles(raw_articles: list[dict], keyword: str) -> list[dict]:
    """
    Flattens nested API response, handles nulls,
    adds derived fields. Returns clean list ready
    for BigQuery insertion.
    """
    now = datetime.now(timezone.utc)
    transformed = []
    skipped = 0

    for article in raw_articles:

        # ── Skip removed articles ──────────────────────
        if article.get("title") in (None, "[Removed]"):
            skipped += 1
            continue

        # ── Parse published_at safely ──────────────────
        published_at = None
        article_age_hours = None
        recency_category = "Unknown"

        raw_date = article.get("publishedAt")
        if raw_date:
            try:
                published_at = datetime.strptime(
                    raw_date, "%Y-%m-%dT%H:%M:%SZ"
                ).replace(tzinfo=timezone.utc)
                article_age_hours = round(
                    (now - published_at).total_seconds() / 3600, 2
                )
                recency_category = calculate_recency_category(published_at)
            except ValueError:
                log.warning(f"Could not parse date: {raw_date}")

        # ── Flatten nested source field ────────────────
        source_name = (article.get("source") or {}).get("name") or None

        # ── Raw fields ─────────────────────────────────
        title       = article.get("title") or None
        description = article.get("description") or None
        content     = article.get("content") or ""
        url         = article.get("url") or ""

        # ── Derived fields ─────────────────────────────
        keyword_in_title       = keyword.lower() in (title or "").lower()
        keyword_in_description = keyword.lower() in (description or "").lower()
        relevance_score        = calculate_relevance_score(title, description, keyword)
        source_tier            = classify_source_tier(source_name)
        content_length         = len(content) if content else None

        # ── Unique article ID ──────────────────────────
        article_id = hashlib.md5(
            (url or title or "").encode()
        ).hexdigest()

        transformed.append({
            "article_id":             article_id,
            "source_name":            source_name,
            "author":                 article.get("author") or None,
            "title":                  title,
            "description":            description,
            "url":                    url or None,
            "published_at":           published_at.isoformat() if published_at else None,
            "content_length_chars":   content_length,
            "article_age_hours":      article_age_hours,
            "recency_category":       recency_category,
            "source_tier":            source_tier,
            "keyword_in_title":       keyword_in_title,
            "keyword_in_description": keyword_in_description,
            "relevance_score":        relevance_score,
            "query_keyword":          keyword,
            "ingested_at":            now.isoformat(),
        })

    log.info(
        f"Transformed {len(transformed)} articles | "
        f"Skipped {skipped} removed/null articles"
    )
    return transformed

# ── Step 3: Load to BigQuery ──────────────────────────────
def get_or_create_table(client: bigquery.Client, table_ref: str) -> bigquery.Table:
    """
    Returns existing table or creates it if it doesn't exist.
    """
    try:
        table = client.get_table(table_ref)
        log.info(f"Table already exists — appending rows")
        return table
    except Exception:
        log.info(f"Table not found — creating it now")
        table = bigquery.Table(table_ref, schema=BQ_SCHEMA)
        table = client.create_table(table)
        log.info(f"Table created successfully")
        return table


def load_to_bigquery(rows: list[dict]) -> bool:
    """
    Loads transformed rows into BigQuery.
    Returns True on success, False on failure.
    """
    if not rows:
        log.warning("No rows to load — skipping BigQuery write")
        return False

    table_ref = (
        f"{config.BQ_PROJECT_ID}"
        f".{config.BQ_DATASET_ID}"
        f".{config.BQ_TABLE_ID}"
    )

    try:
        client = bigquery.Client(project=config.BQ_PROJECT_ID)
        get_or_create_table(client, table_ref)

        job_config = bigquery.LoadJobConfig(
            schema=BQ_SCHEMA,
            write_disposition=config.WRITE_DISPOSITION,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )

        log.info(f"Loading {len(rows)} rows to {table_ref}")
        job = client.load_table_from_json(
            rows,
            table_ref,
            job_config=job_config
        )
        job.result()

        log.info(f"Successfully loaded {len(rows)} rows to BigQuery")
        return True

    except GoogleAPIError as e:
        log.error(f"BigQuery API error: {e}")
        return False
    except Exception as e:
        log.error(f"Unexpected error during BigQuery load: {e}")
        return False
    
    # ── Main ──────────────────────────────────────────────────
def run_pipeline():
    log.info("=" * 60)
    log.info("Marketing News Pipeline — starting")
    log.info("=" * 60)

    # ── Validate config ────────────────────────────────
    missing = []
    if not config.NEWS_API_KEY:
        missing.append("NEWS_API_KEY")
    if not config.BQ_PROJECT_ID:
        missing.append("BQ_PROJECT_ID")
    if not config.BQ_CREDENTIALS_PATH:
        missing.append("GOOGLE_APPLICATION_CREDENTIALS")

    if missing:
        log.error(
            f"Missing required environment variables: "
            f"{', '.join(missing)}"
        )
        log.error("Set them before running: set VAR_NAME=value")
        sys.exit(1)

    # ── Run pipeline steps ─────────────────────────────
    keyword = config.NEWS_QUERY_KEYWORD

    # Step 1: Fetch
    raw_articles = fetch_articles(config.NEWS_API_KEY, keyword)
    if not raw_articles:
        log.warning("No articles fetched — pipeline ending early")
        sys.exit(0)

    # Step 2: Transform
    transformed = transform_articles(raw_articles, keyword)
    if not transformed:
        log.warning("No articles after transformation — pipeline ending early")
        sys.exit(0)

    # Step 3: Load
    success = load_to_bigquery(transformed)

    if success:
        log.info("=" * 60)
        log.info(
            f"Pipeline completed successfully | "
            f"{len(transformed)} rows loaded"
        )
        log.info("=" * 60)
    else:
        log.error("Pipeline completed with errors — check logs above")
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()