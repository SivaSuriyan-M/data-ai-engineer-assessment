# Task 2: Marketing News Data Pipeline

## What This Pipeline Does

Fetches news articles from **NewsAPI** based on a configurable keyword (e.g. "digital marketing India"), transforms the raw response into a clean analytical table, and loads it into **BigQuery** for querying.

**Why NewsAPI:**
Marketing teams track how their client brands and industry topics appear in the news — volume, source quality, and recency. This pipeline automates what someone currently does manually every morning by Googling and copy-pasting into a spreadsheet.

This directly connects to Task 1: the same inconsistency problem (manual, person-dependent, slow) exists for news monitoring as it does for channel performance reporting.

---

## Folder Structure

```
task2-pipeline/
├── pipeline.py       ← fetch → transform → load
├── config.py         ← all parameters centralised
├── requirements.txt  ← Python dependencies
└── queries/
    └── summary.sql   ← BigQuery summary queries
```

---

## How to Run

### 1. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set environment variables
```bash
# Windows
set NEWS_API_KEY=your_newsapi_key_here
set BQ_PROJECT_ID=your_gcp_project_id
set GOOGLE_APPLICATION_CREDENTIALS=path\to\service_account.json
```

### 4. Run the pipeline
```bash
python pipeline.py
```

---

## BigQuery Setup

1. Go to console.cloud.google.com/bigquery
2. Create a new project
3. Create a dataset named `marketing_pipeline` in region `asia-south1`
4. Create a service account with two roles:
   - **BigQuery Data Editor** — read and write data
   - **BigQuery Job User** — create and run load jobs
5. Download the service account JSON key
6. Set `GOOGLE_APPLICATION_CREDENTIALS` to the path of that JSON file
7. The pipeline creates the table automatically on first run

**Why Data Editor and not Admin:**
Principle of least privilege — the pipeline only needs to read and write data, not manage billing or projects. If the key is ever leaked, the damage is contained.

**BigQuery Sandbox limitations:**
- No scheduled queries natively — needs Cloud Scheduler
- Data expires after 60 days
- No streaming inserts — batch load used instead

---

## Pipeline Steps Explained

### Step 1: Fetch
- Calls NewsAPI `/v2/everything` endpoint
- All parameters live in `config.py` — nothing hardcoded
- Handles: connection errors, timeouts, HTTP errors, invalid API responses

### Step 2: Transform
Flattens nested JSON and adds derived fields:

| Field | Description |
|---|---|
| `article_age_hours` | Hours since article was published |
| `recency_category` | Breaking / Today / This Week / Older |
| `source_tier` | Tier 1 Major Outlet / Tier 2 Other |
| `keyword_in_title` | Keyword appears in title |
| `keyword_in_description` | Keyword appears in description |
| `relevance_score` | 0–3 score based on keyword presence |
| `article_id` | MD5 hash of URL — prevents duplicates |
| `ingested_at` | Pipeline run timestamp — audit trail |

### Step 3: Load
- Creates BigQuery table automatically if not exists
- Uses `WRITE_APPEND` — each run adds rows without overwriting history
- Configurable via `config.py`

---

## SQL Summary Queries

See `queries/summary.sql` for full queries.

**Query 1 — Summary by keyword (sample output):**

| query_keyword | total_articles | tier1_sources | avg_age_hours |
|---|---|---|---|
| digital marketing India | 57 | 5 | 38.4 |

**Query 2 — Most recent articles (sample output):**

| title | source_name | recency_category |
|---|---|---|
| Why AI Marketing Agencies Will Dominate | Finessse.digital | This Week |
| Byju Raveendran sentenced to jail | The Indian Express | This Week |

---

## Production Thinking

### How would you schedule this pipeline?
Use **Google Cloud Scheduler** to trigger a **Cloud Run Job** on a cron schedule (e.g. every morning at 7am IST):

```
Cloud Scheduler (cron: 0 7 * * *)
    → triggers Cloud Run Job
        → runs pipeline.py
            → loads to BigQuery
```

### How would you know if it failed?
Three layers:
1. **Exit codes** — pipeline exits with code 1 on failure, Cloud Run marks job as failed
2. **Cloud Logging** — all log messages captured automatically
3. **Alerting policy** — Cloud Monitoring sends email or Slack alert if job fails

### What would you change for 10x data volume?
- Switch to **BigQuery Storage Write API** for higher throughput
- Add **pagination** to fetch more than 100 articles
- Move transforms to **Dataflow** for parallel processing
- Add **deduplication** in BigQuery using MERGE statements
- Store raw responses in **Cloud Storage** before transforming — allows reprocessing if schema changes

---

## Security

- API key and credentials never hardcoded — always environment variables
- Service account has minimum required permissions only
- Service account JSON key is in `.gitignore` — never committed to GitHub

---

## What I Would Do Differently With More Time

- Add unit tests for transform functions
- Add `--dry-run` flag to test without loading to BigQuery
- Support multiple keywords in one run to track several client brands simultaneously
- Implement proper deduplication using BigQuery MERGE
- Add `last_run.json` to avoid re-fetching already ingested articles
