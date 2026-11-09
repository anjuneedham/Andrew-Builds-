# Environment Audit — Andrew Builds: From Sales to SaaS (Stage A)
Date: 2026-11-09. Nothing installed during audit.

- Ubuntu 24.04.5 LTS, x86_64, 4 CPU, 15 GiB RAM, ~30 GB free disk.
- Node v22.23.4, npm 10.9.9, pnpm 10.28.0, yarn 1.22.22, Python 3.13.18.
- FFmpeg/ffprobe 6.1.1 (libx264, libx265, aac).
- Playwright 1.63.0 + Chromium 153 (headless launch verified).
- Remotion: not installed anywhere.
- Fonts: Inter, Inter Display (all weights), JetBrains Mono, DejaVu, Carlito/Caladea, IPA; repo app ships Oswald + Inter woff2 (licence included).
- Repo `Andrew-Builds-`: Outreach Desk app; `production/` with an existing FFmpeg pipeline and a separate "Bootstrapper Experiment" Episode 001/002 (left untouched). Media under `**/exports/*` is git-ignored by repo convention.
- Repo `Content-Platform`: empty.
- Handoff initially not found; supplied by Andrew afterwards and saved as MASTER_PRODUCTION_BRIEF.md.
- 1920×1080 @ 30 fps is feasible locally (verified by the S07 proof).
