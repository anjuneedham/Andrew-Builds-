# Andrew Builds: Content Strategy

Status: **PROPOSED, awaiting Andrew's approval (gate CS-0).** Last updated 2026-11-08 (reconciled with the founder dossier).
Executor: Claude Sonnet (CONTENT-BUILD). This file is the rulebook; the templates beside it are the forms.

## 1. Positioning
Andrew is a Jamaican solopreneur moving from selling and marketing other people's products to building his own software with AI (Claude Code).
Andrew's role: outreach, sales, closing, business direction. Claude Code writes much of the code. The content shows that work as it happens.

What the brand is NOT allowed to say (unless a CONFIRMED claim says otherwise):
- Agriloop is a commercial success. (It is a working beta with very little traction; decision point 30 November.)
- TradeNotes is live or improves trading results. (Development has just started.)
- Andrew is a paid-ads expert or has run paid SaaS campaigns. (He has not.)
- Any revenue, user count, testimonial, quote, date or result without a claim ID.

## 2. Five content pillars
| # | Pillar | What it covers | Main evidence | Typical format |
|---|---|---|---|---|
| P1 | BUILD IN PUBLIC | Commits, deployments, product decisions, failures, milestones | git log, deployment records, `moments` table | Long-form episode segments, daily shorts |
| P2 | SAAS WITH AI | How Claude Code is used, prompts, review loop, limits | Session recordings, diffs, failing/passing tests | Tutorials, course lessons, shorts |
| P3 | FOUNDER LESSONS | Customer service, sales, outreach, agency (YardScale Digital), online ventures | Founder answers (claims), Outreach Desk activity log | Talking-head + screen, text posts |
| P4 | TRADING-JOURNAL JOURNEY | TradeNotes build, journaling and backtesting as a discipline experiment | TradeNotes repo, Andrew's own journal process (no P&L) | Build segments, reflections. Disclaimer always |
| P5 | AGRILOOP DECISION DOCUMENTARY | Marketplace build, validation, low traction, demotivation, the 30 Nov decision | Agriloop repo, beta usage numbers only if CONFIRMED, founder reflections | Documentary episodes, decision episode |

Mix guidance (not a quota): each long-form episode has one primary pillar and at most one secondary pillar.

## 3. Formats and platforms
| Asset | Platform | Role |
|---|---|---|
| The Bootstrapper Experiment (long-form documentary) | YouTube | Main documentary asset |
| From Sales to SaaS (60:00 course) | YouTube (or course host, TBD: Q-C3) | Main educational asset |
| Shorts / Reels / TikToks | YouTube Shorts, Instagram, TikTok | Reach and entry points; each links back to a source episode |
| Text and lesson posts | Instagram captions/carousels, YouTube community | Support, no new claims beyond the source |

Organic only. No paid promotion is planned.

## 4. The Bootstrapper Experiment: documentary format
**Premise:** real-time documentary of Andrew going from selling other people's products to building and trying to grow his own.
**Rules of the format**
1. Follow actual work. Each episode is anchored to real events logged in `moments` (commit, deployment, failure, decision, milestone) inside a stated date window.
2. Real environment: Andrew's actual desk, tablet (Galaxy Tab S9 FE+) and screens. No staged sets.
3. Tablet screen recordings wherever practical (see SHOT_LIST_TEMPLATE.md capture rules). Demo data labelled; real data redacted.
4. Show genuine work: Claude Code sessions, test runs, deployments, outreach in Outreach Desk (names hidden).
5. Setbacks stay in. An episode where the thing did not work is a valid episode.
6. Capture decisions and consequences: every episode states the decision made (or deferred) and, in a later episode, what followed.
7. Connect to the arc: every episode ends with the open question that carries into the next one.
8. No manufactured drama: no fake countdowns, no reaction shots of things that did not happen, no music cues implying success.
9. Length guide: 8-15 min. Length follows material, not a target.

**Current arcs (real, open):**
- Arc A, Agriloop: beta to the 30 November decision. Andrew has NOT decided (he feels demotivated and may try to make it work); never say he "moved on". Dossier evidence: about 10 user rows, about 2 listings, 0 orders (8 Nov), about 2,900 video views to 1 sign-up (C-011, C-012). The decision episode is recorded only after Andrew decides; the outcome is never scripted in advance.
- Arc B, TradeNotes: started 8 Nov 2026, not live, deploys blocked, backtesting not started (C-021..C-025). Andrew's own trading results are not where he wants them (C-003). No trading performance, no "journaling changed my results".
- Arc C, the system itself: Outreach Desk + content platform as the tools running the business.

No episode calendar is set in this document. Episodes are scheduled in the platform (P1 calendar, not yet built) only from logged moments.

## 5. Evidence and claim rules (summary; full detail in REPEATABLE_SCRIPT_TEMPLATE.md)
- Every factual sentence is a `FACT` line citing >= 1 claim ID (`C-###`). Only `CONFIRMED` claims may back a FACT line (Q7 strict, enforced by DB trigger).
- `PARTIALLY_CONFIRMED`, `PLANNED`, `UNKNOWN` claims can only appear in non-FACT lines (REFLECTION, OPINION, HYPOTHESIS, QUESTION) and must be worded as such.
- Planned features are spoken as plans ("I plan to...", PLANNED claim) never as done.
- Banned phrases: "unlock your potential", "next level", "revolutionize", "passionate about". Direct copy only.
- Trading content carries the risk disclosure (wording pending Q5) and "not financial advice".
- No real people, partners, clients or users named or shown without written consent (consent_ref on the asset). Never mention partner terms.
- Never show passwords, keys, banking or payment details. Hide list checked on every asset before publish.
- Nothing is published or sent without explicit founder approval.

## 6. Production workflow and approval gates
```
IDEA -> [G-IDEA] -> EVIDENCE COLLECTION -> EPISODE PLAN -> SCRIPT -> [G-SCRIPT]
 -> SHOT LIST -> RECORDING -> [G-RECORD] -> EDITING -> [G-EDIT] -> QA -> [G-QA]
 -> [G-PUBLISH] -> PUBLISH (Andrew posts) -> METRICS -> REVIEW -> new IDEAs
```
| Step | Owner | Output | Platform state (as built in P0) |
|---|---|---|---|
| IDEA | Sonnet proposes from `moments`, Andrew adds | Idea row with pillar + source moment | `ideas.status=BACKLOG` |
| **G-IDEA** | Andrew | "Approved idea" | idea promoted to `episodes.status=IDEA` (P1) |
| EVIDENCE COLLECTION | Sonnet | Claims + sources; list of UNKNOWNs to ask Andrew | `claims`, `sources` |
| EPISODE PLAN | Sonnet | REPEATABLE_EPISODE_TEMPLATE filled | `episodes.status=SCRIPTING` |
| SCRIPT | Sonnet drafts, Andrew supplies own words | REPEATABLE_SCRIPT_TEMPLATE, every line tagged | `scripts.status=DRAFT -> IN_REVIEW` |
| **G-SCRIPT** | Andrew | Claim checker green + Andrew "approved" | `scripts.status=READY_TO_RECORD` (DB blocks if gate fails), episode `READY_TO_RECORD` |
| SHOT LIST | Sonnet | SHOT_LIST_TEMPLATE | `shots.status=PLANNED` |
| RECORDING | Andrew | Raw files named per ASSET_REGISTER | `shots.status=CAPTURED`, `assets` rows, episode `RECORDED` |
| **G-RECORD** | Andrew | Takes accepted, re-shoots listed | script `LOCKED` |
| EDITING | Sonnet via `production/tools` or Andrew | Edit vN | episode `EDITING` |
| **G-EDIT** | Andrew | Edit approved | - |
| QA | Sonnet runs `qa.py` + PUBLISH_CHECKLIST | Checklist complete | episode `QA` |
| **G-QA** | Andrew | QA signed | episode `READY_TO_PUBLISH` |
| **G-PUBLISH** | Andrew | Explicit "publish" per post | `posts.status=APPROVED` |
| PUBLISH | **Andrew only** | Live URL recorded | `posts.status=PUBLISHED` |
| METRICS / REVIEW | Sonnet records, Andrew decides | METRICS_REVIEW_PLAYBOOK | `metrics` (append-only), `growth_log`, `content_lead_links` |

Approval wording: Andrew replies in chat or the platform with "Approved G-<GATE> <episode code>". Silence is not approval.

## 7. Repurposing, metrics
See REPURPOSING_PLAYBOOK.md (>= 3 standalone shorts per episode when the material supports it, never forced) and METRICS_REVIEW_PLAYBOOK.md (platform metrics kept separate from business outcomes).

## 8. Reused material
| Source | Reuse |
|---|---|
| `production/` pipeline (produce.py, qa.py, make_docs.py, new_episode.py, suggest_content.py) | Editing, QA and short building. Unchanged |
| `production/templates/*` | Merged into the new templates (short extraction, performance tracking, shot list) |
| `production/episode-001`, `episode-002` | Outreach Desk-focused drafts with `[FILL]` placeholders. Treat as Arc C material; re-tag into the new script format before use |
| `production/DAILY_SHORTS_SYSTEM.md` | Kept as the daily short routine; the REPURPOSING_PLAYBOOK governs shorts cut from episodes |
| Platform P0 schema | Workflow states and claim gate map directly (section 6) |
| Founder dossier (`ANDREW_BUILDS_CONTEXT_PACK.md`: timeline, claims, course blueprint, S01-S46, funnel, gaps, founder answers) | **FOUND 2026-11-08 (supplied by Andrew).** `COURSE_60_MINUTE_PLAN.md` v2 and `CLAIMS_REGISTER.md` derive from it. The pack stays OUTSIDE this public repo |
| Agriloop video briefs | 85 files in `agriloopmain/video-production/briefs` (dossier says 84). Agriloop-brand; reference only, pending Q4 |
