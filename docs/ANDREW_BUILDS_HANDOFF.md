# Andrew Builds Handoff (shared source of truth)

Last updated: 2026-11-08. **Approval status: NOTHING APPROVED. PLATFORM-BUILD has not started.**

## Repositories
| Repo | Role | Branch used |
|---|---|---|
| `anjuneedham/Andrew-Builds-` | Outreach Desk app + production system + platform docs (home of the platform) | `ccr-35fb16ad-8f40zk` |
| `anjuneedham/agriloopmain` | Agriloop app incl. `/ops` content studio. Read-only for this project | not modified |
| `anjuneedham/Content-Platform` | Empty, no commits. Recommended: unused | not modified |
| `anjuneedham/agriloop` | Second Agriloop repo, not inspected | — |

## Assets inspected (key paths)
- Auth: `app/core/auth/owner_login.py`; audit: `app/core/audit.py`; schema: `app/database/migrations/001_schema.sql`
- Sales/leads: `app/core/sales/*`, `app/dashboard/sales_api.py`; UI: `app/dashboard/static/`
- Production: `production/episode-001/`, `production/episode-002/`, `production/templates/`, `production/tools/{produce,qa,new_episode}.py`
- Agriloop ops: `agriloopmain/src/app/ops/*`, `src/components/ops/*`, `src/lib/ops/calendar.ts`, migrations `20261104200000_video_production_portal.sql`, `20261105120000_unified_ops.sql`, briefs `video-production/briefs/AGR-*.json` (85)
- `founder-story-dossier/`: **not found**

## Architecture (recommended, pending)
Extend Python/Postgres Outreach Desk with a `core/content/` module, `/api/content/*`, and additive migration `002_content.sql`. Details: `docs/PLATFORM_ARCHITECTURE.md`.

## Data model
series, episodes, ideas, scripts, script_lines, claims, sources, line_claims, claim_sources, shots, assets, posts, metrics (append-only),
moments, growth_log, content_lead_links (→ existing `leads`), course_modules (total = 3600 s), hide_list.

## Security decisions (pending)
Reuse owner login (scrypt + TOTP); all content routes owner-only; RLS default-deny with `content_app` role; secrets in Vercel env only; audit on claim/status/publish/import/delete.

## Editorial rules enforced by the app
Claim gate (only CONFIRMED claims support FACT lines); banned phrases blocked; hide-list check before APPROVED; consent reference for people;
TradeNotes disclaimer required; app never publishes. Agriloop never framed as a success; TradeNotes not live; no paid-ads expertise.

## Build phases
P0 foundation → P1 calendar/ideas → P2 scripts/claims → P3 shots/checklists → P4 assets → P5 publishing/metrics → P6 moments → P7 growth → P8 lead/CTA → P9 course planner → P10 import + deploy. Acceptance criteria: `docs/PLATFORM_BUILD_PLAN.md`.

## Gates
G0 plan · G1 migration on real DB · G2 imports/destructive changes · G3 deploy · G4 publish/send.

## Outstanding questions
Q1–Q6 in `docs/PLATFORM_DECISIONS.md` (dossier location, deployment state, repo choice, Agriloop content scope, TradeNotes disclaimer, second Agriloop repo).

## Exact next action
1. Andrew replies: **"Approved: begin PLATFORM-BUILD Phase P0 in Andrew-Builds- using a throwaway test database. D1 and D7 approved."** (edit as needed)
2. Next session: read this file, then build P0 only, run tests, update `PLATFORM_STATUS.md`, stop at end of P0 for review.
