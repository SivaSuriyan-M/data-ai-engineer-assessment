-- summary.sql
-- Marketing News Pipeline — Summary Queries
-- Run these in BigQuery to extract insights from ingested data.

-- ── Query 1: Overall summary by keyword ──────────────────
-- Shows article volume, source quality, keyword relevance,
-- and recency breakdown for the most recent pipeline run.

SELECT
    query_keyword,
    COUNT(*)                                       AS total_articles,
    COUNTIF(recency_category = 'Breaking')         AS breaking_news,
    COUNTIF(recency_category = 'Today')            AS today_count,
    COUNTIF(recency_category = 'This Week')        AS this_week_count,
    COUNTIF(recency_category = 'Older')            AS older_count,
    COUNTIF(source_tier = 'Tier 1 - Major Outlet') AS tier1_sources,
    COUNTIF(keyword_in_title = TRUE)               AS keyword_in_title,
    COUNTIF(relevance_score >= 2)                  AS high_relevance,
    ROUND(AVG(article_age_hours), 1)               AS avg_age_hours,
    MAX(ingested_at)                               AS last_ingested_at

FROM `tacheon-pipeline.marketing_pipeline.news_articles`

GROUP BY query_keyword;


-- ── Query 2: Most recent articles ────────────────────────
-- Shows latest 10 articles ordered by publish date.
-- Useful for daily morning briefing for marketing analysts.

SELECT
    title,
    source_name,
    source_tier,
    recency_category,
    article_age_hours,
    relevance_score,
    published_at

FROM `tacheon-pipeline.marketing_pipeline.news_articles`

ORDER BY published_at DESC

LIMIT 10;


-- ── Query 3: Source tier breakdown ───────────────────────
-- Shows distribution of articles by source quality
-- and relevance score.

SELECT
    source_tier,
    relevance_score,
    COUNT(*) AS count

FROM `tacheon-pipeline.marketing_pipeline.news_articles`

GROUP BY source_tier, relevance_score
ORDER BY source_tier, relevance_score DESC;