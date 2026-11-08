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

## P0 decisions made during the build (proposed, pending Andrew's approval)
| # | Decision | Reason |
|---|---|---|
| D8 | Added line kind `REFLECTION` to `FACT/OPINION/QUESTION/HYPOTHESIS/DIRECTION/CTA/DISCLAIMER` | The brief requires personal reflections to be distinguishable from facts |
| D9 | `claims.limitations` column; mandatory (CHECK) for `PARTIALLY_CONFIRMED` | The brief says partial claims must display their limitations |
| D10 | `course_plan` singleton table (status DRAFT/READY, fixed 3600 s) in addition to `course_modules` | Architecture says a "READY course plan" must total 3600 s but had no table to hold that status; READY plans are frozen |
| D11 | Extra integrity triggers: CONFIRMED/PARTIAL claims need >= 1 source; rewording a verified claim resets it to UNKNOWN; downgrading a claim returns READY scripts to IN_REVIEW (audited) and their episode to SCRIPTING; READY/LOCKED scripts are frozen; episode needs a READY script to become READY_TO_RECORD | Without these the claim gate could be bypassed by editing after approval, or `CONFIRMED` could mean nothing. Each is a few lines and easy to remove if unwanted |
| D12 | `episodes.parent_episode_id` (A4) and `ideas.episode_id` (promotion link) | Needed for shorts-to-parent and idea promotion in P1 |
| D13 | Each content request = one transaction with `SET LOCAL ROLE content_app`; grant uses `INHERIT FALSE, SET TRUE` on PG16+ | `SET LOCAL` cannot leak across a pooled connection (Neon pooler). Without `INHERIT FALSE` the connecting role inherits the role and bypasses default-deny (found by a failing test) |
| D14 | New tables use native `TIMESTAMPTZ`/`DATE`; legacy tables keep TEXT ISO timestamps | Real types make CHECKs (published >= approved, Monday weeks) possible. API serialises with `default=str` |

## New questions for Andrew
- **Q7 RESOLVED (Andrew): Option A, strict.** A FACT line cannot cite a PARTIALLY_CONFIRMED claim; such claims are usable only in non-FACT lines or after rewriting to a narrower CONFIRMED fact. (Already implemented.)
- ~~Q7 original text:~~ Architecture blocks a `FACT` line that cites a `PARTIALLY_CONFIRMED` claim. The brief says partial claims are shown with their limitations. Keep the stricter rule (partial claims only usable in non-FACT lines), or allow a FACT line to cite a partial claim when its limitation is displayed with it? P0 implements the stricter rule.
- **Q8 RESOLVED (Andrew, 2026-11-08): add a `QA` episode status.** Done in migration `003_episode_qa_status.sql`: `EDITING -> QA -> READY_TO_PUBLISH`. APPROVAL stays the post-level `APPROVED` state (P5).
- **Q9 RESOLVED (Andrew): raise ALL existing buttons.** Done: every button, input, select, chip and tab is >= 48px.
- **Q10** The plan says G0 wording must be given verbatim. Please confirm G0/D1/D7 (and D8-D14) so this is recorded as approved.
