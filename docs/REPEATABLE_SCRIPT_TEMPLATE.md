# Script Template with Evidence Tags

Applies to episodes, course lessons and shorts. Maps 1:1 to `scripts` + `script_lines` + `line_claims` in the platform.
Do not write finished scripts until G-IDEA is approved and claims are collected.

## 1. Line format
One spoken sentence per line:
```
L### | KIND | text | claims | shot
```
Example (illustrative only, not a real script):
```
L001 | FACT        | Agriloop is in beta.                          | C-012 [CONFIRMED]            | S01
L002 | REFLECTION  | Honestly, I lost motivation for a few weeks.   | -                            | S02
L003 | HYPOTHESIS  | I think the problem is reaching buyers, not farmers. | C-019 [UNKNOWN] context only | S03
L004 | QUESTION    | Should I keep going after 30 November?         | -                            | S03
L005 | DIRECTION   | (screen: claim gate turns green)              | -                            | S04
L006 | DISCLAIMER  | This is not financial advice. ...             | -                            | GFX
L007 | CTA         | The full build is in the next episode.         | -                            | END
```

## 2. Line kinds (platform `script_lines.kind`)
| Kind | Use | Claim needed |
|---|---|---|
| FACT | Any statement of fact: dates, numbers, status, what happened, what exists | **>= 1, all CONFIRMED** (DB-enforced) |
| OPINION | Andrew's view ("I think sales is the hard part") | No |
| REFLECTION | Personal feeling or memory | No (but must be Andrew's own, approved) |
| HYPOTHESIS | Something being tested | Optional; may cite PLANNED/UNKNOWN as context |
| QUESTION | Open question | No |
| DIRECTION | On-screen action, demonstration, b-roll note (not spoken) | No; must reference a shot |
| CTA | Call to action | No; must carry cta_code |
| DISCLAIMER | Risk / not financial advice / demo data label | No |

"Demonstration" from the brief = DIRECTION line + shot ID; anything spoken during it is still tagged by kind.
Lines default to FACT, so an untagged line is treated as a fact and blocks the gate.

## 3. Claim statuses
| Status | Meaning | May back a FACT line? | How it may be spoken |
|---|---|---|---|
| CONFIRMED | Source attached (commit, deployment, document, screenshot, founder_answer, url, record) | Yes | As fact |
| PARTIALLY_CONFIRMED | Some evidence; `limitations` field required | **No** (Q7 strict) | As REFLECTION/HYPOTHESIS, or rewrite to the narrower confirmed part as a new CONFIRMED claim |
| PLANNED | Intended, not done | No | "I plan to...", "next I'm building..." |
| UNKNOWN | Not verified | No | Only as a QUESTION, or removed |

## 4. How evidence appears
- In the script document: claim ID + status in the claims column; source shown in the evidence appendix (claim → source kind + reference; private sources marked and never exported).
- On screen: where a number or status is shown, the shot uses the source itself (commit, dashboard, document) or a graphic with the source noted in the shot list.
- In the video description: "Sources" list for public sources only.

## 5. Claim checker (how unsupported statements are stopped)
1. **DB gate (built, P0):** `scripts.status → READY_TO_RECORD` fails unless every FACT line has >= 1 claim and all are CONFIRMED. Error prefix `CONTENT_RULE:`.
2. **Integrity triggers (built):** rewording a verified claim resets it to UNKNOWN; downgrading a claim sends READY scripts back to IN_REVIEW; READY/LOCKED scripts are frozen.
3. **App checks (NOT built, P2):** banned phrases, hide-list terms, trading disclaimer presence, number/date detector that flags digits in non-FACT lines. Until built, Sonnet runs these manually with the PUBLISH_CHECKLIST and `production/tools/qa.py project`.
4. **Human gate:** G-SCRIPT is Andrew's explicit approval after the checker is green.

## 6. Script document layout
```
# E### Script vN (status)
Header: episode, pillar, target length, trading yes/no, gate status
Lines table (section 1 format), grouped by episode-template section (Hook, Context, ...)
Claims appendix: C-### | statement | status | source kind/ref | limitations
Open items: UNKNOWN claims to ask Andrew; [FILL]/[RECORD] placeholders (existing production convention)
Checks: banned phrases 0 | hide list 0 | disclaimers present (if trading) | FACT lines all CONFIRMED
```
Existing convention kept: `[FILL: ...]` = fact only Andrew knows; `[RECORD: ...]` = moment in his own words, only if it happened.
