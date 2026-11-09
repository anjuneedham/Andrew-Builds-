# Prompt: continue the Andrew Builds content platform build (P1, slices 2-5)

Paste everything below into a new Claude Code session that has `anjuneedham/Andrew-Builds-` attached, working on branch `ccr-be9f9528-gocxxq`.

---

You are the platform engineer for Andrew Builds. Continue **P1 Content calendar + idea backlog** of the content platform, in the repo `Andrew-Builds-`, branch `ccr-be9f9528-gocxxq`. Do NOT create or push other branches. Do NOT open a pull request unless asked.

## Read first
`docs/ANDREW_BUILDS_HANDOFF.md` (section "PLATFORM BUILD P1"), `docs/PLATFORM_BUILD_PLAN.md` (P1 and the testing standard), `docs/PLATFORM_ARCHITECTURE.md`, `docs/PLATFORM_STATUS.md`, `app/core/content/` and `app/dashboard/content_api.py`, `app/dashboard/static/js/content.js`.

## State
Slice 1 of 5 is done: series + episodes API and status state machine (`core/content/episodes.py`, 15 tests). The full suite is 174 tests and must stay green. Slices left, one per ~20%:
2. Ideas API (list/create/edit/delete, audit) and **promote idea -> episode** (sets `ideas.episode_id`, status SCHEDULED, creates the episode in one transaction).
3. Calendar API: month and week views, dates interpreted in `America/Jamaica`, reschedule an episode's `planned_date`.
4. UI: episode list/detail and idea backlog screens, tablet-first (Galaxy Tab S9 FE+), 48px touch targets, no innerHTML, no inline script (CSP), vanilla JS like the rest of the app. Create, edit, status change and delete with confirmation.
5. UI: month/week calendar, reschedule, then Playwright checks at 1280x800 and 800x1280 and the P1 acceptance list.

## Rules (binding)
- Work ONE slice (about 20%) at a time. After each slice: run the full suite, run a mutation check (break the rule on purpose, see a test fail, restore the file byte-for-byte), update `PLATFORM_BUILD_PLAN.md` and the handoff, commit, push to `ccr-be9f9528-gocxxq`, then STOP and give Andrew a short update (what was built, tests, what is next, any decision needed). Wait for "continue".
- Every route: 401 without a session, 400 invalid input, 404 unknown id, 409 for rule/uniqueness/dependency conflicts, safe messages only (never driver text). Every write runs inside `content_session` (role `content_app`) and writes an audit row; a failed write writes none.
- Test against a THROWAWAY Postgres only: `pg_ctlcluster 16 main start`, then `TEST_DATABASE_URL=postgresql://<superuser>:<pw>@127.0.0.1:5432/<throwaway db> python3 -m unittest discover -s tests -t .` (create the role/database yourself; the role must be a superuser for the RLS tests). Never use the production DATABASE_URL.
- No new migration without telling Andrew first (G1: never run a migration on a non-throwaway database). If a slice needs one, make it additive and re-runnable, test it twice, and ask before it touches anything live.
- No deployment, env-var change, publishing, sending or sharing without Andrew's explicit approval (G3/G4). Pushes to this branch can create Vercel preview builds; do not change Vercel settings.
- Never print, request or store passwords, tokens, connection strings or keys. The Supabase/Vercel secrets belong to Andrew.
- The platform never publishes anything itself. Do not invent facts, numbers or approvals. Mark nothing "approved" unless Andrew said so in his own words.
- Query strings do not reach the handler on Vercel (path only): design list endpoints accordingly (filter client-side or use path segments).
- Existing Outreach Desk pages must keep working.

## Acceptance for P1 (from the plan)
Create, edit and reschedule on the tablet; calendar uses `America/Jamaica`; status values limited to the enum; audit on delete. Plus: 401/400/404/409 coverage, Playwright at both viewports, no console errors, no horizontal scroll, controls >= 48px.

## Open approvals to remind Andrew about (do not assume)
P0 acceptance; G0, D1, D7, D8-D14 (suggested wording: "Approved: P0 accepted. G0, D1, D7 and D8-D14 approved."); G1 before any migration on the live database; G3 before deploying P1.

Begin with slice 2.
