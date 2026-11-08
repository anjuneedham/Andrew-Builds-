# Platform Decisions

All decisions below are **recommendations pending Andrew's approval** unless marked approved. None are approved yet.

| # | Decision | Reason | Alternatives rejected |
|---|---|---|---|
| D1 | Extend Python/Postgres Outreach Desk | Owner auth + TOTP, audit, leads, PWA and Vercel deploy already exist; one login; one dependency | New Vercel + Supabase app (duplicates auth/audit/leads, second login); building inside Agriloop's Supabase (mixes brands, multi-user partner roles, production data) |
| D2 | Keep Agriloop `/ops` running separately | It works and serves Agriloop's own content and partners | Migrating its data (forbidden without approval, no benefit for MVP) |
| D3 | Files in `production/` stay the source for media; app stores metadata + paths | FFmpeg pipeline and QA already work on files | Moving media into DB/storage |
| D4 | Claim gate enforced in app **and** DB trigger | Cannot be bypassed by a bug or direct API call | App-only check |
| D5 | RLS default-deny + single `content_app` role | Meets RLS requirement meaningfully for a one-owner app | Per-row owner columns (no value with one owner) |
| D6 | Metrics manual and append-only | Brief excludes analytics integrations; keeps history honest | Platform API pulls |
| D7 | Docs live in `Andrew-Builds-/docs`; `Content-Platform` repo left empty | Code and docs together; Content-Platform has no commits | Splitting code across two repos |

## Assumptions
- A1 Neon Postgres is the production DB for Outreach Desk (per README); not verified that it is deployed.
- A2 Andrew uses Chrome on the Tab S9 FE+.
- A3 Timezone for calendar is `America/Jamaica`.
- A4 Shorts are tracked as episodes in series `shorts` linked to a parent episode.
- A5 A "factual sentence" = any line Andrew marks `FACT`; lines default to `FACT` so nothing slips through unmarked.

## Questions requiring Andrew's input
- **Q1** Where is `founder-story-dossier/`? (Not in any attached repo or code search.) Upload it or name the repo.
- **Q2** Is Outreach Desk currently deployed? If yes, which Vercel project/Neon DB, and may P0 use a separate Neon branch for testing?
- **Q3** Approve D1 (extend Outreach Desk) and D7 (use `Andrew-Builds-`, leave `Content-Platform` empty or delete it)?
- **Q4** Should Agriloop-brand content (84/85 briefs) ever appear in this platform, or stay in Agriloop `/ops` only?
- **Q5** Exact disclaimer wording for TradeNotes content.
- **Q6** Should the second repo `anjuneedham/agriloop` be inspected, or is `agriloopmain` canonical?
