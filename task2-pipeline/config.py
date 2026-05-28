# config.py
# All pipeline parameters live here.
# Nothing is hardcoded in pipeline.py — change behaviour by editing this file only.

import os

# ── NewsAPI ──────────────────────────────────────────────
NEWS_API_KEY        = os.environ.get("NEWS_API_KEY", "")
NEWS_API_ENDPOINT   = "https://newsapi.org/v2/everything"
NEWS_QUERY_KEYWORD  = os.environ.get("NEWS_QUERY", "digital marketing India")
NEWS_LANGUAGE       = "en"
NEWS_PAGE_SIZE      = 100
NEWS_SORT_BY        = "publishedAt"
NEWS_FROM_DAYS_AGO  = 7

# ── BigQuery ──────────────────────────────────────────────
BQ_PROJECT_ID       = os.environ.get("BQ_PROJECT_ID", "")
BQ_DATASET_ID       = "marketing_pipeline"
BQ_TABLE_ID         = "news_articles"
BQ_CREDENTIALS_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")

# ── Pipeline behaviour ────────────────────────────────────
WRITE_DISPOSITION   = "WRITE_APPEND"
LOG_LEVEL           = "INFO"