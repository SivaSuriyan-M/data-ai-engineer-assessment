# Tacheon - Data & AI Product Engineer Assessment

**Submitted by:** Siva Suriyan M  
**Date:** May 2026

---

## Overview

This repository contains my submission for the Data & AI 
Product Engineer assessment. It covers two tasks completed 
over 4 days:

- **Task 1** — Product scoping: defining an internal 
  marketing performance tool from scratch
- **Task 2** — Pipeline building: a working Python data 
  pipeline that fetches, transforms, and loads news data 
  into BigQuery

---

## Repo Structure
```
data-ai-engineer-assessment/
├── .gitignore       ← excludes credentials and venv from GitHub
├── README.md        ← overview of both tasks and repo navigation          
├── walkthrough.md   ← decisions, trade-offs and reflection on both tasks
├── task1-product-scoping/
│   ├── README.md
│   ├── product-brief.md   ← full product brief
│   └── flow-diagram.png   ← architecture flow diagram
└── task2-pipeline/
    ├── README.md          ← setup and production thinking
    ├── pipeline.py        ← main pipeline script
    ├── config.py          ← all parameters centralised
    ├── requirements.txt   ← dependencies
    └── queries/
        └── summary.sql    ← BigQuery summary queries
```
---

## Task 1 Summary

Scoped an internal marketing performance tool for a 
marketing technology company supporting multiple client 
brands.

Key decisions:
- Primary user is the internal analyst, not the client
- Tool recommendation depends on existing stack — 
  Power BI for Microsoft environments, Looker Studio 
  for Google Workspace
- AI recommendations deliberately excluded from v1 — 
  trust must be established first
- Weekly email digest as client delivery mechanism

See `task1-product-scoping/product-brief.md` for full 
scoping document.

---

## Task 2 Summary

Built a complete Python data pipeline using NewsAPI 
that fetches marketing news articles, transforms them 
with derived analytical fields, and loads to BigQuery.

Key decisions:
- NewsAPI chosen for marketing relevance and API key 
  requirement — demonstrates real credential handling
- 7 derived fields added including relevance score, 
  source tier, and recency category
- BigQuery table created automatically on first run
- All credentials handled via environment variables — 
  nothing hardcoded

See `task2-pipeline/README.md` for setup and 
production thinking.

---

## Status

- [x] Task 1: Product Scoping
- [x] Task 2: Pipeline Building
