# From Sales to SaaS: 60-Minute Course Plan

Status: **PROPOSED, awaiting approval (G-IDEA for the course).** Not scripted. Total: **60:00 exactly (3600 s)**.
Starting point: the course blueprint in `founder-story-dossier/` was **not found**; this plan is built from the founder story in the brief and the repos. Reconcile with the blueprint when it is supplied.
Platform: the `course_plan` row "From Sales to SaaS" exists (seed). `course_modules.duration_s` values below sum to 3600, so the plan can be set READY (DB rule: READY only at exactly 3600 s, then frozen).

## Structure
| # | Section / Lesson | Dur. | Start-End | Learning objective (learner can...) | Demonstration | Screen recordings required | Evidence required (claims) |
|---|---|---|---|---|---|---|---|
| **1** | **Start here** | **4:00** | 0:00-4:00 | | | | |
| 1.1 | What this course is and is not | 2:00 | 0:00-2:00 | state what they will be able to do and the limits (no success guarantees, no paid-ads method) | none (talking head) | - | course scope; Andrew has not run paid SaaS ads (CONFIRMED by founder answer) |
| 1.2 | Where I am right now | 2:00 | 2:00-4:00 | describe the honest starting point: two products, one beta with little traction, one just started | Agriloop beta and TradeNotes repo on screen | REC-C01 Agriloop beta home (demo data); REC-C02 TradeNotes repo/commit list | Agriloop beta status; traction level; TradeNotes start date |
| **2** | **What sales taught me about products** | **12:00** | 4:00-16:00 | | | | |
| 2.1 | Customer service as problem discovery | 4:00 | 4:00-8:00 | turn complaints/questions into a written problem statement | writing a problem statement from 3 real (anonymised) customer questions | REC-C03 notes doc being written on tablet | customer-service career (dates/employers only if Andrew approves naming) |
| 2.2 | Outreach as validation | 4:00 | 8:00-12:00 | run a small outreach test and log replies honestly | Outreach Desk: create lead, log message, log reply/no reply (demo data) | REC-C04 Outreach Desk pipeline (demo) | Outreach Desk exists and is used; any reply counts only if CONFIRMED |
| 2.3 | Agency lessons: scoping and small teams | 4:00 | 12:00-16:00 | write a one-page scope with must/should/won't | one-page scope for a small feature | REC-C05 scope doc | YardScale Digital services and team size |
| **3** | **Building with Claude Code** | **18:00** | 16:00-34:00 | | | | |
| 3.1 | The role split: founder vs AI | 3:00 | 16:00-19:00 | define what they decide and what they delegate to Claude Code | split diagram | GFX-C01 role-split graphic | Andrew's role (outreach, sales, direction); Claude Code writes much of the code |
| 3.2 | From problem to spec | 5:00 | 19:00-24:00 | write a build brief Claude Code can act on (goal, constraints, acceptance tests, stop condition) | turning the 2.3 scope into a brief | REC-C06 writing the brief | - (method, OPINION/DEMONSTRATION lines) |
| 3.3 | A real build session | 6:00 | 24:00-30:00 | run a session: brief, plan, change, tests, review diff, commit | real Claude Code session on TradeNotes or Outreach Desk | REC-C07 full session (cut down), REC-C08 test run, REC-C09 diff review | commit hash(es) of the session |
| 3.4 | Where AI development fails | 4:00 | 30:00-34:00 | spot the common failures (unverified claims, untested paths, scope creep) and check for them | a real failing test or wrong assumption caught in review | REC-C10 failing test → fix | a real failure record (commit/test log) |
| **4** | **Validation: the Agriloop case** | **12:00** | 34:00-46:00 | | | | |
| 4.1 | A personal problem: selling pigs | 3:00 | 34:00-37:00 | describe a founder-problem origin and its bias risk | farm/phone context (no buyer names) | CAM-C01 farm or desk b-roll | the pig-selling difficulty (founder answer) |
| 4.2 | Beta and what traction actually looked like | 4:00 | 37:00-41:00 | read real usage numbers without spin | Agriloop beta walkthrough + usage numbers | REC-C11 Agriloop beta (demo data), GFX-C02 usage numbers | every number CONFIRMED with source; if none, say "very little traction" as REFLECTION |
| 4.3 | Making the 30 November decision | 5:00 | 41:00-46:00 | apply a decision framework (evidence, cost to continue, alternatives, kill criteria) | Andrew filling the framework for Agriloop | REC-C12 decision doc | decision date; the decision itself only after it is made (until then, framework only) |
| **5** | **TradeNotes: an experiment, not a promise** | **8:00** | 46:00-54:00 | | | | |
| 5.1 | Why a trading journal | 3:00 | 46:00-49:00 | explain journaling/backtesting as a discipline hypothesis | Andrew's journaling process (no P&L) | REC-C13 a journal entry template | Andrew's results are not where he wants (REFLECTION); disclaimer line |
| 5.2 | Scoping an MVP with AI | 5:00 | 49:00-54:00 | cut a product to its smallest testable version | TradeNotes MVP scope + first commits | REC-C14 TradeNotes scope + repo | TradeNotes status (not live); features as PLANNED |
| **6** | **Documenting the journey** | **4:00** | 54:00-58:00 | | | | |
| 6.1 | An evidence-first content system | 4:00 | 54:00-58:00 | tag script lines to claims and run a publish checklist | the content platform claim gate (blocked then passing) | REC-C15 claim gate in the platform | platform P0 exists (PLATFORM_STATUS.md) |
| **7** | **Close** | **2:00** | 58:00-60:00 | leave with one next action | none | - | - |
| | **TOTAL** | **60:00** | | | | | |

Check: 4 + 12 + 18 + 12 + 8 + 4 + 2 = 60 min. Lessons: 2+4+4+4+3+5+6+4+3+4+5+3+5+4+2 = 60 min.

## Transitions (one line each, written later)
1→2 "Before building, what did selling teach me?" · 2→3 "Knowing the problem, how do I build without being a developer?" · 3→4 "Building is the easy part; does anyone want it?" · 4→5 "Same method, a different problem: my own trading discipline." · 5→6 "How I record this without lying to myself or you." · 6→7 next action.

## Final takeaway (to be worded by Andrew)
Sales and customer-service skills are product skills: find the problem, test it with real people, let AI build the smallest version, and judge it on evidence, including when the evidence says stop.

## Disclaimers
Section 5 and any trading mention: risk disclosure + "not financial advice" (wording pending Q5). Course makes no income or results claims.
