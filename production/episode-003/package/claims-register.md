# E003 Claims Register

Source of truth for statements: `docs/CLAIMS_REGISTER.md`. This file maps each E003 claim to the script. Evidence read-only on 8 Nov 2026 (Vercel API + public TradeNotes repo). **Re-verify all rows on recording day.** Only CONFIRMED claims back FACT lines.

| Claim | Exact claim | Status | Evidence / source | Limitation | Script lines |
|---|---|---|---|---|---|
| C-002 | Andrew has traded for about seven years and has run other online businesses as a solopreneur with small teams. | CONFIRMED | founder_answer 8 Nov | Not expertise or results | L006 |
| C-003 | Andrew's trading results are not where he wants them to be. | CONFIRMED | founder_answer 8 Nov | Never state numbers | L007 |
| C-019 | Andrew does outreach, sales, closing and business direction; Claude Code does much of the software development. | CONFIRMED | founder_answer 8 Nov | Exact split (Q-D1) open | L010 |
| C-022 | TradeNotes is not live. | CONFIRMED | Vercel: no READY deploy | Re-check; changes if the fix deploys | L003 |
| C-024 | TradeNotes has 38 unit tests and 15 isolation checks that pass locally. | CONFIRMED | `docs/TEST_RESULTS.md` | Not re-run by me; re-run on camera (L019) | L018 |
| C-036 | Journaling and backtesting can improve trading discipline. | UNKNOWN | Andrew's belief only | HYPOTHESIS line, never FACT | L008 |
| C-037 | TradeNotes has six commits, all made on 8 November 2026. | CONFIRMED | git log, 13:52:25-17:38:57 UTC | Re-check | L001, L014 |
| C-038 | Two-user isolation tests found that a trade could point at another user's account or strategy. | CONFIRMED | commit 93ed914; TEST_RESULTS.md | Local harness, not a deployed database | L001, L023 |
| C-039 | The fix was committed together with the tests that found the bug. | CONFIRMED | commit 93ed914 | Not a claim of overall security | L024 |
| C-040 | TradeNotes has had four production deploys on Vercel, and all four failed. | CONFIRMED | Vercel API, each deploy read | Amend after the attempt | L002, L028 |
| C-041 | Vercel's error message was: "Vulnerable version of Next.js detected, please update immediately." | CONFIRMED | Vercel errorMessage | Quote exact | L029 |
| C-042 | TradeNotes was pinned to Next.js version 15.5.4. | CONFIRMED | package.json @ 1ce3aa0 | Past tense: true before the upgrade | L030 |
| C-043 | Every TradeNotes commit lists Claude as the author. | CONFIRMED | git log, 6 of 6 | With C-019 only | L011 |
| C-044 | TradeNotes is built with Next.js and set up to deploy through Vercel. | CONFIRMED | package.json; Vercel project | Not live | L015 |
| C-045 | TradeNotes' billing page uses HandyPay payment links. | CONFIRMED | plans.ts; billing page | Never show plans.ts | L016 |
| C-046 | Andrew earns an affiliate commission from [named tool or platform]. | **UNKNOWN** | none | Slot L041 stays empty; P-12 | L041 |
| C-047 | Andrew uses Claude Code and Vercel to build and deploy TradeNotes. | CONFIRMED | git trailers; Vercel deploys | - | L038 |
| C-048 | Andrew recommends Supabase for the database. | CONFIRMED (opinion) | founder_answer 9 Nov | OPINION line only | L039 |
| C-049 | Andrew plans to upgrade Next.js on camera and redeploy TradeNotes. | PLANNED | founder_answer 9 Nov | Outcome unknown | L033 |
| C-050 | Andrew plans to try Neon for testing a different database. | PLANNED | founder_answer 9 Nov | Database choice undecided | L040 |
| C-051 | The outcome of the on-camera Next.js upgrade and redeploy. | **UNKNOWN** | recorded evidence only | Ending lines added at G-RECORD | L036 |
| C-052 | TradeNotes will pay affiliates 30% of the referred person's first month and 10% for as long as that person stays subscribed. | PLANNED | founder_answer 9 Nov | Terms undecided; not built | L046 (conditional) |
| C-053 | TradeNotes has a live affiliate program with those terms. | **UNKNOWN** | none | **PUBLISH BLOCKER**: must be built and working before the video is published | L046 |

## Non-factual lines (no claim needed)
OPINION: L004, L012, L020, L021, L026, L031, L032, L039, L042. REFLECTION (Andrew's own, approved before recording): L009, L013, L025, L037. HYPOTHESIS: L008, L033, L034, L040. QUESTION: L043. DISCLAIMER: L005, L041, L044. CTA: L045. DIRECTION: L017, L019, L022, L027, L035.

## Prohibited statements checked
P-1 no Agriloop success · P-2 not live, no users/revenue · P-3 no performance · P-4 no paid-ads · P-6 no partner · P-10 not used · P-12 no affiliate/partnership wording.
