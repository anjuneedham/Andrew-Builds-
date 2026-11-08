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
See `PLATFORM_STATUS.md` "Known issues" (8 items). Key ones: PG < 16 connecting role inherits `content_app`; existing Outreach Desk buttons are 40px; LOCKED scripts citing a later-downgraded claim need a P2 warning; deferrable unique errors surface at COMMIT; imported claim codes must advance `claims_code_seq`.

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
