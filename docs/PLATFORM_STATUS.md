# Platform Status

Last updated: 2026-11-09

**Current phase: CP1 (P1 complete + P2a) is BUILT and TESTED, about 20% of the whole project. STOPPED, waiting for Andrew to say "continue" (CP2 next). P0 acceptance is still not recorded.**
(The kickoff brief groups work into 7 phases; this plan uses P0-P10. Brief "Phase 1 Foundation" = plan P0.)

## Approval record
- G0 (begin build): the kickoff brief called the architecture "approved" and instructed the build, but the exact G0 wording in the handoff was not given
  and Q1-Q6 are unanswered. **P0 was built on that basis, on a throwaway local database only. Andrew: please confirm G0, D1 and D7 explicitly.**
- G1 (migration on a real database): NOT requested, NOT done. G2 (imports): none done. G3 (deploy): none done. G4 (publish): n/a.

## P0 results (actual)
| Check | Result |
|---|---|
| Existing suite before changes (baseline) | PASSED 44/44 |
| Full suite after P0 + QA status (44 existing + 111 new) | PASSED 155/155 (re-run 2026-11-08 after adding migration 003) |
| Migration `002_content.sql` applies, re-runs twice with no change, runner skips it once recorded | PASSED |
| Migration leaves every existing table, column, trigger unchanged (001-only vs 001+002 snapshot) | PASSED |
| Migration run by a NON-superuser role (as a real Neon role would) | PASSED |
| RLS enabled + forced on all 19 content tables; only policy is `content_app` | PASSED |
| Default-deny: owner role without `SET ROLE` sees 0 rows and cannot insert; an unrelated role with SELECT grants sees 0 rows | PASSED |
| `content_app` cannot read `owner_credentials`, `sessions`, `auth_attempts`, leads email/phone, cannot create objects/roles; can only append to `audit_events` | PASSED |
| Claim gate, script lock, evidence rule, downgrade cascade, episode gate, append-only metrics, 60:00 course rule, path/enum/date CHECKs | PASSED (run twice: as connecting role and as `content_app`) |
| Mutation checks (removed FORCE RLS / gate condition / metrics trigger / 3600 constant, each made tests fail; file restored byte-identical) | PASSED (all 4 caught) |
| Python enums == database CHECK constraints (drift guard) | PASSED |
| Every `/api/content/*` route: 401 without/with bad/with revoked session (unit + live server via curl) | PASSED |
| API request really runs as `content_app` (non-superuser DB sees 4 seed rows only through the role) | PASSED |
| Real server, real owner setup over HTTP, real password + TOTP sign-in in Chromium | PASSED |
| Tablet browser run, 1280x800 and 800x1280: nav layout, 5 tabs fit, no horizontal scroll, touch targets >= 48px (nav + Refresh), tap works, dark theme, live counts correct, hide-list term never rendered, sign-out revokes token | PASSED 31/31, 0 console errors, 0 5xx |
| Existing pages (Today/Pipeline/Playbooks/Insights) still load in the browser | PASSED (load only) |
| `production/tools/qa.py project` secret scan | PASSED |

## CP1 results (2026-11-09, throwaway local Postgres 16 only)
| Check | Result |
|---|---|
| Full suite (174 before CP1 + 45 new) | PASSED 219/219 |
| New: ideas + promote + calendar (`test_content_p1_ideas_calendar.py`) | PASSED 20 |
| New: scripts + lines (`test_content_p2a_scripts.py`) | PASSED 24 |
| New: real HTTP handler answers PATCH and DELETE (`test_http_methods.py`) | PASSED 1 |
| Every new route: 401 without/with bad session; 400 invalid input; 404 unknown id; 409 rule/dependency; safe messages; audit on every write, none on a failed write | PASSED (unit, through the real handler + owner auth) |
| Mutation checks on new rules (18 deliberate breaks: promote rule, Jamaica date, Monday weeks, overdue, strict dates, idea release on episode delete, script step order, LOCKED final, FACT default, line insert/delete/move, claim-link copy, archived-episode rule, PATCH/DELETE handlers, no-innerHTML) | PASSED, 18/18 made a test fail; each file restored byte-identical (sha256 checked) |
| Browser, real login, 1280x800 and 800x1280 (`tests/e2e/content_cp1.js`): create idea, promote, see it on the calendar, reschedule, week view and Next/Previous/Today, script editor (add, retag, reorder), FACT line refused with a clear message, retag then READY_TO_RECORD, episode then READY_TO_RECORD, every content page: no horizontal scroll, controls >= 48px, dark theme, existing pages load | PASSED 21/21, 0 console errors, 0 5xx |
| Migrations | NONE added in CP1 (G1 not triggered). No existing table changed (G2). |

**Bug found by the browser run and fixed:** neither the local server nor the Vercel handler (`api/index.py`) answered PATCH or DELETE (HTTP 501), so the episode edit/delete routes from the earlier slice could not have worked outside unit tests. Both now route them; `test_http_methods.py` fails without the fix (verified).

### Built in CP1
`core/content/{common,ideas,schedule,scripts}.py`; `episodes.py` (strict date, deleting an episode returns its idea to BACKLOG); table-driven `dashboard/content_api.py`;
UI `content.js` (tabs, helpers, Foundation), `content_board.js` (calendar, episodes, ideas), `content_script.js` (script editor); CSS; service-worker cache `od-shell-v3`.
New routes: `GET/POST /ideas`, `GET/PATCH/DELETE /ideas/{id}`, `POST /ideas/{id}/status|promote`, `GET /calendar/today|month/YYYY-MM|week/YYYY-MM-DD`,
`GET/POST /episodes/{id}/scripts`, `GET/PATCH/DELETE /scripts/{id}`, `POST /scripts/{id}/status|lines`, `PATCH/DELETE /lines/{id}`, `POST /lines/{id}/move`.

### CP1 NOT tested / not built
- NOT BUILT (CP2): claims, sources, linking claims to lines, the claim checker screen, banned-phrase check. Until then **any FACT line blocks a script from READY_TO_RECORD** (the database gate; the UI says so). Only non-factual lines can pass.
- NOT TESTED: Neon/Supabase/Vercel, real Galaxy Tab S9 FE+, Samsung Internet, Firefox, Safari (Chromium touch emulation only); the installed-PWA cache update to `od-shell-v3`; offline.
- NOT RUN: `tests/e2e/content_p0.js` after its edits for the new tab layout (it expects seed data that the throwaway database no longer has); `tests/e2e/journey.js`. `content_cp1.js` covers the Foundation tab and existing page loads instead.
- NOT MEASURED: tap targets inside the day dialog were measured for the add form and reschedule only; very long titles/notes were not stress-tested visually.
- Local-runner and Vercel-handler parity: PATCH/DELETE are covered by a socket test of the Vercel handler class and by the browser run on the local runner; the live Vercel deployment itself was not exercised (G3).
- Calendar "today" uses the server clock converted to America/Jamaica. Unit tests fake the clock; the real clock was only seen in the browser run.

## Built in P0
Migrations `002_content.sql` and `003_episode_qa_status.sql` (adds episode status `QA`) (19 tables, constraints, triggers, RLS, `content_app` role, seed: 4 series + 1 course plan row); `core/content/` (access, meta, status);
`dashboard/content_api.py` (`GET /api/content/meta`, `GET /api/content/health`); Content page and nav entry; 48px touch targets for nav.
**No editing screens exist.** The Content page is a read-only foundation/status view and says so on screen.

## NOT tested (do not assume these work)
- NOT TESTED: Neon, Vercel, or any production database. Migration privilege requirements on Neon are unverified (see handoff, G1).
- NOT TESTED: PostgreSQL other than 16.15. On PG < 16 the connecting role inherits `content_app`, so FORCE RLS does not deny that one role (other roles still denied).
- NOT TESTED: real Galaxy Tab S9 FE+ hardware, Samsung Internet, Firefox, Safari. Chromium with touch emulation only.
- NOT RUN: existing `tests/e2e/journey.js` (sales browser journey). Only the unit suite and a page-load check cover the old pages.
- NOT TESTED: service-worker update path (cache bumped to `od-shell-v2`; behaviour on an already-installed PWA not observed), offline mode.
- NOT TESTED: concurrent cold-start migration with 002 under the advisory lock (the mechanism is unchanged and 001 uses it).
- NOT BUILT: everything in P1-P10, including all editing screens, the app-layer claim checker, banned-phrase / hide-list checks, imports.

## Known issues / limitations
1. Docs mismatch: `TECHNICAL_ARCHITECTURE.md` mentions `007_sales_os.sql`; the repo has only `001_schema.sql`.
2. `founder-story-dossier/` still not found anywhere (blocks P10 dossier import only). Brief says 84 Agriloop briefs, repo has 85 (unconfirmed). `anjuneedham/agriloop` not inspected.
3. RESOLVED (Q9): all Outreach Desk controls raised to 48px. Measured in Chromium on Today/Pipeline/Playbooks/Insights/Content at 1280x800 and 800x1280: no undersized controls, no horizontal scroll. Only default/empty states were measured; screens opened from drawers or with data-heavy rows were NOT measured.
4. App is still branded "Outreach Desk"; renaming was out of P0 scope.
5. A LOCKED script that cites a claim later downgraded is not auto-changed (it is history). The P2 checker must flag it.
6. Deferrable uniqueness (script line positions, course module positions) is checked at COMMIT, so a duplicate surfaces when the request's transaction ends. P1/P2 API code must map that error.
7. Auto claim codes (`C-001...`) come from a sequence; P10 import of claims with their own codes must advance the sequence to avoid collisions.
8. Content-Platform repo is still empty and unused (D7).

## Next action
Andrew says "continue" to start CP2 (P2b claims/sources/checker/banned phrases + P3a shots). Still open: P0 acceptance and G0/D1/D7/D8-D14 (wording in the handoff); G1 before any live migration; G3 before deploying anything.
