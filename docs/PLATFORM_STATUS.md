# Platform Status

Last updated: 2026-11-08

**Current phase: P0 Foundation is BUILT and TESTED. STOPPED at the P0 approval gate. P1 has NOT started.**
(The kickoff brief groups work into 7 phases; this plan uses P0-P10. Brief "Phase 1 Foundation" = plan P0.)

## Approval record
- G0 (begin build): the kickoff brief called the architecture "approved" and instructed the build, but the exact G0 wording in the handoff was not given
  and Q1-Q6 are unanswered. **P0 was built on that basis, on a throwaway local database only. Andrew: please confirm G0, D1 and D7 explicitly.**
- G1 (migration on a real database): NOT requested, NOT done. G2 (imports): none done. G3 (deploy): none done. G4 (publish): n/a.

## P0 results (actual)
| Check | Result |
|---|---|
| Existing suite before changes (baseline) | PASSED 44/44 |
| Full suite after P0 (44 existing + 109 new) | PASSED 153/153 |
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

## Built in P0
Migration `002_content.sql` (19 tables, constraints, triggers, RLS, `content_app` role, seed: 4 series + 1 course plan row); `core/content/` (access, meta, status);
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
3. Existing Outreach Desk buttons are 40px (small 32px), below the 48px tablet target. Only the new Content controls and the nav were raised. Restyling everything is a decision for Andrew (Q9).
4. App is still branded "Outreach Desk"; renaming was out of P0 scope.
5. A LOCKED script that cites a claim later downgraded is not auto-changed (it is history). The P2 checker must flag it.
6. Deferrable uniqueness (script line positions, course module positions) is checked at COMMIT, so a duplicate surfaces when the request's transaction ends. P1/P2 API code must map that error.
7. Auto claim codes (`C-001...`) come from a sequence; P10 import of claims with their own codes must advance the sequence to avoid collisions.
8. Content-Platform repo is still empty and unused (D7).

## Next action
Andrew reviews P0 and replies with explicit approval (see handoff for wording). Then P1 (calendar, idea backlog, episodes).
