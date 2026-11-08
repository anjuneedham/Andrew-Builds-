# Long-form to Short-form Repurposing Playbook

Extends `production/templates/SHORT_EXTRACTION_TEMPLATE.md` and `production/DAILY_SHORTS_SYSTEM.md`. A short is ONE complete idea, never a slice.
Platform: each short is an episode in series `shorts` with `parent_episode_id` = source episode.

## Target
At least 3 short-form opportunities per documentary episode **where the material supports them**. If only 1 or 2 pass the tests, make 1 or 2. Never manufacture a weak clip to hit 3.

## Step 1: find independent moments (after G-EDIT, from the approved edit + transcript)
Mark a candidate only if it is one of:
| Moment type | Example |
|---|---|
| A decision with its reason | "Why I'm not adding payments yet" |
| A visible before/after | failing test → passing; blocked gate → green |
| A mistake and the lesson | AI-generated code that was wrong and how it was caught |
| A single how-to step | how to write a build brief for Claude Code |
| An honest reflection with a clear point | demotivation with low traction |
| A surprising real number (CONFIRMED) | - |

## Step 2: standalone tests (all must pass)
1. **Hook:** a real tension or question in the first 1-2 s.  2. **One idea:** can be stated in one sentence.  3. **Payoff:** ends with the answer, result or lesson.
4. **Context:** a stranger understands it without the episode (add a 1-line setup VO or text if needed).  5. **Honesty:** every fact is in the source script with a CONFIRMED claim; no new claims.
6. **Privacy:** passes the hide list again for the vertical crop.

## Step 3: build each short
| Field | Content |
|---|---|
| Short ID | `E###-SH##` |
| Source | episode + timestamps + script lines |
| Hook (text + spoken) | |
| One idea | one sentence |
| Payoff | |
| Context line | if needed |
| Captions | always on |
| CTA | e.g. "Full episode on YouTube" + cta_code `CTA-E###-SH##-<platform>` |
| Platforms | Shorts / Reels / TikTok (same cut; adjust cover, caption, hashtags) |
| Trading disclaimer | if applicable |

Build with `production/tools/produce.py short <id>`; QA with `qa.py video --kind short`.

## Step 4: text and lesson posts
- Supporting text post: the episode's question + what happened + link (YouTube community, IG caption).
- Lesson post / carousel: one lesson from the episode as 3-6 steps (OPINION/method, no new facts).
Same publish checklist applies.

## Step 5: track
Each short has its own post rows and metrics; review which moment types work (METRICS_REVIEW_PLAYBOOK).
