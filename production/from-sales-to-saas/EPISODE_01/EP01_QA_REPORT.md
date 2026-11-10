# EP01 QA Report — visual-first review edit v001 (10 Nov 2026)

**Status: REVIEW EDIT, NOT FINAL.** No voice-over yet, by design. Not published, not uploaded.

## Exports (in EPISODE_01/exports/, git-ignored by repo convention)
| File | Size | Video | Duration | Captions |
|---|---|---|---|---|
| EP01_REVIEW_visual-first_v001.mp4 | 27.3 MB | H.264 yuv420p 1920×1080 30 fps, 12,600 frames | 7:00.000 | Soft track (mov_text, switchable, 117 cues) |
| EP01_REVIEW_visual-first_CAPTIONED_v001.mp4 | ~32 MB | same | 7:00.000 | Burned in |
Per-scene sources: exports/scenes/S01–S28.mp4 (re-render any one with `render_all.js … Sxx`).

## Checks run
| Check | Result |
|---|---|
| Runtime, resolution, aspect ratio, fps (ffprobe) | PASS: 420.0 s, 1920×1080 16:9, 30/1 |
| Full decode, both files (ffmpeg -f null) | PASS, no errors |
| Black segments ≥0.5 s (blackdetect) | PASS, none |
| Audio | None present (intended). No music, no SFX, no voice of any kind, synthetic or otherwise. |
| Layout: one still per scene (28) + 17 caption-frame samples, inspected by eye | PASS after fixes: S01 farmer moved away from the headline; burned captions reduced and lowered (they first covered S01/S05/S09/S17/S27 text) |
| Spelling of on-screen text | Checked in stills; no errors found |
| Disclaimer (S11) | Exact text from brief §5, unshortened (copied from the same source string) |
| Fabricated evidence | None: no screenshots, analytics, logos, real UI. All illustrative visuals labelled top-right |
| Claims on screen | C-001/002 (S09, S10), C-004 (S12), C-007 (S19), C-008 (S02–S03, S18), C-009 (S23), C-028 (S17); stories = Andrew's confirmed recollection |
| Private data / secrets | None in frames |
| Unlicensed media | None (all original; fonts OFL) |

## Not checked
- Playback in a consumer player by a person from start to end (machine decode only). **Please watch it once end to end.**
- Every one of the 12,600 frames by eye (sampled ~45 frames + per-scene stills).

## Known issues / open
1. **Captions are ESTIMATED.** They are timed by word count within each narration block's scene window. Because the script runs ~7:26 against a 7:00 plan (approved: keep 7:00 now, extend after), block pacing is uneven: NARR 04 (S14–S17) flashes at ~366 wpm and is too fast to read, while NARR 06 is slow. All captions get re-timed to your real recording.
2. The top-left review marker must be removed for the final master.
3. S27 roadmap uses shortened episode titles for EP04/EP06/EP08/EP09 so they fit (e.g. "Ship It", "Keep Going or Quit?").
4. S19 shows "Development started" (C-007) rather than the brief's "Idea opened".
