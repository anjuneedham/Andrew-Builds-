# Platform Build Plan

Status: **NOT STARTED. Awaiting approval to begin PLATFORM-BUILD.** See `PLATFORM_ARCHITECTURE.md` for the model.

## Testing standard (every phase)
- Unit tests in `app/tests/unit/test_content_*.py` against a **throwaway** Postgres (`TEST_DATABASE_URL`), through the real HTTP handler + auth.
- Every route: 401 without session; 400 on invalid input; 404 unknown id.
- Playwright check at tablet viewport (1280×800 and 800×1280) for each new page.
- Existing suite (`test_owner_login`, `test_sales`, `test_static`) still passes.
- No phase is "done" until Andrew has seen it running locally or on a preview he approved.

## Approval gates (apply to all phases)
- **G0** Before any code: Andrew approves this plan (exact wording in HANDOFF).
- **G1** Before running any migration against a non-throwaway database.
- **G2** Before any import of existing files/data, and before any delete or schema change to existing tables (none planned).
- **G3** Before any deployment (preview or production) or env-var change on Vercel/Neon.
- **G4** Before anything is published, sent, or shared externally. The app never does this itself.

## Phases

### P0 Foundation (depends on G0)
Scope: `002_content.sql` (all tables, CHECKs, triggers, RLS, `content_app` role), `core/content/` skeleton, `content_api.py` dispatcher, nav entry.
Acceptance: migration applies twice idempotently on a throwaway DB; RLS denies a role other than `content_app`; all new routes 401 without auth; existing tests pass.

### P1 Content calendar + idea backlog
Scope: series, episodes, ideas; month/week calendar; promote idea → episode.
Acceptance: create/edit/reschedule on tablet; calendar uses `America/Jamaica`; status values limited to the enum; audit on delete.

### P2 Script editor + claims + claim checker
Scope: scripts, script_lines, claims, sources, line_claims, claim_sources; checker; banned-phrase check.
Acceptance: a FACT line with no claim blocks `READY_TO_RECORD`; a FACT line linked to a `PLANNED`, `UNKNOWN` or `PARTIALLY_CONFIRMED` claim blocks it;
OPINION/QUESTION/HYPOTHESIS lines do not need claims; banned phrases block; DB trigger blocks the transition even if the API is bypassed; checker output lists each failing line.

### P3 Shot lists + recording checklists
Scope: shots per episode; recording checklist adapted from `production/` tablet checklist and `SHOT_LIST_TEMPLATE.md`.
Acceptance: full-screen recording mode usable at arm's length; each shot ticks to CAPTURED; checklist includes "no passwords/keys/bank details on screen".

### P4 Asset register
Scope: assets with path, kind, hide-list check result, consent reference.
Acceptance: import of `production/episode-00{1,2}/*ASSET_REGISTER.md` (after G2) matches file counts; hide-list check runs on text assets (captions, scripts) and records result; images/video require a manual "checked" tick with timestamp.

### P5 Publishing log + manual metrics
Scope: posts, metrics (append-only), publish gate.
Acceptance: post cannot be APPROVED without passing hide-list, banned-phrase, consent and TradeNotes-disclaimer checks; metrics cannot be edited, only re-recorded; no platform API calls.

### P6 Moments library
Scope: moments with source links; "make claim" and "make idea" from a moment.
Acceptance: moment requires a source; a claim created from a moment defaults to `UNKNOWN` until Andrew sets it.

### P7 Growth log
Scope: weekly follower counts and notes per platform.
Acceptance: manual entry only; counts shown as numbers, no percentages below n=30 (existing Insights rule).

### P8 Lead/CTA tracker
Scope: `content_lead_links` to existing `leads`; CTA codes per post.
Acceptance: link a lead to a post from either side; no change to `leads` schema; personal data not copied into content tables.

### P9 Course module planner
Scope: course_modules for "From Sales to SaaS".
Acceptance: plan cannot be marked READY unless total is exactly 60:00; live remaining-time counter; each module links to an episode with its own claim gate.

### P10 Import + deploy (depends on G1, G2, G3)
Scope: one-off import of `production/` episodes and (once located) `founder-story-dossier/` claims register, timeline, shot list S01–S46, course blueprint; preview deploy.
Acceptance: import is idempotent and dry-run first; imported claims keep their original status, never upgraded; Andrew approves preview before production.

## Dependencies
- Neon (or existing Postgres) access for a throwaway test DB: Andrew.
- `founder-story-dossier/` location: blocks P10 dossier import only.
- Hide-list terms (real names, partner names): Andrew enters them himself in the app; never committed to git.

## Out of scope
Paid ads tools; automated publishing or platform APIs; AI-generated faces/voices; scraping; multi-user permissions; analytics integrations;
live sync with Agriloop's database; running FFmpeg from the app; offline editing.
