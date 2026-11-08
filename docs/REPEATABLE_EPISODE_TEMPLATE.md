# Episode Template (The Bootstrapper Experiment)

Copy to `production/episode-NNN/EPISODE_NNN_PLAN.md`. Fill every field; write `UNKNOWN - ask Andrew` rather than guessing.
Platform mapping: `episodes` (series `bootstrapper-experiment`), `ideas.episode_id`, `moments`.

| # | Field | What to write | Rule |
|---|---|---|---|
| 1 | Episode ID and title | `E###` + working title (+1 alternative) | Title makes no claim the script cannot back |
| 2 | Core premise | One sentence: what this episode is about | Must reference a real moment window (dates from `moments`) |
| 3 | Audience | Who it is for (e.g. sales people curious about building; solo founders using AI) | One primary audience |
| 4 | Hook | First 5-15 s: the real question or tension | No fake stakes; the hook's facts need claim IDs |
| 5 | Problem or question | The question the episode tries to answer | Must be answerable, or honestly left open |
| 6 | Real-world context | Where the project stands (status, dates, numbers) | Every item = claim ID + status |
| 7 | Evidence and demonstrations | List of moments, commits, deployments, docs, screen demos | Each item has a source ID and shot ID |
| 8 | Founder commentary | Points Andrew will speak to in his own words (bullets, not script) | Tagged REFLECTION / OPINION / HYPOTHESIS |
| 9 | What happened | Factual sequence of events | FACT lines only from CONFIRMED claims |
| 10 | Lessons | 1-3 lessons | Lesson = OPINION; not presented as universal fact |
| 11 | Next step | The decision made/deferred and the open question for next episode | If a plan: PLANNED claim |
| 12 | CTA | One CTA with a `cta_code` (e.g. `CTA-E001-YT`) | No promises; links tracked in `content_lead_links` |
| 13 | Repurposing opportunities | Candidate shorts per REPURPOSING_PLAYBOOK (timestamp, idea, standalone test) | Only real standalone moments |

Header block:
```
Episode: E###   Pillar (primary/secondary): P_/P_   Arc: A|B|C
Moment window: YYYY-MM-DD to YYYY-MM-DD   Target length: guide only
Trading content: yes/no (yes → disclaimer lines required)
People/partners on screen: none | list + consent_ref
Gate status: G-IDEA [ ] G-SCRIPT [ ] G-RECORD [ ] G-EDIT [ ] G-QA [ ] G-PUBLISH [ ]
```
