# Metrics Review Playbook

Real numbers only, copied manually from platform analytics (D6: metrics are manual and append-only). Views are not customers.

## What to record
### Platform metrics (per post, at 48 h, 7 d, 28 d)
| Metric | YouTube | Instagram | TikTok | Platform field |
|---|---|---|---|---|
| Views | yes | yes | yes | `metrics.views` |
| Impressions | yes | reach/impressions | n/a | **gap** |
| Click-through rate | yes | n/a | n/a | **gap** |
| Average view duration | yes | yes (avg watch time) | yes | derive from `watch_time_s` / views; **gap** for direct value |
| Retention (at 30 s / %) | yes | partial | yes | **gap** |
| Engagement (likes, comments) | yes | yes | yes | `likes`, `comments` |
| Shares | yes | yes | yes | `shares` |
| Saves | n/a | yes | yes | `saves` |
| Subscribers / followers gained | yes | yes | yes | `followers_gained`; totals in `growth_log` |
| Profile visits | n/a | yes | yes | **gap** |
| Link clicks | cards/description (if available) | yes | yes | **gap** |

Gaps: until a migration adds them (needs approval), record gap metrics in the weekly review notes table below.

### Business outcomes (separate table, never mixed with the above)
| Outcome | Definition | Where |
|---|---|---|
| Inquiries | a person contacts Andrew and mentions/arrives via content | `leads` + `content_lead_links` (cta_code) |
| Leads attributed to content | inquiry with a cta_code or stated source | `content_lead_links` |
| Qualified conversations / proposals / closed | existing Outreach Desk pipeline stages | `leads.stage` |
| Product sign-ups (Agriloop, later TradeNotes) | only from that product's own records | product DB, CONFIRMED claim |
Attribution rule: only a cta_code, a tracked link, or the person saying so counts. "Views went up and so did leads" is not attribution.

## Weekly review (Monday, 30 min)
1. Record numbers for posts at 7 d (and 48 h for last week's posts).  2. Update `growth_log` (Monday date).
3. Table: post | pillar | moment type | views | AVD | retention@30s | shares | saves | followers | link clicks | inquiries.
4. Write: what the numbers show (fact) vs what I guess (hypothesis), separately.
5. Pick ONE change to test next week (hook style, length, pillar, posting time). Log it as a HYPOTHESIS.

## Monthly review (first Monday, 60 min)
1. 28-day numbers per post; best and worst 3 by retention and by shares (not just views).
2. Pillar comparison; which moment types produced shorts that passed the standalone tests and performed.
3. Business table: inquiries, attributed leads, conversations, proposals. State plainly if zero.
4. Did last month's tested changes work? Keep/drop.
5. Decide next month's focus (Andrew approves). No targets invented; targets are set by Andrew from real baselines after the first full month.
