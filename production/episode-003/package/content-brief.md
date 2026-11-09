# E003 Content Brief

Status: **G-IDEA APPROVED by Andrew (2026-11-09, "Approved G-IDEA E003").** G-SCRIPT: pending. Strategy docs (CS-0) followed provisionally with Andrew's OK (2026-11-09).

| Field | Content |
|---|---|
| Content ID | `E003` (internal). The public title carries no number (E001/E002 are unrecorded Outreach Desk drafts; see Q-B2) |
| Episode number | 3 (internal) |
| Series / course | The Bootstrapper Experiment, Arc B (TradeNotes). Also feeds the course: M5 (S19, S23, S25) and M6 (S28) |
| Working title | My first TradeNotes test found a bug. My first deploy failed four times. |
| Core idea | On 8 Nov 2026 Claude Code built a trading-journal app in one day. A two-user test found a cross-user bug; then Vercel blocked all four production deploys over the Next.js version. Andrew tries the fix on camera. TradeNotes is not live |
| Audience | Primary: people from sales/service/online business curious about building software with AI. Secondary: solo founders using Claude Code |
| Pillars | P2 SaaS with AI (primary), P4 trading-journal journey (secondary) |
| Purpose | Start Arc B honestly; show the real "tests pass locally, deploy fails" gap; give the course real M5/M6 material |
| Main takeaway (OPINION) | AI can write the app in a day. Whether it is safe and reachable is still a question you have to ask |
| CTA | `CTA-E003-YT`: follow the build. No sign-up promise: the product cannot be used yet |
| Length guide | About 9-10 min (length follows the material) |
| Trading content | **Yes**: approved disclaimer (below) spoken early, repeated on screen and in every description |
| People on screen | None. Voiceover recorded separately over tablet screen recordings |
| Moment window | 2026-11-08 to the day of the fix attempt |

## Approved disclaimer (Andrew, 2026-11-09)
"This is a software project, not trading advice. Trading is high risk and you can lose money. My own trading results aren't where I want them to be, and nothing here is a recommendation to buy or sell anything."

## Evidence sources (all verified read-only, 8 Nov)
TradeNotes repo git log (6 commits, authors, commit 93ed914); `docs/TEST_RESULTS.md`; Vercel API (4 deployments, errorCode `VULNERABLE_NEXTJS_VERSION`); `package.json` (next 15.5.4); `src/lib/plans.ts` (never shown); founder answers 8 and 9 Nov. Claims: C-002, C-003, C-019, C-022, C-024, C-037..C-051 in `docs/CLAIMS_REGISTER.md`.

## Andrew's decisions recorded 2026-11-09
- Fix on camera: **approved** (two honest endings; outcome not scripted).
- Builds on the tablet **and** records on it (Q-D2 answered). Does not mean the split of work is defined (Q-D1 still open).
- Voiceover only: footage is tablet screen recordings; no face to camera needed for this episode.
- Recommends Supabase (OPINION, C-048); Neon for testing a different database (PLANNED, C-050). Database for TradeNotes is **undecided**, so no database claim is spoken as fact.
- Wants affiliate content using his sales skill. **Constraints in the script and in P-12:** no affiliate/partnership wording until each programme is confirmed (C-046); disclosure before the first affiliate mention and in the description; no earnings figures; broker mention only with the trading disclaimer and no profitability suggestion.

## Scope note: the 60-minute course
The course is separate packages, one at a time. E003 is not the course. Reusable parts: S23 (isolation test), S25 (unit tests), S28 (deploy fix) and the "tests pass locally vs shipped" lesson for M5/M6. Next package after E003 is Andrew's choice (suggestion: course M5, or Idea 2/3).

## Open items before G-SCRIPT is approved
1. `[RECORD]` L010 why TradeNotes; L014 what you personally decided or checked on 8 Nov (your words, only if true).
2. Affiliate: which programmes are real (C-046)? Until answered the affiliate slot stays a placeholder.
3. Database for TradeNotes (Supabase vs Neon test) and whether the Agriloop-Supabase rollback should run (still pending your "retry").
4. Ending lines are written after the attempt (C-051).
