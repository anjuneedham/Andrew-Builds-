# Production Log — From Sales to SaaS

| Date | Episode | Stage | Files | Render | QA | Open issues | Approval |
|---|---|---|---|---|---|---|---|
| 2026-11-09 | — | Stage A environment audit | reports/environment-audit.md | — | — | — | n/a |
| 2026-11-09 | EP01 | Docs saved | MASTER_PRODUCTION_BRIEF.md (verbatim copy of handoff), EPISODE_01/EP01_SCRIPT.md, EP01_NARRATION_GUIDE.md | — | — | Narration est. 7:26 vs 7:00 plan | — |
| 2026-11-09 | EP01 | Stage C one-scene proof (S07) | project/{render.js,lib/,scenes/S07_value_diagram.html}; exports/previews/EP01_S07_PROOF_v001.mp4 | 450 frames, 258 s wall time | PASS (see below) | Arrows low-contrast; render speed | **Waiting for Andrew** |

## S07 proof QA (v001)
- File exists, 1,481,919 bytes. H.264, yuv420p, 1920×1080, 30/1 fps, 450 frames, 15.000 s. No audio stream (intended).
- Full decode with FFmpeg: no errors. Blackdetect (0.3 s, 5%): none.
- Frames inspected at 0.5 s, 3 s, 8 s, 12 s, 14.5 s: text readable, nothing clipped, all content inside 160 px safe margin; spelling checked.
- Fonts: Inter Display + JetBrains Mono (installed system fonts) loaded; renderer warns if not.
- Labelled "ILLUSTRATIVE DIAGRAM"; burned-in review marker (scene, planned time, narration block, "NO VOICE-OVER").
- Not checked: playback in a consumer player by a human (decode-verified only).

## Pipeline (chosen)
HTML/CSS/SVG scene per shot → Playwright/Chromium (pre-installed) sets time per frame via `window.renderAt(t)` → PNG frames piped to FFmpeg 6.1 (libx264, CRF 18). Deterministic, no new dependencies, nothing paid or external. Remotion not used (not installed; would add a framework).
Speed: ~0.57 s/frame single process → a 7:00 episode ≈ 2 h serial; plan to render scenes 4 in parallel (4 CPUs) ≈ 35–45 min, re-rendering only changed scenes.
Storage: ~1.5 MB per 15 s → ~45 MB per episode master.
| 2026-11-10 | EP01 | Andrew approved style, keep 7:00 now / extend after VO; confirmed stories | — | — | — | — | Style ✔ |
| 2026-11-10 | EP01 | Gate 3–5: S01–S28 built, rendered, captioned, QA | project/{episode.html,scenes.js,lib/*,render_all.js,stills.js}; exports/EP01_REVIEW_visual-first_v001.mp4 (+_CAPTIONED); EP01_captions_ESTIMATED_v001.srt; all EP01 docs; EP02 brief + gate; EP03–09 briefs | 28 scenes, 4 workers, ~6 min (JPEG frames) | PASS w/ known issues (EP01_QA_REPORT.md) | Captions estimated; NARR 04 too fast to read | **Waiting for Andrew review** |

Concat/caption commands (from EPISODE_01/exports):
`ls scenes/S*.mp4|sort|sed "s/^/file '/;s/$/'/">concat.txt; ffmpeg -f concat -safe 0 -i concat.txt -c copy v.mp4`
soft subs: `ffmpeg -i v.mp4 -i ../EP01_captions_ESTIMATED_v001.srt -map 0 -map 1 -c copy -c:s mov_text EP01_REVIEW_visual-first_v001.mp4`
burned: `-vf "subtitles=../EP01_captions_ESTIMATED_v001.srt:force_style='FontName=Inter,FontSize=11,PrimaryColour=&H00DAE7EF,BackColour=&H99000000,BorderStyle=4,Outline=4,Shadow=0,MarginV=10'"`
| 2026-11-10 | EP01 | Andrew approved edit; review marker removed (clean re-render, v002); offline recording script made | exports/EP01_REVIEW_visual-first_CLEAN_v002.mp4; EPISODE_01/recording/EP01_RECORDING_SCRIPT.{pdf,md} | 28 scenes, 7:00, 12,600 frames, decode OK | Top-right "illustrative" labels kept on purpose; captions still ESTIMATED | Awaiting Andrew's voice-over | Edit ✔ approved |
