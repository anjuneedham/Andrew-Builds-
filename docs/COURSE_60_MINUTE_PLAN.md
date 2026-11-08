# From Sales to SaaS: 60-Minute Course Plan (v2, reconciled with the founder dossier)

Status: **PROPOSED, awaiting approval (CS-0).** Not scripted. Total **60:00 = 3600 s** (checked below).
Source of truth: the dossier's `06_course_blueprint.md` and `07_video_production_research.md` (S01-S46), from `ANDREW_BUILDS_CONTEXT_PACK.md` (kept OUTSIDE this public repo, see handoff). v1 of this plan (built before the dossier was found) is superseded.
Dossier title recommendation: **"From Sales to SaaS: Build Your First Software Product With AI"** (subtitle promises mistakes, not riches). Title not yet approved.
Claim IDs refer to `docs/CLAIMS_REGISTER.md`. Shot IDs (`S##`) refer to the dossier shot list (appendix A).
Platform: set `course_modules.duration_s` to the values below; the DB allows READY only at exactly 3600 s.

## Structure
| # | Module / lesson title | Dur. | Start-End | Learning objective (learner can...) | Practical demonstration | Required screen recordings | Evidence (claims) | Exercise |
|---|---|---|---|---|---|---|---|---|
| M0 | Cold open: what I built, what the numbers said | 1:30 | 0:00-1:30 | state the honest premise: building is no longer the hard part | Agriloop beta vs its real numbers | S01, S02, S03 | C-009, C-010, C-011, C-012, C-015 | none |
| M1 | My journey: sales to marketing to software | 5:30 | 1:30-7:00 | map their own skills onto product building | 3-stage timeline; repo time-lapse | S04, S05, S07 (S06 needs client OK) | C-001, C-002, C-004, C-005, C-008, C-028 (sales story UNKNOWN: Q-A3) | list 3 skills from their job |
| M2 | Find a problem worth solving | 6:00 | 7:00-13:00 | write a pain-point sentence and list workarounds | competitor table; "solve your own problem" strength and risk | S08, S09 (S10 ask) | C-008 | complete "[Person] struggles to ___ because ___, so they ___" (60 s) |
| M3 | Validate before you build (what I skipped) | 6:30 | 13:00-19:30 | design a 48-hour test for 3 assumptions | assumptions table; decision log "reverses if" | S09, S11 (S12 only if a real call happens) | C-016; UNKNOWN: whether any farmer was interviewed (Q-A2) | 3 assumptions + 1 test each (90 s) |
| M4 | Plan and scope the MVP | 7:00 | 19:30-26:30 | produce a 5-step journey and a "not building" list | wall of routes shrinking to five | S13, S14, S15, S16, S17 | C-009, C-010 | list 5 steps, strike the rest (90 s) |
| M5 | Build with Claude and modern tools | 10:00 | 26:30-36:30 | follow a repeatable AI-build workflow | live Claude Code session; PR with CI; RLS test catching a leak | S18, S19 (create), S20, S21, S22, S23-S25 (record runs), S26 | C-019, C-021, C-024; role stated per C-019; no Postgres expertise claim (P-9) | write 5 AGENTS.md rules (2 min) |
| M6 | Ship it: Vercel, Supabase, domain, payments | 7:00 | 36:30-43:30 | write a deploy checklist and a first-10-customers payment plan | read the failed TradeNotes deploy log | S27, S28, S29, S30, S31, S32 (S33, S34 ask) | C-022, C-025, C-027 | payment plan for 10 customers (60 s) |
| M7 | Get users: organic distribution | 6:00 | 43:30-49:30 | write a 2-second hook and a first-ten-users plan | growth log table; retention drop at 0:02 | S35, S36, S37, S38, S39 | C-012, C-013, C-029 | write a 2-second hook (90 s) |
| M8 | Agriloop debrief, the decision, TradeNotes | 7:00 | 49:30-56:30 | build a stop/continue scorecard with numbers and dates | Agriloop scorecard; TradeNotes honest status | S40 (ask), S41, S42, S43, S44, S45 (to camera, create) | C-011, C-014, C-017, C-018, C-003, C-021, C-022, C-023 | stop/continue criteria (90 s) |
| M9 | Your next steps and working with me | 3:30 | 56:30-60:00 | leave with one action | one-page founder loop; application page | S46 (ask: page must exist) | none stated as fact (offer terms UNKNOWN: Q-F1/F2) | homework: pain sentence + 3 assumptions + 48 h test |
| | **TOTAL** | **60:00** | | | | | | |

Arithmetic: 90 + 330 + 360 + 390 + 420 + 600 + 420 + 360 + 420 + 210 = **3600 s = 60:00**.
Format mix (dossier): ~35% voice/camera, ~45% screen recording, ~15% graphics, ~5% exercise prompts.

## Transitions (one line each, written later)
M0→1 "To explain how I got here I need to start before the code." · 1→2 "The first skill is finding a problem." · 2→3 "A problem is a guess. Next, how to test it." · 3→4 "Once something survives, you scope the smallest version." · 4→5 "Now the part you came for: building with AI." · 5→6 "Code isn't a product until strangers can reach it." · 6→7 "Shipping gets a URL. Distribution gets a user." · 7→8 "When the data comes in, you decide: improve or change direction." · 8→9 "If you want to do this yourself, here's what to do next."

## Final takeaway
Dossier central message (founder's brief, verbatim): "You don't need to know everything about software development to start building software. You need to understand problems, learn how to use the tools, build something useful, get it into people's hands and learn from the process."

## Changes forced by the founder's 8 Nov answers
- **M1 opens on the pigs** (Agriloop began from his own difficulty selling pigs at the right price, C-008). **M2** teaches "solve your own problem" with both the strength and the risk (one data point: himself).
- **M8 is a live decision, not a finished pivot.** Never say "I moved on from Agriloop". Say "I'm at a decision point" (30 Nov). The recorded outcome (S45) is shot only after he decides; it is never scripted in advance.
- **TradeNotes is a personal build-in-public experiment** (C-003, C-021..23), never a success story. Do not reuse the draft copy "journaling changed my results" (contradicted by the founder).
- **No partner** mention, terms or business in any module (S40/S41 must exclude partner rows).
- Trading disclaimer (wording Q5) on any TradeNotes frame.

## Appendix A: dossier shot list S01-S46 status (import into `shots` at P2; do not alter IDs)
READY (exists now): S01-S05, S07-S09, S11, S13-S18, S20-S22, S26, S27, S29, S30, S35-S39, S41, S42.
ASK (needs permission or decision): S06 client OK · S10 consider $10k challenge mention · S33 HandyPay (hide balances) · S34 Namecheap · S40 decision log, omit partner/profit rows · S46 apply page must exist.
TO CREATE: S12 real validation call (with permission) · S19 live Claude Code session (tablet, hide session URL) · S23-S25 recorded test runs · S28 deploy fix on camera (needs Andrew's approval to upgrade Next.js) · S31 bank-transfer flow on test data · S32 billing page without real links · S43 local TradeNotes landing · S44 scorecard graphic · S45 to-camera decision.
Dossier production dependencies: fix or redeploy TradeNotes; record test runs once; clean Agriloop demo environment; decide partner mention (Q-C2); record S45 early; hold footage with real people's data until permission.
Dossier file naming `CRS_<module>_<shot>_<slug>_<YYYYMMDD>_v<nn>.mp4` is adopted (see ASSET_REGISTER_TEMPLATE.md).
Re-verify on recording day: Agriloop counts, TradeNotes deploy state, every URL shown.
