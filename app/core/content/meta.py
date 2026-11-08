"""Single source of truth for the content platform's enumerations and rule descriptions.

The database CHECK constraints are authoritative. tests/unit/test_content_p0.py fails if anything here drifts from them,
so the UI can safely build its dropdowns from this module (served by GET /api/content/meta)."""

ROLE = "content_app"

TABLES = ("series", "sources", "moments", "claims", "claim_sources", "episodes", "ideas", "scripts", "script_lines", "line_claims",
          "shots", "assets", "posts", "metrics", "growth_log", "content_lead_links", "course_plan", "course_modules", "hide_list")

PROJECTS = ("agriloop", "tradenotes", "yardscale", "andrew-builds")
PLATFORMS = ("youtube", "instagram", "tiktok")

# (table, column) -> allowed values, exactly as the CHECK constraints list them.
ENUMS = {
    ("episodes", "status"): ("IDEA", "SCRIPTING", "READY_TO_RECORD", "RECORDED", "EDITING", "QA", "READY_TO_PUBLISH", "PUBLISHED", "ARCHIVED"),
    ("ideas", "status"): ("BACKLOG", "SCHEDULED", "DROPPED"),
    ("scripts", "status"): ("DRAFT", "IN_REVIEW", "READY_TO_RECORD", "LOCKED"),
    ("script_lines", "kind"): ("FACT", "OPINION", "REFLECTION", "QUESTION", "HYPOTHESIS", "DIRECTION", "CTA", "DISCLAIMER"),
    ("claims", "status"): ("CONFIRMED", "PARTIALLY_CONFIRMED", "PLANNED", "UNKNOWN"),
    ("claims", "project"): PROJECTS,
    ("moments", "project"): PROJECTS,
    ("moments", "kind"): ("commit", "deployment", "failure", "decision", "milestone"),
    ("sources", "kind"): ("commit", "deployment", "document", "screenshot", "founder_answer", "url", "record"),
    ("shots", "status"): ("PLANNED", "CAPTURED", "REJECTED"),
    ("assets", "kind"): ("raw", "voiceover", "screen", "graphic", "thumbnail", "caption", "export"),
    ("assets", "hide_list_result"): ("PASSED", "FAILED", "MANUAL_OK"),
    ("posts", "platform"): PLATFORMS,
    ("posts", "status"): ("DRAFT", "APPROVED", "PUBLISHED"),
    ("growth_log", "platform"): PLATFORMS,
    ("course_plan", "status"): ("DRAFT", "READY"),
    ("hide_list", "category"): ("person", "partner", "secret", "financial", "other"),
}

# Line kinds that make a factual assertion and therefore need CONFIRMED claims. Everything else is clearly marked as not-a-fact.
FACTUAL_KINDS = ("FACT",)
NON_FACTUAL_KINDS = tuple(k for k in ENUMS[("script_lines", "kind")] if k not in FACTUAL_KINDS)

COURSE_TOTAL_SECONDS = 3600

# Shown on the Content page. `where` says which layer enforces it; `phase` says when its screen exists.
RULES = (
    {"id": "claim_gate", "title": "Claim gate",
     "detail": "A script becomes READY_TO_RECORD only when every FACT line cites at least one claim and every cited claim is CONFIRMED. "
               "PARTIALLY_CONFIRMED, PLANNED and UNKNOWN claims block it.", "where": "database trigger", "phase": "P2"},
    {"id": "script_lock", "title": "Approved scripts are frozen",
     "detail": "Lines, claim links and body of a READY_TO_RECORD or LOCKED script cannot change. LOCKED is final.", "where": "database trigger", "phase": "P2"},
    {"id": "claim_evidence", "title": "Claims need evidence",
     "detail": "CONFIRMED and PARTIALLY_CONFIRMED claims need at least one source. PARTIALLY_CONFIRMED must state its limitations. "
               "Rewording a verified claim resets it to UNKNOWN.", "where": "database trigger + CHECK", "phase": "P2"},
    {"id": "claim_downgrade", "title": "Downgraded claim pulls scripts back",
     "detail": "If a claim stops being CONFIRMED, READY_TO_RECORD scripts that cite it return to IN_REVIEW (audited).", "where": "database trigger", "phase": "P2"},
    {"id": "episode_gate", "title": "Episode needs a ready script",
     "detail": "An episode can become READY_TO_RECORD only when one of its scripts is READY_TO_RECORD.", "where": "database trigger", "phase": "P1"},
    {"id": "metrics_append_only", "title": "Metrics are append-only",
     "detail": "Numbers are entered by hand and never edited; a correction is a new row.", "where": "trigger + privileges", "phase": "P5"},
    {"id": "course_60", "title": "Course is exactly 60:00",
     "detail": "The course plan can be READY only when its modules total exactly 3600 seconds; READY plans are frozen.", "where": "database trigger", "phase": "P9"},
    {"id": "rls", "title": "Row-level security",
     "detail": "Enabled and forced on every content table; only the content_app role has a policy. Any other database role sees nothing.",
     "where": "database", "phase": "P0"},
)

# Honest list of what does not exist yet. The UI shows it so a rendered screen is never mistaken for a finished feature.
NOT_BUILT = (
    ("P1", "Content calendar, idea backlog, episode management"),
    ("P2", "Script editor, claims register, claim checker screen"),
    ("P3", "Shot lists and recording checklist"),
    ("P4", "Asset register"),
    ("P5", "Publishing log, publish gate, manual metrics"),
    ("P6", "Moments library"),
    ("P7", "Growth log"),
    ("P8", "Lead and CTA tracker"),
    ("P9", "Course planner"),
    ("P10", "Import of existing production files, founder-story-dossier, and deployment"),
)
