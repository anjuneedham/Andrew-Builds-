# Shot List Template

Supersedes `production/templates/SHOT_LIST_TEMPLATE.md` for new episodes (that file stays for episodes 001-002). Maps to `shots` (`code`, `description`, `location`, `device`, `status`, `checklist`).
The dossier's S01-S46 list was not found; when supplied, import it using these columns.

## Columns
| Field | Content |
|---|---|
| Shot ID | `S##` within episode; full ref `E###-S##` |
| Script ref | Line IDs `L###-L###` |
| Purpose | What the viewer must understand from this shot |
| Visual description | What is on screen |
| Type | SCREEN (tablet / desktop) or CAMERA (face / desk / b-roll) |
| Tablet capture instructions | see rules below |
| On-screen text | exact text, max 7 words |
| Evidence source | claim ID / source ID shown |
| Privacy risks | names, emails, phone numbers, keys, payments, partner info, notifications |
| Status | PLANNED / CAPTURED / REJECTED (+ reason) |

Row:
```
| E###-S## | L001-L004 | ... | ... | SCREEN-TAB | ... | "..." | C-012 | notifications, lead names | PLANNED |
```

## Tablet capture rules (Galaxy Tab S9 FE+)
1. Do Not Disturb on; close all apps except the one recorded.
2. Use demo data where possible (`production/tools/reset_demo_env.sh`), and label it "Demo data" on screen.
3. Built-in screen recorder, media sounds only, no mic (voice recorded separately) unless it is a live talk-through.
4. Landscape 2560x1600 for long-form; portrait for shots meant only for shorts. Record 3 s still before and after.
5. Browser: hide bookmarks bar, signed-out profile or clean profile, no autofill suggestions.
6. Never record password entry, TOTP, `.env`, Vercel/Neon env pages, banking or payment screens.
7. After recording: scrub the file for privacy risks before renaming it into the asset register.

## Recording-mode checklist (per shot, stored in `shots.checklist`)
- [ ] DND on  - [ ] demo data / redaction confirmed  - [ ] framing and orientation  - [ ] audio level checked (camera shots)  - [ ] take reviewed  - [ ] asset registered
