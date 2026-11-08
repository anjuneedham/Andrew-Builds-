# Publish Checklist (mandatory, per post)

One checklist per post (each platform version is its own post). Every box ticked or the post stays DRAFT. Sonnet prepares; **only Andrew approves and publishes.**

## A. Approvals
- [ ] G-IDEA approved (date)  - [ ] G-SCRIPT approved; claim gate green  - [ ] G-RECORD approved  - [ ] G-EDIT approved  - [ ] G-QA approved

## B. Facts and claims
- [ ] Every FACT line cites CONFIRMED claims only; no claim downgraded since script lock
- [ ] On-screen text, title, description, thumbnail text and captions contain no claim beyond the script
- [ ] No planned feature shown as done; TradeNotes not presented as live; Agriloop not presented as a success
- [ ] No invented revenue, users, testimonials, results, ad campaigns, expertise, quotes or dates
- [ ] Banned phrases absent: "unlock your potential", "next level", "revolutionize", "passionate about"

## C. Privacy and consent
- [ ] Hide-list check run on every asset (result recorded)  - [ ] `production/tools/qa.py project` secret scan passed
- [ ] No passwords, keys, tokens, banking, payment info, notifications or emails visible (frame-by-frame scrub of screen recordings)
- [ ] No real person, partner, client or user named or shown without written consent (consent_ref recorded)
- [ ] No partner terms mentioned
- [ ] Demo data labelled

## D. Trading content (if any trading mention)
- [ ] Spoken + on-screen risk disclosure and "not financial advice" (wording: Q5, pending)  - [ ] Same in description  - [ ] No performance, P&L or win-rate claims

## E. Quality
- [ ] Audio: no clipping, consistent level, no background noise masking speech  - [ ] Video: correct resolution/orientation, no stutter, text readable on phone
- [ ] Captions present and proofread (names/terms correct)  - [ ] `qa.py video` passed

## F. Packaging
- [ ] Thumbnail (long-form) approved; text matches content  - [ ] Title/description final  - [ ] Platform formatting:
  - YouTube: 16:9, chapters, sources list, end screen  - Shorts/Reels/TikTok: 9:16, <= 60 s (or platform limit), burned-in or native captions, cover text, source-episode reference
- [ ] CTA present with cta_code; link works

## G. Final
- [ ] **Andrew's explicit approval to publish this post** (`posts.status=APPROVED`)
- [ ] After Andrew posts: URL + published time recorded (`PUBLISHED`)
