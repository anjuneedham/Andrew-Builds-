# Andrew Builds Handoff (shared source of truth)

Last updated: 2026-11-08. **Implementation phase: P0 Foundation BUILT + TESTED, stopped at its approval gate. P1 not started.**
Approval status: G0 assumed from the kickoff brief (verbatim wording not given; please confirm). No G1/G2/G3/G4 approvals requested or used.

## CONTENT BUILD (Sonnet): current package (updated 2026-11-09)
**Stage: GATE 2 (G-SCRIPT). Script v1 + claim register DRAFTED. Awaiting Andrew. Nothing recorded, edited, published or imported.**

| Field | State |
|---|---|
| Current content package | **E003** "My first TradeNotes test found a bug. My first deploy failed four times." Arc B, P2 primary / P4 secondary |
| Package location | `production/episode-003/` (scaffolded with `new_episode.py`); package files in `production/episode-003/package/`: `content-brief.md`, `script.md`, `claims-register.md` (others created at Gates 3-5) |
| Script status | v1 DRAFT (45 lines, about 580 spoken words, roughly 4 min of narration; live test run and fix attempt add screen time, so expect 7-9 min, 3 `[RECORD]` slots + ending written after recording) |
| Claim-check status | Manual check done: FACT lines cite CONFIRMED only, except L036 (outcome of the fix, UNKNOWN by design, added at G-RECORD). New claims C-037..C-051 and P-12 added to `docs/CLAIMS_REGISTER.md`. C-046 (affiliates) and C-051 UNKNOWN |
| Founder approvals | G-IDEA **approved 2026-11-09** ("Approved G-IDEA E003"). Disclaimer wording approved. CS-0 followed provisionally with his OK. G-SCRIPT pending |
| Recording / Editing / QA / Publishing | Not started |
| Short-form candidates | isolation test found the leak; "Vulnerable version of Next.js detected": reading the log; passing locally is not shipped |
| Decisions 2026-11-09 | Fix on camera approved; builds and records on the tablet; voiceover-only; recommends Supabase, Neon for testing; wants affiliate content |
| Affiliates | Constraint P-12: no affiliate/partnership wording until each programme is CONFIRMED (C-046); disclosure before first mention + in description; no earnings figures; broker mention only with disclaimer and no profitability implication |
| Course | Separate packages, one at a time. E003 reuses S23/S25/S28 for M5/M6. Next package after E003 is Andrew's choice |
| Supabase rollback | **NOT done.** The destructive SQL needed an unanswered confirmation. `tradenotes` schema (10 empty tables, 5 functions) + migration row `20261108173630` still believed present. Awaiting "retry" and the database decision |

### Known gaps
`[RECORD]` L009 (why TradeNotes), L013 (what he decided/checked 8 Nov), L036-L037 (ending, after attempt). C-046 which affiliate programmes are real. Database choice. Q-D1 split of work. Hide-list findings from Gate 1 (plans.ts links, session URLs, Supabase dashboard, public SALES_PLAYBOOK copy P-10) still apply.

**Next approval required:** `Approved G-SCRIPT E003` (or edits). **Exact next action:** on approval, write `shot-list.md`, `on-screen-text.md`, `recording-checklist.md` (Gate 3) and STOP. The fix-on-camera attempt is recorded after Gate 3, and ending lines are added at G-RECORD.

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

# CONTENT PLAN (2026-11-08, v2 reconciled with the founder dossier) - STATUS: PROPOSED, NOT APPROVED

Documentation only. Nothing was recorded, edited, published, deployed, imported or written to any database. The platform was NOT configured with these templates: only P0 exists (read-only page, no editing screens, no import), so there was nothing to import into without approval (G1/G2).

## Source material (resolved: dossier found)
Andrew supplied `ANDREW_BUILDS_CONTEXT_PACK.md` (236 KB: dossier files 00-13 plus key source docs). Path in the session that received it: `/root/.claude/uploads/.../502edbc7-ANDREW_BUILDS_CONTEXT_PACK.md`.
**It is deliberately NOT committed:** `Andrew-Builds-` is a PUBLIC repo and the pack holds traction numbers, partner/user-adjacent detail and strategy. Next session: ask Andrew to re-attach it, or to make this repo private / name a private repo for it (decision Q-N1).
A search of all 37 GitHub repos found no other copy. Dossier research date 8 Nov 2026; numbers must be re-verified on recording day.

## Confirmed platform capabilities (verified in code, P0)
- Schema: series, episodes (IDEA, SCRIPTING, READY_TO_RECORD, RECORDED, EDITING, QA, READY_TO_PUBLISH, PUBLISHED, ARCHIVED), ideas, scripts/lines/claims/sources, shots, assets, posts, metrics (append-only), growth_log, content_lead_links, course_plan/modules, hide_list. Seeded: 4 series, course_plan "From Sales to SaaS".
- DB-enforced: claim gate (FACT lines need CONFIRMED claims; Q7 strict), script freeze, claim-downgrade cascade, course READY only at 3600 s, post timestamps.
- NOT available: any create/edit UI or API (only `GET /api/content/meta|health`), calendar, app-level checks (banned phrases, hide list, disclaimers), imports. Metrics lack impressions, CTR, retention, profile visits, link clicks; asset kinds lack camera/document/short export.
- `production/tools/*` pipeline exists per its README; not re-run.

## Template and content locations
| Doc | Purpose |
|---|---|
| `docs/CONTENT_STRATEGY.md` | positioning, 5 pillars, documentary format, rules, workflow + gates, reuse map |
| `docs/COURSE_60_MINUTE_PLAN.md` | **v2**: dossier modules M0-M9, exactly 60:00, shot IDs, claim IDs, S01-S46 status (Appendix A) |
| `docs/CLAIMS_REGISTER.md` | **new**: 36 seed claims (C-001..C-036) + prohibited statements P-1..P-11 |
| `REPEATABLE_EPISODE_TEMPLATE.md`, `REPEATABLE_SCRIPT_TEMPLATE.md`, `SHOT_LIST_TEMPLATE.md`, `ASSET_REGISTER_TEMPLATE.md`, `PUBLISH_CHECKLIST.md`, `REPURPOSING_PLAYBOOK.md`, `METRICS_REVIEW_PLAYBOOK.md` | as before (shot/asset docs now carry the dossier hide list, tablet settings and `CRS_` naming) |

## Course (60:00)
M0 Cold open 1:30 · M1 Journey 5:30 · M2 Find a problem 6:00 · M3 Validate (what I skipped) 6:30 · M4 Scope the MVP 7:00 · M5 Build with Claude 10:00 · M6 Ship 7:00 · M7 Organic distribution 6:00 · M8 Agriloop debrief, decision, TradeNotes 7:00 · M9 Next steps 3:30 = 3600 s.
M1 opens on the pigs (C-008). M8 is a LIVE decision (30 Nov), never "I moved on". Dossier timecodes for shorts (e.g. "52 tables, 0 orders" M0; "the 0:02 problem" M7; "RLS test caught a leak" M5) feed the repurposing playbook once an edit exists.

## Evidence and claim rules
FACT lines cite only CONFIRMED claims in `CLAIMS_REGISTER.md`; PARTIAL/PLANNED/UNKNOWN only in REFLECTION/OPINION/HYPOTHESIS/QUESTION lines. Prohibited statements P-1..P-11 never appear. Founder-confirmed facts use source kind `founder_answer`. Banned phrases, trading disclaimer, consent, hide list, partner never mentioned, nothing published without Andrew.

## Production workflow and gates
IDEA >G-IDEA> evidence > plan > script >G-SCRIPT> shot list > recording >G-RECORD> edit >G-EDIT> QA >G-QA> >G-PUBLISH> Andrew publishes > metrics > review. Approval wording: "Approved G-<GATE> <code>". Detail: CONTENT_STRATEGY section 6.

## Repurposing and metrics
>= 3 standalone shorts per episode only where material passes 6 tests; metrics manual at 48 h / 7 d / 28 d; business outcomes kept separate. See playbooks.

## Answered by the dossier (no longer open)
Q1 dossier location. Q-C4 TradeNotes repo = `anjuneedham/TradeNotes`, first commit 8 Nov 2026 (C-021). Agriloop real numbers = C-011/C-012 (founder-copied; refresh). Q-C6 episodes 001/002 are Outreach Desk-focused (dossier Q-B2 still open on how they relate).

## Outstanding questions (founder), highest value first
- **Q-N1** This repo is public: make it private, or name a private repo for the context pack? (blocks storing the pack)
- **Q5 / dossier Q-H3** exact trading disclaimer wording.
- **Q-A2** Did you speak to any farmers/buyers before building Agriloop, how many, what did they say? (decides whether M3 is "what I skipped")
- **Q-A3 / Q-A4** specific sales story; first paying customer in your own business. (M1 cannot be scripted without them)
- **Q-A5** which Aug-Sep sites were paid client work (C-006).
- **Q-C2** may the partnership be mentioned at all? Currently NO (P-6). Q-C3/Q-C4 what happens to existing users and Agriloop's future.
- **Q-D1 / Q-D2** exact split of work between you and Claude Code; do you build on the tablet or only record?
- **Q-E1-E3** trading history and focus; has TradeNotes changed since 8 Nov (deploy fix, domain)?
- **Q-B1** brand architecture (YardScale / Andrew Builds / Agriloop / TradeNotes / course); Q-B2 how the Bootstrapper Experiment relates to the course.
- **Q-F1 / Q-F2** do you take MVP clients now; delivery model, price, timeline (none invented; `[DECIDE]` placeholders).
- **Q-H1 / Q-H2** which names, logos, client sites and dashboards may be shown.
- Course hosting (free YouTube or platform); first-user permission to tell her story (Q-C8); approve later schema additions (metrics gap columns, asset kinds).
- Housekeeping from dossier: upgrade TradeNotes' Next.js; rotate credentials pasted into chats earlier; confirm old Agriloop demo accounts/passwords are deleted; update stale docs before showing them.

## Current approval status
Content strategy, course plan v2, claims register and templates: **NOT APPROVED** (gate CS-0). Platform P0 approval and G0/D1/D7/D8-D14 still pending.

## Exact next step for CONTENT-BUILD (only after CS-0 approval)
1. Get Q-N1 answered; re-attach the context pack to the session.
2. Turn `CLAIMS_REGISTER.md` into the working register (re-verify C-010, C-011, C-021..C-025 against live state on the day; ask Andrew for the UNKNOWN items). Do not import to the DB (needs G1/G2).
3. Propose 3 episode ideas to Andrew for **G-IDEA** from real moments (Arc A: Agriloop to 30 Nov; Arc B: TradeNotes deploy fix; dossier hook candidates in file 07 section 6). No calendar dates.
4. For the approved idea: `python3 production/tools/new_episode.py <N> "<title>"`, fill the episode template, draft a tagged script, stop at **G-SCRIPT**. Record S45 (decision) only after Andrew decides.
Suggested reply: "Approved CS-0: content strategy, course plan v2, claims register and templates accepted." plus answers to the questions above.
