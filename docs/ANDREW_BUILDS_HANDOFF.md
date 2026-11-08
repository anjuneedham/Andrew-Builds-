# Andrew Builds Handoff (shared source of truth)

Last updated: 2026-11-08. **Implementation phase: P0 Foundation BUILT + TESTED, stopped at its approval gate. P1 not started.**
Approval status: G0 assumed from the kickoff brief (verbatim wording not given; please confirm). No G1/G2/G3/G4 approvals requested or used.

## Repositories
| Repo | Role | Branch |
|---|---|---|
| `anjuneedham/Andrew-Builds-` | Home of the platform: Outreach Desk app + production system + docs | `ccr-5358f71e-jn5kgr` (the planning docs from `ccr-35fb16ad-8f40zk` were cherry-picked here) |
| `anjuneedham/Content-Platform` | Empty, no commits, unused (D7) | not modified |
| `anjuneedham/agriloopmain`, `agriloop` | Agriloop. Not touched this phase | - |

## Current implementation phase
P0 (brief's "Phase 1 Foundation"). Plan phases P0-P10: `docs/PLATFORM_BUILD_PLAN.md`. Brief's 7 phases map to P1-P2 (organization), P2 (script/evidence), P3-P4 (recording/assets), P5 (publishing), P6-P8 (business/growth), P9 (course).

## Completed features (P0)
- Additive migration `app/database/migrations/003_episode_qa_status.sql` (Q8 approved: episode status `QA` between EDITING and READY_TO_PUBLISH; replaces only the status CHECK).
- Additive migration `app/database/migrations/002_content.sql`: 19 tables, CHECK constraints, DB triggers for the rules below, RLS enabled and forced, `content_app` role, seed (4 series, 1 course plan).
- Python: `app/core/content/{access,meta,status}.py`; API `app/dashboard/content_api.py` (`GET /api/content/meta|health`), wired in `app/dashboard/app.py` AFTER owner authentication.
- UI: `app/dashboard/static/js/content.js` (read-only foundation page; lists what is NOT built), nav entry, `core.js` icon, CSS (48px nav/touch targets), service worker cache `od-shell-v2`.
- Tests: `app/tests/unit/test_content_p0.py` (109), `app/tests/e2e/content_p0.js` (31 browser steps).

## Rules enforced in the database (so API bugs cannot bypass them)
Claim gate (every FACT line cites >= 1 claim, all CONFIRMED; PARTIAL/PLANNED/UNKNOWN block) - READY/LOCKED scripts frozen - CONFIRMED/PARTIAL claims need a source, PARTIAL needs limitations,
rewording voids verification - claim downgrade returns READY scripts to IN_REVIEW and episode to SCRIPTING (audited) - episode needs a READY script to be READY_TO_RECORD -
metrics append-only (trigger + no UPDATE/DELETE grant) - course READY only at exactly 3600 s and then frozen - safe relative paths for assets/production paths.
Violations raise SQLSTATE 23514 with message prefix `CONTENT_RULE:`; `access.rule_message(exc)` returns the safe text (use it, never raw driver text).

## Database changes
`002_content.sql` and `003_episode_qa_status.sql` (additive; verified not to alter any existing table/column/trigger). Role `content_app` is cluster-global (NOLOGIN, NOBYPASSRLS). It has: DML on content tables (metrics: SELECT/INSERT only),
INSERT on `audit_events`, SELECT on `leads(id,name,business,stage)`. Nothing on credentials/sessions.
**How RLS is used:** every content request runs in ONE transaction with `SET LOCAL ROLE content_app` (`access.content_session`). Never use plain `SET ROLE` (leaks across pooled connections). Any new content route must use `content_session`.
Test DB for this phase: local Postgres 16.15, throwaway (`ab_throwaway`, `ab_e2e`). Not Neon.

## Existing functionality reused (unchanged)
Owner login + TOTP + sessions + rate limit (`core/auth/owner_login.py`), `audit_events`, `leads` (FK target for `content_lead_links`), migration runner with advisory lock (`core/db.py`), PWA shell/CSP/static serving (`dashboard/app.py`), test helpers (`tests/dbutil.py`, `tests/authutil.py`), `production/tools/qa.py project` secret scan.
`production/` files were read to verify the docs; NOT imported (G2).

## Tests and results
- Baseline before changes: 44/44 PASSED. After P0 + QA status: 155/155 PASSED. Browser tablet run: 31/31 PASSED, 0 console errors, 0 5xx.
- How to run: `cd app && TEST_DATABASE_URL=postgresql://... python -m unittest discover -s tests -t .` (role must be SUPERUSER for the RLS tests, else they skip loudly; use a THROWAWAY database).
  Browser: start `scripts/run_local.py` on a fresh DB owned by a non-superuser, complete setup, then `BASE=... PASSWORD=... TOTP_SECRET=... OUT=... node tests/e2e/content_p0.js`.
- Full tables: `docs/PLATFORM_STATUS.md`.

## Untested functionality
Neon/Vercel/production; Postgres other than 16.15; real Tab S9 FE+ and non-Chromium browsers; old sales `journey.js`; service-worker upgrade and offline; concurrent cold-start migration with 002. Everything in P1-P10 is unbuilt.

## Known defects / limitations
See `PLATFORM_STATUS.md` "Known issues" (8 items). Key ones: PG < 16 connecting role inherits `content_app`; (Q9 done: all controls now 48px; drawer/data-heavy states unmeasured); LOCKED scripts citing a later-downgraded claim need a P2 warning; deferrable unique errors surface at COMMIT; imported claim codes must advance `claims_code_seq`.

## Security status
One owner login (scrypt + TOTP) unchanged; all `/api/content/*` routes are 401 without a valid session (tested in unit + live curl); RLS enabled+forced everywhere with a single `content_app` policy; `content_app` has no access to credentials/sessions/personal contact fields; no secrets in source (grep + qa.py scan clean); no innerHTML in new JS; CSP unchanged (no inline script); hide-list terms are never returned by any route.
**Honest limit:** RLS is defense in depth against OTHER database roles (read-only/BI/leaked secondary credentials). Someone holding the owner `DATABASE_URL` can still `SET ROLE content_app` or alter policies.

## G1 checklist (before any non-throwaway database)
1. The migrating role must be able to create `content_app` (CREATEROLE) or already hold ADMIN OPTION on it, and be allowed `GRANT content_app TO CURRENT_USER`. On Neon the project owner role normally qualifies: UNVERIFIED.
2. Prefer Postgres 16+ (for default-deny against the connecting role).
3. Run first on a Neon BRANCH, not the main database. Andrew approves the target.

## Pending approvals
G0 confirmation + D1/D7; decisions D8-D14; questions Q1-Q10 in `docs/PLATFORM_DECISIONS.md` (Q7 partial-claim rule, Q8 QA status, Q9 button sizes matter before P1/P2).

## Exact next implementation task
After Andrew approves P0, start **P1 Content calendar + idea backlog** (plan section P1): series/episodes/ideas CRUD routes under `/api/content/*` using `content_session`; month/week calendar in `America/Jamaica`; promote idea -> episode; episode status transitions as a state machine; audit on delete; Playwright at 1280x800 and 800x1280. Episode statuses now include QA (003). Do NOT start P1 until approved.

Suggested approval reply: **"Approved: P0 accepted. G0, D1, D7 and D8-D14 approved. Begin P1 using a throwaway test database."** (edit as needed; answer Q7-Q9)

---

# CONTENT PLAN (added 2026-11-08) - STATUS: PROPOSED, NOT APPROVED

Content work is documentation only. Nothing was recorded, edited, published, deployed, imported or written to any database. The platform was NOT configured with these templates: only P0 exists (read-only page, no editing screens, no import tools), so there was nothing to import into without approval (G1/G2).

## Confirmed platform capabilities (verified in code on this branch, P0)
- Schema for series, episodes (IDEA → SCRIPTING → READY_TO_RECORD → RECORDED → EDITING → QA → READY_TO_PUBLISH → PUBLISHED), ideas, scripts/lines/claims/sources, shots, assets, posts, metrics (append-only), growth_log, content_lead_links, course_plan/modules, hide_list.
- DB-enforced: claim gate (FACT lines need CONFIRMED claims, Q7 strict), script freeze, claim-downgrade cascade, course READY only at 3600 s, post approval/publish timestamps.
- Seeded: 4 series (`course`, `bootstrapper-experiment`, `andrew-builds`, `shorts`) and course_plan "From Sales to SaaS".
- NOT available: any create/edit UI or API, calendar, app-layer checks (banned phrases, hide list, disclaimers), imports. Metrics table lacks impressions, CTR, AVD, retention, profile visits, link clicks. Asset kinds lack camera/document/short export.
- Existing file pipeline `production/tools/*` (produce, qa, make_docs, new_episode, suggest_content) works per its README; not re-run this session.

## Content system (template locations)
| Doc | Purpose |
|---|---|
| `docs/CONTENT_STRATEGY.md` | Positioning, 5 pillars, documentary format, rules, workflow + gates, reuse map |
| `docs/COURSE_60_MINUTE_PLAN.md` | From Sales to SaaS: 7 sections, 15 lessons, exactly 60:00 |
| `docs/REPEATABLE_EPISODE_TEMPLATE.md` | 13-field episode plan |
| `docs/REPEATABLE_SCRIPT_TEMPLATE.md` | Line-by-line script with kinds + claim IDs; claim checker |
| `docs/SHOT_LIST_TEMPLATE.md` | Shot columns + tablet capture rules |
| `docs/ASSET_REGISTER_TEMPLATE.md` | Naming, versioning, types, register |
| `docs/PUBLISH_CHECKLIST.md` | Mandatory per-post checklist |
| `docs/REPURPOSING_PLAYBOOK.md` | Long → short process, standalone tests |
| `docs/METRICS_REVIEW_PLAYBOOK.md` | Weekly/monthly review; platform vs business outcomes |

## Summary
- **Pillars:** P1 Build in Public · P2 SaaS with AI · P3 Founder Lessons · P4 Trading-Journal Journey · P5 Agriloop Decision Documentary.
- **Course:** Start here 4:00 · What sales taught me 12:00 · Building with Claude Code 18:00 · Validation: Agriloop 12:00 · TradeNotes experiment 8:00 · Documenting the journey 4:00 · Close 2:00 = **60:00**.
- **Evidence rules:** every factual sentence = FACT line citing CONFIRMED claim(s); PARTIAL/PLANNED/UNKNOWN only in REFLECTION/OPINION/HYPOTHESIS/QUESTION lines; banned phrases; trading disclaimer; consent; hide list; nothing published without Andrew.
- **Workflow / gates:** IDEA →G-IDEA→ evidence → plan → script →G-SCRIPT→ shot list → recording →G-RECORD→ edit →G-EDIT→ QA →G-QA→ G-PUBLISH → Andrew publishes → metrics → review. Approval = explicit "Approved G-<GATE> <code>".
- **Repurposing:** >= 3 shorts per episode only when moments pass 6 standalone tests; shorts are `shorts` episodes with `parent_episode_id`.
- **Metrics:** manual, 48 h / 7 d / 28 d; business outcomes (inquiries, attributed leads via cta_code) kept separate.

## Outstanding questions (content)
- **Q1 (still open)** `founder-story-dossier/` not found (timeline, claims register, course blueprint, S01-S46 shot list, funnel, knowledge gaps, founder answers). Course plan and templates were built without it and must be reconciled when it arrives.
- **Q5 (still open)** exact trading risk disclosure wording.
- **Q4 (still open)** may Agriloop-brand briefs (85 found, brief says 84) be used for Andrew Builds content?
- Q-C1 Which customer-service / corporate employers, dates, and online ventures may be named? (needed for course 2.1-2.3, P3)
- Q-C2 Agriloop real beta numbers (listings, farmers, buyers, transactions) with sources, or confirm "very little traction" is the only public statement.
- Q-C3 Course host: YouTube (free) or a course platform? Free or paid? (no funnel was found)
- Q-C4 TradeNotes repo name and first-commit date; is it attached to any session?
- Q-C5 Consent: any people (family, farmers, YardScale clients/team) Andrew wants to show? Written consent needed.
- Q-C6 Is episode-001/002 (Outreach Desk-focused) still wanted, or replaced by the Bootstrapper Experiment arcs A/B?
- Q-C7 Approve proposed schema additions (metrics gap columns, asset kinds) as a later migration?

## Current approval status
Content strategy, course plan and templates: **NOT APPROVED** (gate CS-0). Platform P0 approval still pending as above.

## Exact next step for CONTENT-BUILD (only after CS-0 approval)
1. Ask Andrew Q-C2 and Q-C4; turn answers into claims (C-###) with sources in a working claims register `production/claims/CLAIMS_REGISTER.md` (file-based until P2 UI exists).
2. Run `production/tools/suggest_content.py` / review git logs to list real moments for Arc A (Agriloop, last 60 days); propose 3 episode ideas to Andrew for **G-IDEA**. No calendar dates until approved.
3. For the approved idea: `python3 production/tools/new_episode.py <N> "<title>"`, fill REPEATABLE_EPISODE_TEMPLATE, then a draft script in REPEATABLE_SCRIPT_TEMPLATE format, then stop at **G-SCRIPT**.
Suggested reply: "Approved CS-0: content strategy, course plan and templates accepted." (plus answers to Q1, Q5, Q-C1..C7).
