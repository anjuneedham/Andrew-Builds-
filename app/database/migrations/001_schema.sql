-- Outreach Desk schema (PostgreSQL). One owner, no agents, no payments.

CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);

-- Owner authentication: exactly one credentials row (password + TOTP).
CREATE TABLE owner_credentials (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  password_hash TEXT NOT NULL,
  totp_secret TEXT NOT NULL,
  totp_last_step BIGINT NOT NULL DEFAULT 0,      -- replay protection: a code works once
  recovery_hashes TEXT NOT NULL DEFAULT '[]',    -- sha256 of single-use recovery codes
  setup_complete BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TEXT NOT NULL
);
CREATE TABLE sessions (
  token_hash TEXT PRIMARY KEY,                   -- sha256 of the bearer token; the token itself is never stored
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  revoked BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE TABLE auth_attempts (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  kind TEXT NOT NULL CHECK (kind IN ('login','setup')),
  ok BOOLEAN NOT NULL,
  at TEXT NOT NULL
);
CREATE INDEX auth_attempts_recent ON auth_attempts (kind, ok, at);

-- Security/audit log (logins, logouts). Append-only.
CREATE TABLE audit_events (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, at TEXT NOT NULL, actor TEXT NOT NULL,
  action TEXT NOT NULL, target TEXT, detail TEXT
);
CREATE FUNCTION audit_events_immutable() RETURNS trigger AS $$
BEGIN RAISE EXCEPTION 'audit_events is append-only'; END; $$ LANGUAGE plpgsql;
CREATE TRIGGER audit_no_update BEFORE UPDATE OR DELETE ON audit_events
  FOR EACH ROW EXECUTE FUNCTION audit_events_immutable();
CREATE TRIGGER audit_no_truncate BEFORE TRUNCATE ON audit_events
  FOR EACH STATEMENT EXECUTE FUNCTION audit_events_immutable();

-- Prospects (table name kept as `leads`).
CREATE TABLE leads (
  id TEXT PRIMARY KEY,
  name TEXT, business TEXT, email TEXT, phone TEXT, notes TEXT,
  industry TEXT, location TEXT, website TEXT,
  contact_other TEXT,                     -- handle / WhatsApp / other way to reach them
  source_channel TEXT,                    -- where the prospect came from
  offer TEXT, research_notes TEXT,
  qualification TEXT NOT NULL DEFAULT 'unqualified' CHECK (qualification IN ('unqualified','qualified','maybe','not_qualified')),
  stage TEXT NOT NULL DEFAULT 'identified',
  outcome TEXT,
  deal_value NUMERIC(14,2),
  revenue_won NUMERIC(14,2),              -- OWNER-RECORDED; this app never verifies payments
  currency TEXT NOT NULL DEFAULT 'USD',
  last_contact_at TEXT,
  next_followup_at TEXT,                  -- YYYY-MM-DD, derived from open follow-up tasks
  playbook_run_id TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT
);
CREATE UNIQUE INDEX leads_email ON leads (lower(email)) WHERE email IS NOT NULL AND email <> '';
CREATE INDEX leads_stage ON leads (stage);

-- Every business event. Append-only: history is never rewritten; corrections are new events.
-- at = when it was recorded (immutable). occurred_at = when it actually happened (owner-supplied, may be earlier).
CREATE TABLE activity_events (
  id BIGSERIAL PRIMARY KEY,
  at TEXT NOT NULL,
  occurred_at TEXT NOT NULL,
  lead_id TEXT,                           -- deliberately no FK: history outlives a deleted prospect
  kind TEXT NOT NULL,
  summary TEXT NOT NULL,
  detail TEXT NOT NULL DEFAULT '{}',      -- JSON
  task_id TEXT,
  run_id TEXT,
  actor TEXT NOT NULL DEFAULT 'owner'
);
CREATE INDEX activity_lead ON activity_events (lead_id, id);
CREATE INDEX activity_at ON activity_events (at);
CREATE FUNCTION activity_events_immutable() RETURNS trigger AS $$
BEGIN RAISE EXCEPTION 'activity_events is append-only'; END; $$ LANGUAGE plpgsql;
CREATE TRIGGER activity_no_update BEFORE UPDATE OR DELETE ON activity_events
  FOR EACH ROW EXECUTE FUNCTION activity_events_immutable();
CREATE TRIGGER activity_no_truncate BEFORE TRUNCATE ON activity_events
  FOR EACH STATEMENT EXECUTE FUNCTION activity_events_immutable();

CREATE TABLE sales_tasks (
  id TEXT PRIMARY KEY,
  lead_id TEXT,
  title TEXT NOT NULL,
  detail TEXT,
  kind TEXT NOT NULL DEFAULT 'other',
  priority INTEGER NOT NULL DEFAULT 2 CHECK (priority IN (1,2,3)),   -- 1 high, 2 normal, 3 low
  due_date TEXT,                          -- YYYY-MM-DD
  status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','done','skipped')),
  playbook_id TEXT, run_id TEXT, step_id TEXT, outcome TEXT,
  created_at TEXT NOT NULL,
  completed_at TEXT
);
CREATE INDEX sales_tasks_open ON sales_tasks (status, due_date);
CREATE INDEX sales_tasks_lead ON sales_tasks (lead_id);

CREATE TABLE playbooks (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  builtin_slug TEXT UNIQUE,               -- set for shipped playbooks; NULL for custom/duplicates
  parent_id TEXT,
  objective TEXT NOT NULL DEFAULT '',
  intended_user TEXT NOT NULL DEFAULT '',
  when_to_use TEXT NOT NULL DEFAULT '',
  prerequisites TEXT NOT NULL DEFAULT '[]',
  steps TEXT NOT NULL DEFAULT '[]',
  recommended_actions TEXT NOT NULL DEFAULT '[]',
  example_messages TEXT NOT NULL DEFAULT '[]',
  expected_outcome TEXT NOT NULL DEFAULT '',
  completion_criteria TEXT NOT NULL DEFAULT '',
  common_mistakes TEXT NOT NULL DEFAULT '[]',
  next_recommended TEXT NOT NULL DEFAULT '',
  version INTEGER NOT NULL DEFAULT 1,
  archived BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

-- A run snapshots the steps it started with, so later edits to a playbook never rewrite past executions.
CREATE TABLE playbook_runs (
  id TEXT PRIMARY KEY,
  playbook_id TEXT NOT NULL,
  playbook_name TEXT NOT NULL,
  playbook_version INTEGER NOT NULL,
  lead_id TEXT,
  steps TEXT NOT NULL,
  progress TEXT NOT NULL DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'in_progress' CHECK (status IN ('in_progress','completed','abandoned')),
  started_at TEXT NOT NULL,
  completed_at TEXT,
  outcome_note TEXT
);
CREATE INDEX playbook_runs_lead ON playbook_runs (lead_id);
CREATE INDEX playbook_runs_pb ON playbook_runs (playbook_id);
