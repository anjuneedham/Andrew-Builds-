# Claims Register (seed, file-based until platform P2)

Seeded 2026-11-08 from the dossier production source pack (`10_production_source_pack.md` §5 and §2) and the founder answers (`11_founder_answers_update.md`). Statuses use the platform vocabulary. "CONFIRMED-BY-FOUNDER" in the dossier = `CONFIRMED` with source kind `founder_answer`.
Rules: only CONFIRMED claims may back a FACT line (Q7 strict). Wording is fixed: changing a statement voids its verification. Codes match the platform's `C-###` format; when imported, advance `claims_code_seq` past C-051.
**Repo is public: do not add partner names/terms, user names, keys or links here.**

| Code | Statement (exact wording allowed in FACT lines) | Project | Status | Source kind: reference | Limitations / re-check |
|---|---|---|---|---|---|
| C-001 | Andrew has worked in customer-service and corporate roles. | andrew-builds | CONFIRMED | founder_answer: 2026-11-08 answers | No specific stories yet (Q-A3) |
| C-002 | Andrew has traded for about seven years and has run other online businesses as a solopreneur with small teams. | andrew-builds | CONFIRMED | founder_answer: 2026-11-08 | Not expertise or results |
| C-003 | Andrew's trading results are not where he wants them to be. | tradenotes | CONFIRMED | founder_answer: 2026-11-08 | Never state numbers or performance |
| C-004 | Andrew runs YardScale Digital, a marketing and web agency. | yardscale | CONFIRMED | record: repos, Vercel team | - |
| C-005 | Between August and September 2026 Andrew built websites and tools for local, mostly Jamaican, businesses. | yardscale | CONFIRMED | record: repos | Do not say "clients" or "paid" (see C-006) |
| C-006 | Which of those sites were paid client work. | yardscale | UNKNOWN | - | Ask Q-A5 |
| C-007 | Agriloop development started on 13 September 2026. | agriloop | CONFIRMED | commit/deployment: git, Vercel | - |
| C-008 | Agriloop began from Andrew's own difficulty selling his pigs at the right price. | agriloop | CONFIRMED | founder_answer: 2026-11-08 | Date approx.; confirm Agriloop lets him list pigs (dossier file 11 §2.5) |
| C-009 | Agriloop is a working beta. | agriloop | CONFIRMED | record: code, audit, deployments | - |
| C-010 | Agriloop has 52 database tables, all with row-level security enabled. | agriloop | CONFIRMED | record: Supabase listing 2026-11-08 | Re-check on recording day |
| C-011 | As of 8 November 2026 Agriloop had about 10 user rows, about 2 listings and 0 orders. | agriloop | CONFIRMED | record: Supabase counts 2026-11-08 | Approximate; includes non-customer accounts; refresh before recording |
| C-012 | Four short videos produced about 2,900 views and one attributable sign-up. | agriloop | CONFIRMED | document: GROWTH_LOG (hand-copied by founder, 6 Nov) | Figures are the founder's own copy |
| C-013 | Most viewers stopped watching at 0:02 on the first video. | agriloop | CONFIRMED | document: GROWTH_LOG | - |
| C-014 | Agriloop has generated no revenue. | agriloop | PARTIALLY_CONFIRMED | record: 0 subscriptions, 0 payment events in the database | Off-platform payments unknown. Not usable in FACT lines; say as REFLECTION until founder confirms |
| C-015 | Andrew's own audit says: "The platform is ahead of its traffic." | agriloop | CONFIRMED | document: agriloop-audit/01-executive-platform-audit.md | Quote exact |
| C-016 | Agriloop's pricing model changed five times in 55 days. | agriloop | CONFIRMED | commit: git history/audit | Do NOT add "without a paying customer" (rests on C-014) |
| C-017 | Andrew will make a decision about Agriloop on 30 November 2026. | agriloop | CONFIRMED | founder_answer: brief | Outcome unknown; never imply a result |
| C-018 | Andrew has felt demotivated about Agriloop. | agriloop | CONFIRMED | founder_answer: 2026-11-08 | His own feeling; do not blame partner or market |
| C-019 | Andrew does outreach, sales, closing and business direction; Claude Code does much of the software development. | andrew-builds | CONFIRMED | founder_answer: 2026-11-08 | Q-D1: exact split to confirm |
| C-020 | Andrew is learning to create content. | andrew-builds | CONFIRMED | founder_answer: 2026-11-08 | - |
| C-021 | TradeNotes development started on 8 November 2026. | tradenotes | CONFIRMED | commit: git (6 commits 13:52-17:38 UTC) | Re-check (Q-E3) |
| C-022 | TradeNotes is not live. | tradenotes | CONFIRMED | deployment: Vercel (4 production deploys in ERROR) | Re-check before filming |
| C-023 | TradeNotes backtesting has not been started. | tradenotes | CONFIRMED | document: IMPLEMENTATION_STATUS.md | Re-check |
| C-024 | TradeNotes has 38 unit tests and 15 isolation checks that pass locally. | tradenotes | CONFIRMED | document: TEST_RESULTS.md | Local runs only |
| C-025 | All four TradeNotes production deploys failed because Vercel blocked a vulnerable Next.js version. | tradenotes | CONFIRMED | deployment: Vercel API 2026-11-08 | Re-check; may be fixed on camera (S28) |
| C-026 | TradeNotes has a CSV import library but no import screen. | tradenotes | PARTIALLY_CONFIRMED | document: IMPLEMENTATION_STATUS.md | Library only; re-check |
| C-027 | TradeNotes billing uses two payment links with manual activation and is not deployed. | tradenotes | PARTIALLY_CONFIRMED | record: plans.ts, DEPLOYMENT.md | Do not show real links |
| C-028 | Andrew has created about 35 repositories in about 14 weeks. | andrew-builds | CONFIRMED | record: GitHub | Count shifts; recheck |
| C-029 | Andrew has not run paid advertising campaigns for SaaS products. | andrew-builds | CONFIRMED | founder_answer: brief | Paid ads = a future channel only |
| C-030 | Andrew records on a Samsung Galaxy Tab S9 FE+. | andrew-builds | PARTIALLY_CONFIRMED | document: shot lists | Whether he also builds on it: Q-D2 |
| C-031 | Andrew plans to document his journey in a series called The Bootstrapper Experiment. | andrew-builds | PLANNED | document: production/ | Nothing published yet |
| C-032 | Andrew has built an Outreach Desk app for sales outreach. | andrew-builds | CONFIRMED | record: Andrew-Builds- repo | - |
| C-033 | Andrew has built MVPs for clients. | yardscale | UNKNOWN | - | Q-F1; never state |
| C-034 | Andrew posts on Instagram. | andrew-builds | UNKNOWN | - | Q-G1 |
| C-035 | Andrew learned to build with AI from YouTube. | andrew-builds | UNKNOWN | - | Q-A8 |
| C-036 | Journaling and backtesting can improve trading discipline. | tradenotes | UNKNOWN | - | Andrew's belief only: HYPOTHESIS line, never FACT |
| C-037 | TradeNotes has six commits, all made on 8 November 2026. | tradenotes | CONFIRMED | commit: git log 13:52:25-17:38:57 UTC (read 8 Nov) | Re-check on recording day |
| C-038 | Two-user isolation tests found that a trade could point at another user's account or strategy. | tradenotes | CONFIRMED | commit: 93ed914; document: TEST_RESULTS.md "Bug found by testing" | Local test harness (shim of the auth schema); not run on a deployed database |
| C-039 | The fix was committed together with the tests that found the bug. | tradenotes | CONFIRMED | commit: 93ed914 (tests + ownership triggers in one commit) | Says nothing about the app being secure overall |
| C-040 | TradeNotes has had four production deploys on Vercel, and all four failed. | tradenotes | CONFIRMED | deployment: Vercel API, 4 deploys read individually 8 Nov | Changes once the fix deploys: re-check; amend wording after the on-camera attempt |
| C-041 | Vercel's error message was: "Vulnerable version of Next.js detected, please update immediately." | tradenotes | CONFIRMED | deployment: Vercel errorCode VULNERABLE_NEXTJS_VERSION, step build | Quote exact |
| C-042 | TradeNotes was pinned to Next.js version 15.5.4. | tradenotes | CONFIRMED | record: package.json at commit 1ce3aa0 | Changes when upgraded |
| C-043 | Every TradeNotes commit lists Claude as the author. | tradenotes | CONFIRMED | commit: git log, 6 of 6 | Does not state the Andrew/Claude split (Q-D1); use with C-019 |
| C-044 | TradeNotes is built with Next.js and set up to deploy through Vercel. | tradenotes | CONFIRMED | record: package.json, Vercel project (framework nextjs) | "Set up", not live (C-022) |
| C-045 | TradeNotes' billing page uses HandyPay payment links. | tradenotes | CONFIRMED | record: src/lib/plans.ts, billing page text | Never show plans.ts (public checkout URLs) |
| C-046 | Andrew earns an affiliate commission from [named tool or platform]. | andrew-builds | UNKNOWN | - | Ask which programmes are real, per tool. Until CONFIRMED, no affiliate or partnership wording anywhere (P-12) |
| C-047 | Andrew uses Claude Code and Vercel to build and deploy TradeNotes. | tradenotes | CONFIRMED | record: git trailers, Vercel deploys by his account; founder_answer 2026-11-09 | - |
| C-048 | Andrew recommends Supabase for the database. | andrew-builds | CONFIRMED | founder_answer: 2026-11-09 | His opinion: OPINION lines only |
| C-049 | Andrew plans to upgrade Next.js on camera and redeploy TradeNotes. | tradenotes | PLANNED | founder_answer: 2026-11-09 approval | Outcome unknown |
| C-050 | Andrew plans to try Neon for testing a different database. | tradenotes | PLANNED | founder_answer: 2026-11-09 | Which database TradeNotes runs on is undecided |
| C-051 | The outcome of the on-camera Next.js upgrade and redeploy. | tradenotes | UNKNOWN | - | Created from the recording itself; script ending lines added at G-RECORD |

## Prohibited statements (never claim; no platform status exists for "false")
P-1 Agriloop is a commercial success or has revenue/orders beyond C-011. P-2 TradeNotes is live, launching, has users, revenue or working backtesting. P-3 Andrew is a profitable or successful trader; any trading performance. P-4 Andrew has paid-ads SaaS experience; the YardScale site line "runs the paid distribution" must not be repeated. P-5 Any client name, testimonial, price, guarantee or timeline. P-6 Any mention of the operating partner, her business, or terms. P-7 Any real user's name or message. P-8 "I moved on from Agriloop" (undecided until 30 Nov). P-9 Expertise in Postgres/RLS/DevOps ("learning, verifying with tests"). P-10 "Journaling changed my results" / "kept making the same mistakes until journaling" (contradicted by founder). P-11 Jamaica "has ~200,000 farmers" (unsourced). P-12 Any affiliate, sponsorship or partnership with Vercel, Anthropic/Claude, Supabase, Neon, HandyPay or a trading platform/broker unless C-046 is CONFIRMED for that exact party; any income, commission or earnings figure; any suggestion that using a tool or broker will make someone profitable.
