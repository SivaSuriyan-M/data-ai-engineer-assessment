# Assessment Walkthrough

**Candidate:** [Your Name]  
**Date:** May 2026  
**Role:** Data & AI Product Engineer — Tacheon / Smacient

---

## How I Approached This Assessment

When I received the brief, the first thing I did was read it fully before touching any code or writing any document. Two things stood out immediately:

1. The only hard constraint was that the team would not change their tools
2. The assessors wanted to see thinking, not just output — commit history, decisions, trade-offs

So I started the GitHub repo on Day 1 before writing anything, committed regularly as I worked, and wrote commit messages that described what I changed and why.

---

## Task 1: Product Scoping

### The Problem I Was Solving

A marketing team supporting multiple client brands gets asked the same question constantly:

> "How is our marketing performing across channels right now, and where should we focus?"

Today someone manually logs into each platform, pulls numbers, stitches them together, and writes a response. The answer looks different every time depending on who does it. If that person is busy, the question goes unanswered.

This is not a data problem — the data exists. It is a process and consistency problem.

### How I Thought About the Tool

My first instinct was to jump to a solution. I stopped myself and worked through the questions the brief suggested:

**Who is the primary user?**
I committed to the internal analyst — not the client. The analyst is the one doing the manual work today. If they don't trust and use the tool, it won't survive long enough to reach clients.

**What does a successful interaction look like?**
An analyst opens one place, selects a client brand, and in under 2 minutes can walk into a client call knowing which channel is performing and which needs attention — without logging into a single ad platform.

**What tool fits around the team's existing stack?**
This is where I had to be careful. The brief's only hard constraint was no new tools. I initially considered Power BI because I have hands-on experience with it. But I caught myself — I was assuming the team uses Microsoft tools without any evidence.

So I changed my approach: instead of picking one tool, I scoped a decision tree:
- If the team uses Microsoft 365 → Power BI (first preference, widely adopted in Indian agencies)
- If the team uses Google Workspace → Looker Studio (already available with any Google account, zero new tool adoption)
- If neither is clear → ask before building

The dashboard logic is identical either way. This is a 5-minute question to ask the team — not a technical debate.

**What did I leave out of v1 and why?**

| What | Why |
|---|---|
| AI recommendations | Trust must be established before adding interpretation |
| Automated email | Adds complexity — manual templated email is still faster than today |
| WhatsApp integration | Meta Business API needs approval, adds setup time |
| Attribution modelling | Hard problem, would delay shipping something useful |

### What I Would Revisit With More Time

The biggest gap in my brief is that I never spoke to an actual analyst. Every user assumption I made came from the scenario description. A 30-minute conversation would validate or significantly change the v1 feature set. That conversation should happen before a single line of code is written.

---

## Task 2: Pipeline Building

### Why I Chose NewsAPI

I considered no-key APIs like Open-Meteo first — easier setup, no authentication. But I reconsidered. This task is evaluating pipeline skills. A no-key API skips credential handling entirely — one of the most important real-world skills in building data pipelines.

NewsAPI requires a free API key and is directly relevant to a marketing technology company. Marketing teams track how their client brands appear in the news — volume, source quality, recency. This pipeline automates what someone currently does manually every morning.

It also connects directly to Task 1: the same manual, inconsistent, person-dependent problem exists for news monitoring as it does for channel performance reporting.

### How I Structured the Code

I separated the code into three clear layers:

**`config.py`** — all parameters in one place. API key, BigQuery project ID, keyword, date range — everything lives here. Nothing is hardcoded in `pipeline.py`. Sensitive values come from environment variables so they never touch the codebase.

**`pipeline.py`** — three functions, one job each:
- `fetch_articles()` — calls NewsAPI, handles 4 types of errors gracefully
- `transform_articles()` — flattens nested JSON, handles nulls, adds 7 derived fields
- `load_to_bigquery()` — creates table automatically, appends rows
- `run_pipeline()` — validates config, calls all three in order

**`queries/summary.sql`** — meaningful SQL queries that show the data is useful, not just stored.

### The Derived Fields I Added

Raw NewsAPI data tells you what articles exist. The derived fields tell you what they mean:

- `article_age_hours` — how fresh is the news
- `recency_category` — Breaking / Today / This Week / Older
- `source_tier` — Tier 1 Major Outlet vs Tier 2 Other
- `relevance_score` — 0 to 3 based on keyword presence in title and description
- `article_id` — MD5 hash of URL to prevent duplicate rows on re-runs
- `ingested_at` — pipeline run timestamp for audit trail

### Security Decisions

- API key and credentials never hardcoded — always environment variables
- Service account has only two roles: BigQuery Data Editor and BigQuery Job User
- I chose Data Editor over Admin deliberately — principle of least privilege. If the key is leaked, damage is contained to data operations only.
- Service account JSON is in `.gitignore` — can never be accidentally committed

### What Happened When I Ran It

The pipeline ran successfully on first attempt except for one error — the service account was missing the `BigQuery Job User` role. Data Editor allows reading and writing data, but loading data requires creating a BigQuery job, which needs a separate permission. I added the role, re-ran, and 57 rows loaded successfully.

This is exactly the kind of thing you encounter in a real engineering role — documentation says one thing, actual permissions require something slightly different.

### Production Thinking

**Scheduling:**
On GCP, the natural approach is Cloud Scheduler triggering a Cloud Run Job on a cron — something like `0 7 * * *` to run every morning at 7am IST. The pipeline is already stateless and parameterised so it would drop straight into that setup without changes.

That said, my background is more in the Microsoft/Azure stack — tools like Azure Data Factory where you can set up a scheduled trigger or an event-based trigger depending on what makes more sense for the use case. ADF also has a BigQuery connector so it could orchestrate this same pipeline if the team already lives in Azure. Both approaches work — the right one depends on where the team's infrastructure already sits.

**How would you know if it failed:**
A few layers here. First, the pipeline exits with code 1 on any failure — Cloud Run picks that up and marks the job as failed automatically. Second, all the log messages we wrote using Python's logging module get captured in Cloud Logging — so if something breaks, you can see exactly which step failed and why. Third, you'd set a Cloud Monitoring alert to notify you via email or Slack if the job fails or if no rows were loaded within an expected window.

One thing I'd add that's not in the current code — a retry mechanism. If the pipeline fails because NewsAPI had a momentary blip, you don't want to wake someone up at 7am for something that would fix itself in 60 seconds. Cloud Run supports automatic retries on failure, so I'd configure 2-3 retries before it actually alerts anyone.

**Scaling to 10x volume:**
A few things I'd look at. On the BigQuery side — partition the table by `ingested_at` date and cluster by `query_keyword` and `source_tier`. BigQuery doesn't use traditional indexes like SQL Server or MySQL, but partitioning and clustering do the same job — queries only scan the data they actually need instead of the full table. That alone makes a huge difference at scale.

On the pipeline side — switch to incremental loads. Right now we fetch the last 7 days every run, which means we're re-processing articles we've already seen. Adding a watermark timestamp (tracking the last successful run) means each run only fetches genuinely new articles. The `article_id` MD5 hash already prevents duplicate rows, but incremental fetch saves API quota and processing time.

For the transform layer at real scale — a single Python script running on one machine won't cut it. That's where something like Databricks or Dataflow comes in for parallel processing. I've worked with Databricks, Synapse, and ADLS in other contexts — the pattern is the same, just the execution layer changes.

I want to be honest here — my hands-on pipeline experience has been in Microsoft Fabric, which I've actually worked with practically. That gave me a solid grasp of the underlying concepts — incremental loads, partitioning, orchestration, error handling — and helped me understand how similar tools like ADF, Databricks, and Synapse fit together conceptually, even though I haven't worked on those hands-on yet.

Python-based pipelines on GCP were new to me going into this assessment. But because the core concepts translate across stacks, picking it up wasn't starting from zero. Building this end to end in 4 days gave me a much more concrete understanding of how GCP approaches the same problems I've seen solved in Fabric.

---

## What I Would Do Differently With More Time

**Task 1:**
- Talk to one actual internal analyst before writing anything — every assumption I made came from the scenario description, not a real conversation
- Design the email digest template properly, not just mention it as in scope
- Validate the client sharing model against any data privacy requirements the clients actually have

**Task 2:**
- Add unit tests for the transform functions — especially `calculate_relevance_score()` and `classify_source_tier()`
- Add a `--dry-run` flag so you can test the fetch and transform without actually writing to BigQuery
- Support multiple keywords in one run to track several client brands simultaneously
- Add `last_run.json` to make the pipeline truly incremental — only fetch articles published after the last successful run

---

## Final Thought

The brief said a focused solution that works and is well-documented will always score higher than an expansive one that cannot be walked through. I kept that in mind the whole way through. Every decision I made, I made deliberately — and where I made calls without full information, I said so explicitly rather than pretending I knew things I didn't.
