# Extracted verbatim from MASTER_PRODUCTION_BRIEF.md §10. Not in production.

## EP06 — Ship It: Hosting, Databases, Payments and Failed Deploys (7:00)

Core question: What has to happen between working code and a product people can use?

Cover:
- Code repository.
- Hosting and deployment.
- Database and authentication.
- Domains and environment variables (never expose actual secrets).
- Payment availability and regional considerations.
- TradeNotes deployment problems.
- Two-user testing and the account ownership bug.
- Learning to verify rather than assume.

Use C-021, C-022, C-023, C-025/C-040, C-037 to C-039, and C-054 where relevant. Agriloop stack details must be verified against the repository before being labelled FACT.

Include the exact trading disclaimer whenever TradeNotes or trading is mentioned.

Visuals:
- Deployment pipeline diagram.
- Database/authentication architecture illustration.
- Payment flow diagram.
- Failed deployment case-file.
- Two-user test diagram.
- Never show API keys, `.env` files, tokens, passwords, private URLs, customer details, or financial balances.
