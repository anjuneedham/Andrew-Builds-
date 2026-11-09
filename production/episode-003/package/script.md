# E003 Script v2 (DRAFT, awaiting G-SCRIPT). v2 2026-11-09: deploy count now six, Neon switch added

Episode E003 · Pillar P2 primary / P4 secondary · Arc B · Length guide: expect 7-9 min (about 580 spoken words, roughly 4 min of narration; live test run and fix attempt add screen time, so expect 7-9 min) · **Trading content: yes** · Gate status: G-IDEA [x] G-SCRIPT [ ] G-RECORD [ ] G-EDIT [ ] G-QA [ ] G-PUBLISH [ ]
Line format: `L### | KIND | text | claims | shot`. Shot IDs are provisional until Gate 3. FACT lines use the claim wording in `claims-register.md`. Any reword is re-checked.
Voice: Andrew, voiceover over tablet screen recordings. `[RECORD]` = only in your own words and only if true. Nothing here is a number or outcome you have not verified.

## 1. Hook (0:00-0:35)
| ID | Kind | Text | Claims | Shot |
|---|---|---|---|---|
| L001 | FACT | On day one of TradeNotes, a test found that a trade could point at another user's account or strategy. | C-037, C-038 | S01 |
| L002 | FACT | Then every one of my production deploys failed. | C-040 | S02 |
| L003 | FACT | TradeNotes is not live. | C-022 | S02 |
| L004 | OPINION | This is the day, including the parts that went wrong. | - | S02 |

## 2. Context (0:35-2:30)
| ID | Kind | Text | Claims | Shot |
|---|---|---|---|---|
| L005 | DISCLAIMER | This is a software project, not trading advice. Trading is high risk and you can lose money. My own trading results aren't where I want them to be, and nothing here is a recommendation to buy or sell anything. | - (approved wording) | S03 + GFX |
| L006 | FACT | I've traded for about seven years and have run other online businesses as a solopreneur with small teams. | C-002 | S03 |
| L007 | FACT | My trading results are not where I want them to be. | C-003 | S03 |
| L008 | HYPOTHESIS | I believe writing trades down and testing changes can help with discipline. I don't know if it will. This is an experiment. | C-036 [UNKNOWN, context only] | S03 |
| L009 | REFLECTION | [RECORD: in your own words, why you are building TradeNotes. Only what is true.] | - | S03 |
| L010 | FACT | I do outreach, sales, closing and the direction of the business. Claude Code does much of the software development. | C-019 | S04 |
| L011 | FACT | Every TradeNotes commit lists Claude as the author. | C-043 | S04 |
| L012 | OPINION | So my job here isn't to read the code. It's to ask what could go wrong with what Claude built. | - | S04 |
| L013 | REFLECTION | [RECORD: what you personally decided or checked on 8 November. Skip if nothing.] | - | S04 |

## 3. The build (2:30-4:00)
| ID | Kind | Text | Claims | Shot |
|---|---|---|---|---|
| L014 | FACT | TradeNotes' first six commits were all made on 8 November 2026. | C-037 | S05 |
| L015 | FACT | It is built with Next.js and set up to deploy through Vercel. | C-044 | S05 |
| L016 | FACT | Its billing page uses HandyPay payment links. | C-045 | S06 |
| L017 | DIRECTION | Scroll the commit list on screen. Hold on the commit messages only (no session URL visible). | - | S05 |
| L018 | FACT | TradeNotes has 38 unit tests, 23 database isolation checks and 28 browser checks that pass locally. | C-024 | S07 |
| L019 | DIRECTION | Re-run the tests live in a terminal. Show the real result. If it differs from C-024, this section is rewritten. | - | S07 |
| L020 | OPINION | Passing locally is not the same as shipped. Keep that in mind. | - | S07 |

## 4. The test that caught the bug (4:00-5:45)
| ID | Kind | Text | Claims | Shot |
|---|---|---|---|---|
| L021 | OPINION | Here's the idea in plain English: one user should never be able to touch another user's data. | - | S08 |
| L022 | DIRECTION | Show the isolation test file and the commit message for the fix. | - | S08 |
| L023 | FACT | Two-user isolation tests found that a trade could point at another user's account or strategy. | C-038 | S08 |
| L024 | FACT | The fix was committed together with the tests that found the bug. | C-039 | S08 |
| L025 | REFLECTION | I would not have found that by clicking around the app. A test did. | - | S08 |
| L026 | OPINION | That doesn't make the app secure. It means one hole got found early. | - | S08 |

| L047 | FACT | Since that test, I've switched TradeNotes to Neon and Better Auth, so that exact code has been replaced. | C-054 | S08 |

## 5. The deploy that wouldn't ship (5:45-7:15)
| ID | Kind | Text | Claims | Shot |
|---|---|---|---|---|
| L027 | DIRECTION | Show the Vercel deployments list (crop out any source/session panel). | - | S09 |
| L028 | FACT | TradeNotes has had six production deploys on Vercel, and all six failed. | C-040 | S09 |
| L029 | FACT | Vercel's error message was: "Vulnerable version of Next.js detected, please update immediately." | C-041 | S10 |
| L030 | FACT | TradeNotes was pinned to Next.js version 15.5.4. | C-042 | S10 |
| L031 | OPINION | In plain English, Vercel looked at the framework version and refused to publish the app. | - | S10 |
| L032 | OPINION | I'd rather the platform stop me than ship something with a known problem. | - | S10 |

## 6. The fix, on camera (7:15-9:00)
| ID | Kind | Text | Claims | Shot |
|---|---|---|---|---|
| L033 | HYPOTHESIS | My plan is to upgrade Next.js, run the tests again, and deploy again. | C-049 [PLANNED] | S11 |
| L034 | HYPOTHESIS | I don't know if that's all it takes. Let's see what the screen says. | - | S11 |
| L035 | DIRECTION | Real, unscripted attempt on the tablet: ask Claude Code to upgrade, run tests, push, watch Vercel. Cut waiting time only, never results. Hide the session URL. | - | S11-S13 |
| L036 | FACT | **ENDING A or B, written after recording** (deploy works, or still failing). Added at G-RECORD with its own claim C-051, then re-gated. | C-051 [UNKNOWN until recorded] | S13 |
| L037 | REFLECTION | [RECORD: your honest reaction, whichever way it went.] | - | S13 |

## 7. Where it stands + the tools (9:00-10:15)
| ID | Kind | Text | Claims | Shot |
|---|---|---|---|---|
| L038 | FACT | I use Claude Code and Vercel to build and deploy TradeNotes. | C-047 | S14 |
| L039 | OPINION | For the database, I recommend Supabase. | C-048 | S14 |
| L040 | FACT | TradeNotes now uses Neon for its database and Better Auth for sign-in. | C-054 | S14 |
| L041 | DISCLAIMER | [AFFILIATE DISCLOSURE: ONLY if a real affiliate relationship exists for a named tool. Draft: "Some links in the description are affiliate links. If you sign up through them I may earn a commission, at no extra cost to you."] | C-046 [UNKNOWN: slot stays empty until confirmed] | S14 |
| L042 | OPINION | I work in sales, so here's my honest pitch: use a tool if it solves the problem you have this week, and check the pricing yourself. | - | S14 |
| L046 | FACT | **[PUBLISH BLOCKER: say this only once the program is live]** TradeNotes has an affiliate program: affiliates earn 30% of the referred person's first month and 10% for as long as that person stays subscribed. | C-053 [UNKNOWN until built] | S14 |

## 8. Close (10:15-10:45)
| ID | Kind | Text | Claims | Shot |
|---|---|---|---|---|
| L043 | QUESTION | The open question for next time: what happens when a real person tries to use it? | - | S15 |
| L044 | DISCLAIMER | This is a software project, not trading advice. | - | GFX |
| L045 | CTA | Follow the build. I'm showing the real work, including what breaks. | `CTA-E003-YT` | S15 |

## Claims appendix
See `claims-register.md`.

## Open items
UNKNOWN: C-046 (affiliate programmes, per tool), C-051 (fix outcome), **C-053 (TradeNotes affiliate program must be built before publishing)**. `[RECORD]`: L009, L013, L036-L037. Decisions: database choice (L039), Supabase rollback pending.

## Checks (manual; app-level checker not built)
Banned phrases: 0 · Hide list: scripted shots avoid plans.ts, Supabase dashboard, session URLs · Disclaimer: present (L005, L044, description) · FACT lines cite CONFIRMED only: **yes**, except L036 (UNKNOWN by design; blocks the DB gate until the ending is added at G-RECORD) · Digits in non-FACT lines: none (numbers in L018, L028 are FACT and must be re-checked on recording day) · Planned items spoken as plans: L033, L040 · Affiliate wording: none spoken as fact (P-12).
