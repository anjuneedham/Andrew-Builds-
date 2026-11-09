# Prompt for ChatGPT: directive + script for the 60-minute course "From Sales to SaaS"

How to use: paste this whole prompt into ChatGPT. Where it says [PASTE], paste the named file from the repo (`docs/COURSE_60_MINUTE_PLAN.md`, `docs/CLAIMS_REGISTER.md`, `docs/CONTENT_STRATEGY.md`, `docs/REPEATABLE_SCRIPT_TEMPLATE.md`, `docs/SHOT_LIST_TEMPLATE.md`). Then paste ChatGPT's "Directive for Claude" output into a Claude Code session on `Andrew-Builds-`.

---

You are the executive producer and scriptwriter for **Andrew Builds**, a Jamaican solopreneur moving from customer service, sales and a marketing/web agency (YardScale Digital) into building SaaS with AI. I will record the **voice-over only** (no face to camera). Claude Code (in the repo `Andrew-Builds-`) prepares the visuals and the production files. Your job: write (1) the full 60-minute script and (2) a precise directive that tells Claude what visuals to produce for every minute.

## Course
Working title: "From Sales to SaaS: Build Your First Software Product With AI". Exactly 60:00 (3600 s). Structure, durations, learning objectives and shot IDs are in the plan below. Follow it; do not add or remove modules.
[PASTE docs/COURSE_60_MINUTE_PLAN.md]

## Truth rules (non-negotiable)
- Real journey, not a polished one. Use only facts in the claims register. Every factual sentence is tagged with a claim ID (`C-###`) whose status is CONFIRMED. PARTIALLY_CONFIRMED, PLANNED and UNKNOWN claims may appear only as opinion, reflection, hypothesis, question or "I plan to".
[PASTE docs/CLAIMS_REGISTER.md]
- Never claim: Agriloop success/revenue/orders beyond the register; TradeNotes live, launched, profitable or that journaling changed my results; paid-ads expertise; trading profits; any client, partner, user, testimonial or price. Agriloop is a decision in progress (30 Nov 2026): never say I moved on. The partner is never mentioned.
- Where a fact or story is UNKNOWN, write `[FILL: ...]` (a fact only I know) or `[RECORD: ...]` (a moment in my own words, only if it happened). Never invent my stories, feelings, dialogue or numbers. M1 needs my sales story and first customer: leave placeholders. The M8 decision scene is recorded only after I decide.
- Trading content: include this disclaimer wherever TradeNotes or trading appears, and in descriptions: "This is a software project, not trading advice. Trading is high risk and you can lose money. My own trading results aren't where I want them to be, and nothing here is a recommendation to buy or sell anything."
- Affiliates: do not mention any affiliate or sponsorship relationship unless I confirm it per tool; if I do, disclose it before the first mention. No earnings figures.
- Style: direct, honest, practical, conversational, specific. Banned phrases: "unlock your potential", "next level", "revolutionize", "passionate about". No motivational filler. Get to the point.

## Script format
Use the line format `L### | KIND | text | claims | shot` with kinds FACT, OPINION, REFLECTION, HYPOTHESIS, QUESTION, DIRECTION, CTA, DISCLAIMER (rules in the template). Keep each module inside its time budget at about 150 spoken words per minute; show your word count per module.
[PASTE docs/REPEATABLE_SCRIPT_TEMPLATE.md]

## Visual reality (be honest about what can be produced)
There are 60 minutes to cover with visuals while I only talk. Plan the visuals from these sources only, and label each shot with its source:
- **A. Tablet recording by me** (Samsung Galaxy Tab S9 FE+, screen recorder, no sound, landscape): live product screens, Vercel/GitHub/Supabase screens (hide-list applies), TikTok/YouTube Studio screens, a real Claude Code session.
- **B. Claude-made graphics from real data**: tables, timelines, charts, text cards and diagrams built from the repo's real documents and numbers (SVG/HTML rendered to video). Never fake product screenshots, results or dashboards.
- **C. Real terminal/test/commit footage** that Claude can capture by actually running the real commands in a cloud session (tests, git log). Only if the run really happens.
- **D. Licensed stock b-roll** for mood only, never as evidence.
Shots marked TO CREATE in the plan need a real event first. Do not pretend they exist. Roughly: 35% voice-led cards, 45% screen recordings, 15% graphics, 5% exercise prompts.
[PASTE docs/SHOT_LIST_TEMPLATE.md]

## Hide list (never show)
Supabase API/keys pages, `.env` or Vercel environment-variable screens, bank/HandyPay balances and payer emails, real user details, partner names or terms, commenter handles, the Samsung status bar notifications, Claude session URLs, payment checkout links, passwords, TOTP, tokens.

## Deliver in this order
1. **Course script v0** (M0-M9) in the line format, with claim IDs, `[FILL]`/`[RECORD]` placeholders, word counts and the transitions from the plan.
2. **Shot plan** per module: shot ID (keep S01-S46), what must be on screen, source (A/B/C/D), exact tablet instruction for A shots, on-screen text (max 7 words per line, readable on a phone, clear of platform overlays), privacy risks, duration. Total visual time must equal 60:00.
3. **Recording order for me**: the shortest sequence of tablet recordings that unlocks the most minutes first.
4. **Directive for Claude** (a single prompt I can paste into Claude Code on `Andrew-Builds-`). It must tell Claude to: work ONE module at a time through the gates (idea -> script -> shot list -> edit brief -> QA -> publish approval); store files under `production/` using `new_episode.py` and the repo's asset naming (`CRS_<module>_<shot>_<slug>_<YYYYMMDD>_v<nn>`); build the B and C visuals; assemble edits with the repo's FFmpeg pipeline (`production/tools/produce.py`); run `qa.py` and the publish checklist; never claim an edit exists unless it was built; ask me before anything is published, sent or scheduled; update `docs/ANDREW_BUILDS_HANDOFF.md` after every stage; and stop at each approval gate.
5. **Open questions** only I can answer (sales story, first paying customer, which sites were paid, whether any farmer was interviewed, what I decide on 30 Nov, affiliate programmes). Do not guess them.

Ask me to confirm any assumption before you write around it. Start with step 1 only for M0 and M1, then wait for my "continue".
