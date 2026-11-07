# Andrew Builds

The home base for the **Bootstrapper Experiment**: a business built through outreach, the software that runs it, and the videos that document it.

```
app/          Outreach Desk: the sales execution app (Today, Pipeline, Playbooks, Insights). Python + Postgres, no build step.
production/   The video production system: episodes, scripts, shot lists, FFmpeg pipeline, QA, templates.
docs/         Audit, architecture, test report and the story of how this repo came to be (docs/HANDOVER.md).
```

## Outreach Desk (app/)
One owner, one login (password + authenticator app). It answers: what should I do today, who do I contact, what happened, what is working.
It records what you do; it never sends messages and has no AI. 12 editable playbooks, a pipeline, a tamper-proof activity timeline, and honest reports (counts first; no percentages from small samples).

### Run it locally
```bash
cd app
pip install -r requirements.txt
cp .env.example .env.local        # set DATABASE_URL (any postgresql:// URL; a free Neon database works) and OWNER_SETUP_TOKEN (20+ characters)
python scripts/run_local.py       # http://127.0.0.1:8080 : create your password + authenticator on first visit
```

### Test it
```bash
cd app
TEST_DATABASE_URL=postgresql://... python -m unittest discover -s tests -t .      # use a THROWAWAY database
BASE=http://127.0.0.1:8080 TOKEN=<session token> OUT=/tmp/e2e node tests/e2e/journey.js   # browser journey (needs Playwright)
```

### Deploy (Vercel + Neon)
1. Create a Neon project; copy its connection string.
2. Import this repo in Vercel; set **Root Directory** to `app`.
3. Environment variables: `DATABASE_URL`, `OWNER_SETUP_TOKEN` (first-time setup only; remove it afterwards), optional `SALES_TIMEZONE`.
4. Deploy, open the site, complete setup. The schema is created automatically on first start.

## Production system (production/)
See `production/README.md`. Text, config and scripts are tracked; large media is git-ignored and regenerated with the tools.

## Rules this repo keeps
No outreach, publishing or deployment without the owner saying so. No revenue is stated unless verified. Demo data is always labelled. No secrets in git (`production/tools/qa.py project` scans for them).
