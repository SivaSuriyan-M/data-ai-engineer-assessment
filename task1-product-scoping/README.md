# Task 1: Product Scoping

## What's in This Folder

| File | Description |
|---|---|
| `product-brief.md` | Full product brief — problem framing, user definition, v1 scope, architecture |
| `flow-diagram.png` | Flow diagram showing data sources to user delivery |

---

## The Tool I Scoped

A **BI dashboard + weekly email digest** that lets internal marketing analysts answer the question *"how is our marketing performing and where should we focus?"* in under 2 minutes — without manually logging into each channel platform.

---

## Key Decisions I Made

**Power BI first, Looker Studio for Google stack — not a fixed choice**
The brief's only hard constraint is that the team does not change their tools. Since I do not know the team's environment, I scoped the tool as a decision tree rather than a fixed pick. Power BI is the first preference — it is the most widely adopted BI tool in Indian agency and corporate contexts. Looker Studio is recommended if the team runs on Google Workspace, since it requires only a Google account and zero new setup. The dashboard logic is identical either way. This is a 5-minute question to ask the team before building starts.

**Data sources kept general — not assumed**
The brief does not name which platforms the team uses. I described sources by type (paid search, paid social, web analytics) rather than assuming specific tools. The exact platforms need to be confirmed with the team.

**Internal analyst as the primary user, not the client**
The brief describes a pain point felt by the team doing manual work. Clients are a secondary beneficiary. Building for the analyst first means the tool gets adopted before it gets shared externally — which is the right sequence.

**Excluded AI recommendations from v1**
The core trust problem has to be solved first. An analyst who catches one wrong number will stop using the tool. Before adding AI interpretation, the raw numbers need to be reliable and consistent. AI is a v2 feature.

**Email digest over WhatsApp or Slack for client delivery**
WhatsApp Business API requires Meta approval and adds setup complexity. Email is universally accessible and can be WhatsApp-forwarded by the analyst if needed. Simple beats clever in v1.

---

## What I Would Revisit With More Time

- Talk to one actual internal analyst (30 min would validate or reshape everything)
- Confirm the team's tool stack — Microsoft 365 or Google Workspace — to finalise the Power BI vs Looker Studio call
- Confirm the exact channel mix per client brand — not all brands run the same platforms
- Design the email digest template, not just note it as "in scope"
- Validate the client sharing model against any data privacy requirements

---

## What I Ruled Out and Why

| Option | Why Ruled Out |
|---|---|
| Slack bot | Clients are not in the team's Slack. Limited to text, no visuals. |
| Custom web dashboard | Adds infra and hosting complexity. A BI tool solves the same problem without new infrastructure. |
| AI summary layer | Trust must be established before adding interpretation. v2 feature. |
| Full attribution modelling | Hard problem, would delay shipping. Out of scope for v1. |
| WhatsApp integration | Meta Business API requires approval and adds setup time. Not worth it for v1. |
