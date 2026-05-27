# Product Brief: Marketing Performance Intelligence Tool
**Version:** 1.0 (Scoping Document)  
**Author:** Siva Suriyan M  
**Date:** May 2026  
**Status:** Draft - Task 1 Submission

---

## 1. The Problem

Marketing teams supporting multiple client brands are repeatedly asked the same question:

> *"How is our marketing performing across channels right now, and where should we be focusing?"*

Today, answering this question looks like this:

1. An analyst logs into each marketing platform separately — paid channels, analytics, social — one by one
2. They manually pull numbers for each channel
3. They stitch the numbers together in a spreadsheet or a chat message
4. They write a response — shaped by their own interpretation on that day
5. The next time someone asks, a different person does the same thing differently

**The result:**
- The answer takes 30–60 minutes to produce every time it is asked
- It looks different depending on who answers it
- If the usual person is unavailable, the question just sits unanswered
- There is no single source of truth the whole team can point to

This is not a data problem. The data exists. It is a **process and consistency problem** — the team lacks a reliable, centralised way to surface the answer they already have the inputs for.

---

## 2. The User

### Primary User: Internal Marketing Analyst

The tool is built first and foremost for the **internal analyst** — the person currently doing the manual work.

**Why this matters:**  
If the internal analyst does not trust and use the tool, it will not survive. They are the ones who know what the numbers mean, catch anomalies, and present findings to clients. Building for them first means the tool gets adopted before it gets shared externally.

**What they need:**
- A single place to check channel performance without logging into multiple platforms
- Confidence that the numbers are current and consistent
- Enough context to walk into a client call prepared

### Secondary User: Client (Brand Stakeholder)

Clients receive a **read-only, shareable view** of their own brand's performance. They do not interact with the tool directly in v1 — they receive a link or a periodic report.

**Why not build for clients first:**  
Clients in the Indian market rarely check dashboards proactively. They respond to what is pushed to them — typically via email or WhatsApp. The dashboard serves as the source of truth; the email digest is the delivery mechanism to the client.

---

## 3. What the Tool Does in V1

### The Core Interaction

An internal analyst opens a BI dashboard and sees — without any manual work — a current snapshot of marketing performance across all active channels for a selected brand.

They can answer the question *"how are we doing and where should we focus?"* in under 2 minutes, using data that refreshed automatically that morning.

### Tool Choice: Fitting Around the Team's Existing Stack

The brief has one hard constraint: the team does not change the tools they use or the way they work. This means the dashboard tool must fit into whatever the team already uses — not introduce something new.

The right tool depends on the team's existing environment, and this is a question to validate before building:

| If the team uses | Recommended Tool | Why |
|---|---|---|
| **Microsoft 365 / Windows environment** | **Power BI** *(first preference)* | Most widely adopted BI tool in Indian agencies and corporate teams. Free desktop version available. Rich connectors, strong visualisation, familiar to most analysts. |
| **Google Workspace (Gmail, Drive, Sheets)** | **Looker Studio** | Free, requires only a Google account, connects natively to Google's own ad and analytics platforms. Zero new tool adoption. |
| **Neither / unclear** | **Looker Studio** | Free with any Google account. Lowest barrier to entry. No install, no licence, browser-based. |

The dashboard logic, features, and scope are **identical regardless of which tool is used**. Only the implementation changes. This is a 5-minute question to ask the team — not a technical debate.

What is explicitly not being introduced in v1: a new data warehouse, a new ETL tool, any paid middleware, or any platform the team does not already interact with.

### V1 Feature Set

| Feature | Description |
|---|---|
| **Channel Overview** | Side-by-side KPIs for each active marketing channel |
| **Key Metrics per Channel** | Spend, impressions, clicks, CTR, conversions, CPA (where available per channel) |
| **Week-on-Week Comparison** | Current week vs previous week for each metric |
| **Top / Bottom Performer Flag** | Simple visual indicator showing which channel is over or underperforming relative to its own recent baseline |
| **Brand Filter** | Switch between client brands without opening a new report |
| **Data Freshness Indicator** | Timestamp showing when data was last pulled — critical for trust |
| **Client Share View** | A filtered, simplified version of the same report accessible via a shareable link |

### What a Successful Interaction Looks Like

> An analyst opens the dashboard at 9am before a client call.  
> They select the client brand from the dropdown.  
> In 90 seconds they can see: paid social spend is up but CTR dropped this week. Search ads are stable. Organic traffic spiked on Tuesday.  
> They walk into the call with a clear "focus on social creative refresh" recommendation — without having opened a single ad platform.

---

## 4. Data Sources and How They Connect

The tool reads from whichever channel platforms the team already uses. The exact sources need to be confirmed with the team — common ones in this context include paid search, paid social, and web analytics platforms.

| Source Type | What It Provides | How It Connects |
|---|---|---|
| **Paid Search Platform** | Spend, impressions, clicks, conversions | Native BI connector or structured CSV export |
| **Paid Social Platform** | Spend, reach, CTR, conversions | Native BI connector or structured CSV export |
| **Web Analytics Platform** | Sessions, organic traffic, goal completions, channel breakdown | Native BI connector or structured CSV export |

### V1 Data Connection Approach

In v1, data connections use **native connectors** built into the chosen BI tool where available. Where a native connector does not exist, the fallback is a **structured weekly CSV export** that feeds into the same data model — no new infrastructure required.

This is a deliberate trade-off: where CSV exports are used, data may be up to a week old. The data freshness timestamp makes this visible at all times so users are never misled.

**The team does not change its tools.** We are reading from platforms the team already uses. No new data warehouse, ETL tool, or middleware is introduced in v1.

---

## 5. V1 Scope — What Is In and What Is Not

### In Scope

- BI dashboard (Power BI if Microsoft stack, Looker Studio if Google stack) with channel KPIs and week-on-week comparison
- Support for whichever paid and organic channels the team already tracks
- Multi-brand filter — one dashboard serves all client brands
- Data freshness timestamp on every view
- Shareable read-only client link
- Weekly email digest summarising top-line numbers (manual send in v1, templated)

### Explicitly Out of Scope for V1

| What | Why It's Out |
|---|---|
| AI-generated recommendations | Clients and analysts need to trust the numbers first before trusting an AI's interpretation. Trust is earned incrementally. |
| Automated email sending | Adds infrastructure complexity. In v1, the analyst sends the templated email manually — this is still faster than today. |
| WhatsApp integration | Meta Business API requires approval and adds meaningful setup time. V1 delivers value without it. |
| Attribution modelling | Cross-channel attribution is a hard problem. Solving it in v1 would delay shipping something useful. |
| Competitor benchmarking | Requires additional data sources not currently in use by the team. |
| Predictive forecasting | Needs historical data volume and model validation. Better suited for v2 once data is being collected consistently. |
| Client login / access control | Shareable links in both Power BI (Publish to Web) and Looker Studio are public by default. If a client requires gated access, additional licensing is needed. Known limitation — noted for v2 planning. |

---

## 6. What Would Make a User Trust It

Trust is the hardest problem this tool has to solve. An analyst who catches one wrong number will stop using it.

Three things build trust in v1:

1. **Data freshness timestamp** — always visible, never hidden. If the data is 3 days old, the user sees that.
2. **Source transparency** — each metric shows which platform it came from. No black-box aggregations in v1.
3. **Consistency over cleverness** — the dashboard shows the same numbers the analyst would find if they logged in manually. No derived scores, no weighted averages, no composite indices in v1. Just the raw channel metrics, cleanly presented.

---

## 7. What I Would Revisit With More Time

- **Talk to actual analysts on the team.** My user assumptions are based on the scenario description. A 30-minute conversation with one internal analyst would either validate or significantly reshape the v1 feature set.
- **Confirm the team's existing tool stack.** A single question — "do you use Microsoft 365 or Google Workspace?" — finalises the Power BI vs Looker Studio decision. I did not make this assumption in the brief; it should be confirmed before building starts.
- **Confirm which marketing channels each client brand actually uses.** Not all brands run the same channel mix. V1 needs to handle partial data gracefully — a brand that does not run paid search should not see an empty paid search panel.
- **Evaluate the client sharing model against data sensitivity requirements.** Public share links are convenient but may not be appropriate for all clients. This needs a direct conversation.
- **Prototype the email digest template.** The weekly email is in scope but I have not designed what it looks like. If it is hard to read, clients will not engage with it.

---

## 8. Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                     DATA SOURCES                         │
│   Paid Search │ Paid Social │ Web Analytics │ (others)   │
│         (whichever platforms the team already uses)      │
└────────┬──────┴──────┬──────┴───────┬────────────────────┘
         │             │              │
  Native connectors / structured CSV exports (no new infra)
         │             │              │
         ▼             ▼              ▼
┌──────────────────────────────────────────────────────────┐
│            BI DASHBOARD LAYER                            │
│                                                          │
│  Power BI     → if team uses Microsoft 365 (preferred)   │
│  Looker Studio → if team uses Google Workspace           │
│                                                          │
│  - Brand filter          - Week-on-week comparison       │
│  - Channel KPIs          - Data freshness timestamp      │
│  - Top/bottom performer flag                             │
└──────────────────────┬───────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────┐     ┌──────────────────────┐
│  Internal View   │     │   Client Share View  │
│  (Full access)   │     │   (Shareable link)   │
│                  │     │   Read-only, filtered│
└──────────────────┘     └──────────────────────┘
                                    │
                         ┌──────────▼───────────┐
                         │  Weekly Email Digest │
                         │  (Manual, templated) │
                         └──────────────────────┘
```

---

## 9. Decisions Made Without Full Information

The brief asks me to be explicit about where I made calls without complete data. Here are those decisions:

| Decision | Assumption Made | Risk If Wrong |
|---|---|---|
| Power BI as first preference, Looker Studio for Google stack | Tool fit depends on team's existing environment — not confirmed | If team uses neither, one needs to be introduced, which touches the constraint |
| Generic channel sources (paid search, paid social, web analytics) | Exact platforms not specified in the brief | Some brands may use platforms with limited or no native connectors |
| Internal analyst as primary user | The scenario implies this | If clients are the primary requestor, the UX needs to change significantly |
| Email as the client delivery mechanism | Common in Indian marketing agency context | Some clients may prefer WhatsApp or another channel |
| Public share link for client view | Data is not sensitive enough to require gated access | If clients have contractual data privacy requirements, this model breaks |

---

*This brief is a living document. Decisions marked above should be validated with the team before development begins.*
