# Handover: Zero-to-Revenue → Andrew Builds

Date: 7 Nov 2026. The Zero-to-Revenue OS (Scout/Operator/Treasury agents, PayPal and wallet verification, crypto-era bounty scoring, football-themed dashboard) is retired as the platform. This repo is the new home. The old repo is untouched and can stay as an archive.

## Carried over (and changed)
| Piece | Change |
|---|---|
| Sales system: prospects, stages, tasks, playbooks, activity log, insights (`app/core/sales`) | Moved as is. Table `leads` kept as the prospect table |
| Owner auth (password + TOTP, hashed sessions, lockout, recovery codes) | Moved as is; authenticator issuer renamed "Outreach Desk" |
| Front end: Today, Pipeline, Prospect, Playbooks, Insights | Moved; OS pages, football theme, splash ball and agent status chip removed; storage keys renamed `od_*` |
| Schema | One slim `001_schema.sql` (settings, auth, audit, prospects, activity, tasks, playbooks). No agents, payments, wallets or legacy lead statuses |
| Tests | 25 sales tests + 15 login tests + browser journey |
| Video production system | Moved to `production/` unchanged apart from paths |

## Left behind on purpose
Scout, Operator, Treasury, scheduler/cron, MCP connector, notifications, Gmail/PayPal/EVM integrations, the Game plan page, the OS spec and docs. If any is wanted later it should come back as a small, separate module, not as the platform.

## Things that changed in behaviour
- Prospects no longer carry the old CSV/Gmail `status` column. Importing earlier outreach is a to-do (the app supports back-dated `occurred_at` on every record).
- There is no verified-revenue concept here. Revenue entered on a won prospect is owner-recorded only.

## Open items
1. Deploy (Vercel + Neon, steps in the root README) once you approve.
2. Re-capture the demo footage and thumbnails on the new look (they were captured on the old theme).
3. Back-fill real outreach.
4. Rotate any credentials pasted into chat during the OS era.
