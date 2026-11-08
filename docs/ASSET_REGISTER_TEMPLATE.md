# Asset Register Template

Maps to `assets` (`episode_id`, `kind`, `path`, `hide_list_checked_at`, `hide_list_result`, `consent_ref`). Paths are relative to the repo (`production/...`); large media is git-ignored (existing rule).

## Naming convention
```
<EPISODE>_<TYPE>_<SHOT-or-PART>_<DESC>_v<NN>.<ext>
E004_SCR_S03_claim-gate_v01.mp4
E004_VO_P02_context_v02.wav
C3.3_SCR_S01_build-session_v01.mp4     (course lesson)
E004_SHT_SH02_tiktok_v01.mp4          (short export)
```
- EPISODE: `E###` (documentary), `C<section>.<lesson>` (course), `SH-YYYYMMDD-N` (standalone daily short)
- Lowercase-kebab description, no names of people, no spaces. Versions start at v01; never overwrite, always increment. "FINAL" is never in a filename; final = the version marked approved in the register.

## Types
| Code | Type | Folder in `production/episode-NNN/` | Platform `assets.kind` |
|---|---|---|---|
| SCR | Raw screen recording | `screen-recordings/` | screen |
| VO | Voice recording | `voiceover/` | voiceover |
| CAM | Camera footage | `raw-footage/` | raw |
| EDT | Edited video (long-form) | `exports/` | export |
| THM | Thumbnail | `thumbnails/` | thumbnail |
| GFX | Graphic | `graphics/` | graphic |
| CAP | Captions (.srt/.vtt) | `captions/` | caption |
| SHT | Short-form export | `exports/shorts/` | export (+ parent episode link) |
| DOC | Supporting document | `research/` | raw (kind gap, see note) |

Note: `assets.kind` has no camera or document value; CAM and DOC use `raw` with the type code in the filename. Proposal (not applied): add `camera`, `document`, `short_export` kinds in a later migration (requires approval).

## Register table
| Asset ID | File | Type | Episode | Shot / script ref | Version | Status (DRAFT/APPROVED/REJECTED) | Hide-list result + date | Consent ref | People on screen | Notes |
|---|---|---|---|---|---|---|---|---|---|---|

Rules: every asset used in an export must be APPROVED and hide-list PASSED or MANUAL_OK; any person shown needs a consent_ref (written consent, stored privately).
