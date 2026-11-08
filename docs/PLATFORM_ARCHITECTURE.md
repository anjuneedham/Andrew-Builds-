# Platform Architecture: Andrew Builds Content Operating Platform

Status: **PLAN, not approved.** Nothing here is built. Last updated 2026-11-08.

## 1. Stack decision

**Extend the existing Python/PostgreSQL Outreach Desk in `Andrew-Builds-/app`.** Do not start a new Vercel + Supabase app.

Evidence from the repo:

| Need | Already in `app/` | File |
|---|---|---|
| One owner, password + 2FA | scrypt password + TOTP, hashed bearer sessions, rate limiting, one-time setup token | `app/core/auth/owner_login.py` |
| Audit of sensitive actions | `audit_events`, append-only by trigger | `app/core/audit.py`, `app/database/migrations/001_schema.sql` |
| Append-only business log | `activity_events`, append-only by trigger | `001_schema.sql`, `app/core/sales/events.py` |
| Leads | `leads` table + pipeline | `app/core/sales/pipeline.py` |
| Tablet UI | Vanilla-JS PWA, no build step, strict CSP, manifest + service worker | `app/dashboard/static/` |
| Deployment | Vercel Python function + Neon Postgres, already documented | `app/vercel.json`, `README.md` |
| Dependencies | One: `psycopg[binary]` | `app/requirements.txt` |

A new Vercel + Supabase app would duplicate auth, audit, leads and deployment, and would add a second login. Supabase Auth's
MFA is workable but the owner-only login here already exists and is tested (`app/tests/unit/test_owner_login.py`).
The Agriloop Supabase project must not host this: it is Agriloop's production data with partner/multi-user roles.

## 2. Component structure

```
app/
  core/auth/            REUSE as-is (owner login, sessions)
  core/audit.py         REUSE (audit sensitive content actions)
  core/sales/           REUSE (leads, activity log). Lead/CTA tracker links to leads.id
  core/content/         NEW  calendar.py, scripts.py, claims.py, shots.py, assets.py,
                             posts.py, moments.py, growth.py, course.py, checks.py (claim checker, hide-list, banned phrases)
  dashboard/content_api.py   NEW  /api/content/* dispatcher (auth done by dashboard.app, same as sales_api.py)
  dashboard/static/js/content/*.js   NEW pages, same createElement/textContent pattern
  database/migrations/002_content.sql   NEW, additive only
production/             REUSE: file-based pipeline (FFmpeg assembly, QA gates, thumbnails, short extraction).
                        The app records metadata and file paths; it does not run FFmpeg.
```

## 3. Integration strategy

| Source | Action |
|---|---|
| Outreach Desk auth, audit, sessions | **Reuse unchanged.** |
| `leads`, `activity_events` | **Reuse.** CTA tracker adds `content_lead_links`; no change to existing tables. |
| `production/episode-00N/*` (scripts, shot lists, asset registers, checklists) | **Import read-only** (one-off, owner-approved script) into episodes/scripts/shots/assets. Files stay the source for the FFmpeg pipeline. |
| `production/templates/*` (shot list, short extraction, performance tracking) | **Adapt** into form fields and checklist rows. |
| `production/tools/qa.py` secret scan | **Reuse** pattern for the hide-list check. |
| Agriloop `/ops` studio (`src/app/ops/*`), `ProductionVideo`, `VideoScriptRevision`, `PublishRecord`, `PlatformMetric` | **Leave in place.** Agriloop-brand content stays in Agriloop. Optional later: owner-triggered CSV export → import. No live connection between databases. |
| Agriloop `video-production/briefs/AGR-*.json` (85 files found; brief says 84) | **Reference only.** Count to be confirmed by Andrew. |
| Agriloop content calendar (`src/lib/ops/calendar.ts`) | **Pattern reference** (Jamaica-timezone days). |
| `founder-story-dossier/` | **NOT FOUND** in any attached repo or code search. Import blocked until located (see DECISIONS Q1). |
| `Content-Platform` repo | Empty. Recommended: do not use for code; keep docs here. |

## 4. Data model (migration `002_content.sql`, additive)

All ids `BIGSERIAL`; all tables have `created_at`, `updated_at`. Status fields are `CHECK`-constrained text.

| Entity | Key fields | Relations |
|---|---|---|
| **series** | slug (`course`, `bootstrapper-experiment`, `andrew-builds`, `shorts`), title | 1→N episodes |
| **episodes** | series_id, code (e.g. `E001`, `M03`), title, status (`IDEA`,`SCRIPTING`,`READY_TO_RECORD`,`RECORDED`,`EDITING`,`READY_TO_PUBLISH`,`PUBLISHED`,`ARCHIVED`), planned_date, target_duration_s, production_path | N→1 series; 1→N scripts, shots, assets, posts |
| **ideas** | title, notes, series_id null, moment_id null, status (`BACKLOG`,`SCHEDULED`,`DROPPED`) | promoted to episode |
| **scripts** | episode_id, version, status (`DRAFT`,`IN_REVIEW`,`READY_TO_RECORD`,`LOCKED`), body | 1→N script_lines; versions immutable once `LOCKED` |
| **script_lines** | script_id, position, text, kind (`FACT`,`OPINION`,`QUESTION`,`HYPOTHESIS`,`DIRECTION`,`CTA`,`DISCLAIMER`) | N→M claims via `line_claims` |
| **claims** | code (`C-001`), statement, status (`CONFIRMED`,`PARTIALLY_CONFIRMED`,`PLANNED`,`UNKNOWN`), project (`agriloop`,`tradenotes`,`yardscale`,`andrew-builds`), verified_at, notes | N→M sources via `claim_sources` |
| **sources** | kind (`commit`,`deployment`,`document`,`screenshot`,`founder_answer`,`url`,`record`), reference, captured_at, private bool | evidence for claims |
| **shots** | episode_id, code (`S01`), description, location, device, status (`PLANNED`,`CAPTURED`,`REJECTED`), checklist JSON | N→1 episode |
| **assets** | episode_id null, kind (`raw`,`voiceover`,`screen`,`graphic`,`thumbnail`,`caption`,`export`), path, hide_list_checked_at, hide_list_result, consent_ref null | N→1 episode |
| **posts** | episode_id, asset_id, platform (`youtube`,`instagram`,`tiktok`), url, status (`DRAFT`,`APPROVED`,`PUBLISHED`), approved_at, published_at | 1→N metrics |
| **metrics** | post_id, captured_at, views, likes, comments, shares, saves, watch_time_s, followers_gained, source=`manual` | append-only (trigger) |
| **moments** | occurred_at, kind (`commit`,`deployment`,`failure`,`decision`,`milestone`), project, summary, source_id | can create claims and ideas |
| **growth_log** | week_start, platform, followers, notes | manual |
| **content_lead_links** | post_id, lead_id (existing `leads.id`), cta_code, first_touch_at | joins content to inquiries |
| **course_modules** | position, title, duration_s, episode_id null | enforced total = 3600 s |
| **hide_list** | term, category (`person`,`partner`,`secret`,`financial`,`other`), active | used by checks; never shown in exports |

### Enforced rules (DB + app)
- **Claim gate:** a script may move to `READY_TO_RECORD` only if every `FACT` line links ≥1 claim and every linked claim is `CONFIRMED`.
  `PARTIALLY_CONFIRMED`/`PLANNED`/`UNKNOWN` block. Checked in `core/content/checks.py` and by a DB trigger on `scripts.status`.
- **Course total:** `READY` course plan requires `SUM(duration_s) = 3600`; UI shows remaining seconds live.
- **Publish gate:** a post may move to `APPROVED` only with: hide-list check passed on its asset, banned-phrase check passed, TradeNotes
  content carries the risk + "not financial advice" disclaimer line, consent reference on any asset tagged as showing a person.
  `PUBLISHED` is set manually by Andrew after he posts; the app never posts.
- **Banned phrases:** "unlock your potential", "next level", "revolutionize", "passionate about" fail the script and post checks.

## 5. Security model
- **Auth:** reuse owner login (scrypt + TOTP, 24 h sessions, rate limit, setup closes after first use). No second account.
- **Authorization:** every `/api/content/*` route behind the existing owner check; 401 otherwise. No public routes besides login and static shell.
- **Row-level security:** enable RLS on all new tables with default-deny; app connects as a dedicated non-owner role `content_app`
  that has a single permissive policy (`USING (true)` for that role only). Any other role (including a leaked read-only role) sees nothing.
  This is defense-in-depth: there is one owner, so per-row ownership columns add nothing.
- **Secrets:** `DATABASE_URL`, `OWNER_SETUP_TOKEN` in Vercel env only; `.env.local` git-ignored; `qa.py` secret scan runs before commit.
- **Audit:** claim status change, script → `READY_TO_RECORD`, post → `APPROVED`/`PUBLISHED`, hide-list edits, imports, deletes.
- **Data hygiene:** `sources.private` items and the hide-list are excluded from any export; no partner terms stored in content tables.

## 6. Tablet-first UX (Galaxy Tab S9 FE+, Chrome, landscape and portrait)
- Touch targets ≥ 48 px; no hover-only controls; works one-handed in portrait.
- Two-pane layout in landscape (list + detail); single column in portrait.
- Script editor: one line per row, kind selector and claim chip per line, red/green gate banner at top.
- Recording mode: full-screen shot checklist, large tick buttons, screen kept simple for use beside a camera.
- Installable PWA (existing manifest); offline shows shell only (existing behaviour, not extended in MVP).
- No build step; same CSS and fonts as Outreach Desk.
