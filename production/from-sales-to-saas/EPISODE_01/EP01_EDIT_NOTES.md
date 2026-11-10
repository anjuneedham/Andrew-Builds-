# EP01 Edit Notes

## How to rebuild
```bash
cd production/from-sales-to-saas/EPISODE_01/project
node stills.js <dir> 0.8                     # one still per scene, layout check (~10 s)
node render_all.js ../exports/scenes 4       # all scenes, 4 in parallel
node render_all.js ../exports/scenes 4 S07   # re-render one scene only
# then concat + captions: see ../../logs/production-log.md (commands recorded there)
```
Edit text or timing in `scenes.js` (each scene: `s`/`e` seconds, `html`, `data-a="type start duration"`).

## After Andrew records (approved approach: extend to the voice)
1. Put `EP01_NARR_01.wav` … `_06.wav` in `EPISODE_01/assets/audio/`.
2. Measure each block's length; stretch the scenes in that block by changing their `s`/`e` (and animation starts if needed).
3. Re-time captions to the real audio (from the recording/transcript, not the estimate).
4. Mix voice; re-render changed scenes only; re-run QA; export a final review version.
5. Remove the review marker (top-left) for the final master.

## Review-edit conventions
- Top-left marker: scene · planned time · narration block · "REVIEW EDIT — NO VOICE-OVER".
- Top-right label: what kind of visual it is (illustration / conceptual / required disclaimer).
- Fades: 0.4 s in, 0.45 s out per scene (dip to dark). S01 starts on picture (no logo, no fade).
