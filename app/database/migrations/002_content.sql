-- Andrew Builds Content Operating Platform, P0 foundation (PostgreSQL).
-- ADDITIVE ONLY: touches no existing table. Re-runnable: every statement is idempotent.
-- Design: docs/PLATFORM_ARCHITECTURE.md. Deviations from it are listed in docs/PLATFORM_DECISIONS.md (D8-D12).
--
-- Rules enforced HERE (so a bug or a direct API call cannot bypass them):
--   * claim gate     a script becomes READY_TO_RECORD only if every FACT line cites >=1 claim and every cited claim is CONFIRMED
--   * script lock    READY_TO_RECORD / LOCKED scripts cannot have lines, claim links or body edited; LOCKED is final
--   * evidence       CONFIRMED / PARTIALLY_CONFIRMED claims need >=1 source; PARTIALLY_CONFIRMED must state its limitations
--   * metrics        append-only (corrections are new rows)
--   * course         a READY course plan totals exactly 3600 s (60:00) and is frozen until set back to DRAFT
--   * RLS            enabled AND forced on every table; only role content_app has a policy; everyone else sees nothing

-- ---------------------------------------------------------------------------------------------------------------------
-- 0. The single application role. NOLOGIN: the app connects as usual and does SET LOCAL ROLE content_app per request.
-- ---------------------------------------------------------------------------------------------------------------------
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'content_app') THEN
    CREATE ROLE content_app NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
  END IF;
END $$;
-- The connecting role must be able to SET ROLE content_app, but must NOT inherit its privileges: a policy "TO content_app" applies
-- to every role that inherits content_app, which would let the connecting role bypass the default-deny. PostgreSQL 16 can express
-- that (INHERIT FALSE, SET TRUE). On older servers membership always inherits, so only OTHER roles are denied (see docs).
DO $$ BEGIN
  IF current_setting('server_version_num')::int >= 160000 THEN
    EXECUTE 'GRANT content_app TO CURRENT_USER WITH INHERIT FALSE, SET TRUE';
  ELSE
    EXECUTE 'GRANT content_app TO CURRENT_USER';
  END IF;
END $$;

CREATE OR REPLACE FUNCTION content_touch() RETURNS trigger AS $$
BEGIN NEW.updated_at := now(); RETURN NEW; END; $$ LANGUAGE plpgsql;

-- ---------------------------------------------------------------------------------------------------------------------
-- 1. Tables
-- ---------------------------------------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS series (
  id BIGSERIAL PRIMARY KEY,
  slug TEXT NOT NULL UNIQUE CHECK (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  title TEXT NOT NULL CHECK (length(btrim(title)) > 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Evidence for claims. private = never leaves the app in an export (default: private until the owner says otherwise).
CREATE TABLE IF NOT EXISTS sources (
  id BIGSERIAL PRIMARY KEY,
  kind TEXT NOT NULL CHECK (kind IN ('commit','deployment','document','screenshot','founder_answer','url','record')),
  reference TEXT NOT NULL CHECK (length(btrim(reference)) > 0),
  captured_at TIMESTAMPTZ,
  private BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Real business moments. A moment must point at a source: no source, no moment.
CREATE TABLE IF NOT EXISTS moments (
  id BIGSERIAL PRIMARY KEY,
  occurred_at TIMESTAMPTZ NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('commit','deployment','failure','decision','milestone')),
  project TEXT NOT NULL CHECK (project IN ('agriloop','tradenotes','yardscale','andrew-builds')),
  summary TEXT NOT NULL CHECK (length(btrim(summary)) > 0),
  source_id BIGINT NOT NULL REFERENCES sources(id) ON DELETE RESTRICT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE SEQUENCE IF NOT EXISTS claims_code_seq;
CREATE TABLE IF NOT EXISTS claims (
  id BIGSERIAL PRIMARY KEY,
  code TEXT NOT NULL UNIQUE DEFAULT ('C-' || lpad(nextval('claims_code_seq')::text, 3, '0')) CHECK (code ~ '^C-[0-9]{3,}$'),
  statement TEXT NOT NULL CHECK (length(btrim(statement)) > 0),
  status TEXT NOT NULL DEFAULT 'UNKNOWN' CHECK (status IN ('CONFIRMED','PARTIALLY_CONFIRMED','PLANNED','UNKNOWN')),
  project TEXT NOT NULL CHECK (project IN ('agriloop','tradenotes','yardscale','andrew-builds')),
  verified_at TIMESTAMPTZ,
  limitations TEXT,           -- what is NOT established; mandatory for PARTIALLY_CONFIRMED and always shown with it
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (status <> 'PARTIALLY_CONFIRMED' OR length(btrim(coalesce(limitations, ''))) > 0)
);

CREATE TABLE IF NOT EXISTS claim_sources (
  claim_id BIGINT NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
  source_id BIGINT NOT NULL REFERENCES sources(id) ON DELETE RESTRICT,
  PRIMARY KEY (claim_id, source_id)
);

CREATE TABLE IF NOT EXISTS episodes (
  id BIGSERIAL PRIMARY KEY,
  series_id BIGINT NOT NULL REFERENCES series(id) ON DELETE RESTRICT,
  code TEXT NOT NULL CHECK (length(btrim(code)) > 0),
  title TEXT NOT NULL CHECK (length(btrim(title)) > 0),
  status TEXT NOT NULL DEFAULT 'IDEA' CHECK (status IN
    ('IDEA','SCRIPTING','READY_TO_RECORD','RECORDED','EDITING','READY_TO_PUBLISH','PUBLISHED','ARCHIVED')),
  planned_date DATE,
  target_duration_s INTEGER CHECK (target_duration_s IS NULL OR target_duration_s > 0),
  production_path TEXT CHECK (production_path IS NULL OR (production_path ~ '^production/[A-Za-z0-9._/-]+$' AND production_path !~ '\.\.')),
  parent_episode_id BIGINT REFERENCES episodes(id) ON DELETE SET NULL,   -- a short points at its long-form parent (A4)
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (series_id, code),
  CHECK (parent_episode_id IS NULL OR parent_episode_id <> id)
);

CREATE TABLE IF NOT EXISTS ideas (
  id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL CHECK (length(btrim(title)) > 0),
  notes TEXT NOT NULL DEFAULT '',
  series_id BIGINT REFERENCES series(id) ON DELETE SET NULL,
  moment_id BIGINT REFERENCES moments(id) ON DELETE SET NULL,
  episode_id BIGINT REFERENCES episodes(id) ON DELETE SET NULL,          -- set when the idea is promoted
  status TEXT NOT NULL DEFAULT 'BACKLOG' CHECK (status IN ('BACKLOG','SCHEDULED','DROPPED')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS scripts (
  id BIGSERIAL PRIMARY KEY,
  episode_id BIGINT NOT NULL REFERENCES episodes(id) ON DELETE RESTRICT,
  version INTEGER NOT NULL CHECK (version >= 1),
  status TEXT NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT','IN_REVIEW','READY_TO_RECORD','LOCKED')),
  body TEXT NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (episode_id, version)
);

-- One sentence per row. Lines default to FACT so nothing slips through unmarked (A5).
CREATE TABLE IF NOT EXISTS script_lines (
  id BIGSERIAL PRIMARY KEY,
  script_id BIGINT NOT NULL REFERENCES scripts(id) ON DELETE CASCADE,
  position INTEGER NOT NULL CHECK (position >= 1),
  text TEXT NOT NULL CHECK (length(btrim(text)) > 0),
  kind TEXT NOT NULL DEFAULT 'FACT' CHECK (kind IN
    ('FACT','OPINION','REFLECTION','QUESTION','HYPOTHESIS','DIRECTION','CTA','DISCLAIMER')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (script_id, position) DEFERRABLE INITIALLY DEFERRED     -- lets a reorder swap positions inside one transaction
);

CREATE TABLE IF NOT EXISTS line_claims (
  line_id BIGINT NOT NULL REFERENCES script_lines(id) ON DELETE CASCADE,
  claim_id BIGINT NOT NULL REFERENCES claims(id) ON DELETE RESTRICT,   -- a claim in use cannot be deleted
  PRIMARY KEY (line_id, claim_id)
);

CREATE TABLE IF NOT EXISTS shots (
  id BIGSERIAL PRIMARY KEY,
  episode_id BIGINT NOT NULL REFERENCES episodes(id) ON DELETE RESTRICT,
  code TEXT NOT NULL CHECK (length(btrim(code)) > 0),
  description TEXT NOT NULL DEFAULT '',
  location TEXT NOT NULL DEFAULT '',
  device TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'PLANNED' CHECK (status IN ('PLANNED','CAPTURED','REJECTED')),
  checklist JSONB NOT NULL DEFAULT '[]'::jsonb CHECK (jsonb_typeof(checklist) = 'array'),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (episode_id, code)
);

-- path is a RELATIVE path to a file in the production/ pipeline. The app records metadata; files stay on disk (D3).
CREATE TABLE IF NOT EXISTS assets (
  id BIGSERIAL PRIMARY KEY,
  episode_id BIGINT REFERENCES episodes(id) ON DELETE RESTRICT,
  kind TEXT NOT NULL CHECK (kind IN ('raw','voiceover','screen','graphic','thumbnail','caption','export')),
  path TEXT NOT NULL CHECK (length(btrim(path)) > 0 AND path !~ '(^/|(^|/)\.\.(/|$)|\\|://)'),
  hide_list_checked_at TIMESTAMPTZ,
  hide_list_result TEXT CHECK (hide_list_result IS NULL OR hide_list_result IN ('PASSED','FAILED','MANUAL_OK')),
  consent_ref TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK ((hide_list_result IS NULL) = (hide_list_checked_at IS NULL))
);

-- status only records what Andrew did. The app never posts anything. (Publish-gate trigger arrives with P5.)
CREATE TABLE IF NOT EXISTS posts (
  id BIGSERIAL PRIMARY KEY,
  episode_id BIGINT NOT NULL REFERENCES episodes(id) ON DELETE RESTRICT,
  asset_id BIGINT REFERENCES assets(id) ON DELETE SET NULL,
  platform TEXT NOT NULL CHECK (platform IN ('youtube','instagram','tiktok')),
  url TEXT,
  status TEXT NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT','APPROVED','PUBLISHED')),
  approved_at TIMESTAMPTZ,
  published_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (status = 'DRAFT' OR approved_at IS NOT NULL),
  CHECK (status <> 'PUBLISHED' OR published_at IS NOT NULL),
  CHECK (published_at IS NULL OR approved_at IS NULL OR published_at >= approved_at)
);

-- Manual entry only (D6). Append-only: to correct a number, record a new row.
CREATE TABLE IF NOT EXISTS metrics (
  id BIGSERIAL PRIMARY KEY,
  post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE RESTRICT,
  captured_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  views INTEGER CHECK (views >= 0),
  likes INTEGER CHECK (likes >= 0),
  comments INTEGER CHECK (comments >= 0),
  shares INTEGER CHECK (shares >= 0),
  saves INTEGER CHECK (saves >= 0),
  watch_time_s INTEGER CHECK (watch_time_s >= 0),
  followers_gained INTEGER,                 -- may legitimately be negative (net)
  source TEXT NOT NULL DEFAULT 'manual' CHECK (source = 'manual'),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS growth_log (
  id BIGSERIAL PRIMARY KEY,
  week_start DATE NOT NULL CHECK (extract(isodow FROM week_start) = 1),   -- a Monday
  platform TEXT NOT NULL CHECK (platform IN ('youtube','instagram','tiktok')),
  followers INTEGER NOT NULL CHECK (followers >= 0),
  notes TEXT NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (week_start, platform)
);

-- Joins content to EXISTING leads (leads.id is TEXT). No personal data is copied here. Deleting a prospect removes its links.
CREATE TABLE IF NOT EXISTS content_lead_links (
  id BIGSERIAL PRIMARY KEY,
  post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE RESTRICT,
  lead_id TEXT NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  cta_code TEXT,
  first_touch_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (post_id, lead_id)
);

-- Singleton plan: the 60-minute course. Total length is a constant of the product, not a setting.
CREATE TABLE IF NOT EXISTS course_plan (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  title TEXT NOT NULL CHECK (length(btrim(title)) > 0),
  status TEXT NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT','READY')),
  target_duration_s INTEGER NOT NULL DEFAULT 3600 CHECK (target_duration_s = 3600),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS course_modules (
  id BIGSERIAL PRIMARY KEY,
  position INTEGER NOT NULL CHECK (position >= 1),
  title TEXT NOT NULL CHECK (length(btrim(title)) > 0),
  duration_s INTEGER NOT NULL CHECK (duration_s > 0 AND duration_s <= 3600),
  episode_id BIGINT REFERENCES episodes(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (position) DEFERRABLE INITIALLY DEFERRED
);

-- Terms that must never appear on screen or in a post (names, partners, secrets). Entered by Andrew in the app, never in git.
CREATE TABLE IF NOT EXISTS hide_list (
  id BIGSERIAL PRIMARY KEY,
  term TEXT NOT NULL CHECK (length(btrim(term)) > 0),
  category TEXT NOT NULL CHECK (category IN ('person','partner','secret','financial','other')),
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS hide_list_term ON hide_list (lower(btrim(term)));

-- Indexes on foreign keys and the filters the screens will use.
CREATE INDEX IF NOT EXISTS episodes_series ON episodes (series_id);
CREATE INDEX IF NOT EXISTS episodes_status ON episodes (status);
CREATE INDEX IF NOT EXISTS episodes_planned ON episodes (planned_date);
CREATE INDEX IF NOT EXISTS episodes_parent ON episodes (parent_episode_id);
CREATE INDEX IF NOT EXISTS ideas_status ON ideas (status);
CREATE INDEX IF NOT EXISTS ideas_series ON ideas (series_id);
CREATE INDEX IF NOT EXISTS scripts_episode ON scripts (episode_id);
CREATE INDEX IF NOT EXISTS line_claims_claim ON line_claims (claim_id);
CREATE INDEX IF NOT EXISTS claims_status ON claims (status);
CREATE INDEX IF NOT EXISTS claims_project ON claims (project);
CREATE INDEX IF NOT EXISTS claim_sources_source ON claim_sources (source_id);
CREATE INDEX IF NOT EXISTS shots_episode ON shots (episode_id);
CREATE INDEX IF NOT EXISTS assets_episode ON assets (episode_id);
CREATE INDEX IF NOT EXISTS posts_episode ON posts (episode_id);
CREATE INDEX IF NOT EXISTS posts_status ON posts (status);
CREATE INDEX IF NOT EXISTS metrics_post ON metrics (post_id, captured_at);
CREATE INDEX IF NOT EXISTS moments_when ON moments (occurred_at);
CREATE INDEX IF NOT EXISTS moments_source ON moments (source_id);
CREATE INDEX IF NOT EXISTS lead_links_lead ON content_lead_links (lead_id);
CREATE INDEX IF NOT EXISTS course_modules_episode ON course_modules (episode_id);

-- ---------------------------------------------------------------------------------------------------------------------
-- 2. Rule functions and triggers. Messages start with CONTENT_RULE: so the API can show them safely (SQLSTATE 23514).
-- ---------------------------------------------------------------------------------------------------------------------

-- The single source of truth for the claim gate. The trigger below and (in P2) the checker screen both call it.
CREATE OR REPLACE FUNCTION script_gate_failures(p_script_id BIGINT)
RETURNS TABLE(out_line_id BIGINT, out_position INTEGER, out_reason TEXT, out_claim TEXT) AS $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM script_lines WHERE script_id = p_script_id) THEN
    RETURN QUERY SELECT NULL::BIGINT, NULL::INTEGER, 'EMPTY_SCRIPT'::TEXT, NULL::TEXT;
    RETURN;
  END IF;
  RETURN QUERY
    SELECT l.id, l.position, 'FACT_WITHOUT_CLAIM'::TEXT, NULL::TEXT
      FROM script_lines l
     WHERE l.script_id = p_script_id AND l.kind = 'FACT'
       AND NOT EXISTS (SELECT 1 FROM line_claims lc WHERE lc.line_id = l.id)
    UNION ALL
    SELECT l.id, l.position, ('CLAIM_' || c.status)::TEXT, c.code
      FROM script_lines l
      JOIN line_claims lc ON lc.line_id = l.id
      JOIN claims c ON c.id = lc.claim_id
     WHERE l.script_id = p_script_id AND l.kind = 'FACT' AND c.status <> 'CONFIRMED'
    ORDER BY 2, 3;
END; $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION scripts_guard() RETURNS trigger AS $$
DECLARE failures INTEGER;
BEGIN
  IF TG_OP = 'DELETE' THEN
    IF OLD.status IN ('READY_TO_RECORD', 'LOCKED') THEN
      RAISE EXCEPTION 'CONTENT_RULE: script % is %; a % script cannot be deleted (move a READY_TO_RECORD script back to DRAFT first)',
        OLD.id, OLD.status, OLD.status USING ERRCODE = 'check_violation';
    END IF;
    RETURN OLD;
  END IF;
  IF TG_OP = 'UPDATE' THEN
    IF OLD.status = 'LOCKED' THEN
      RAISE EXCEPTION 'CONTENT_RULE: script % is LOCKED and can no longer change', OLD.id USING ERRCODE = 'check_violation';
    END IF;
    IF NEW.episode_id <> OLD.episode_id OR NEW.version <> OLD.version THEN
      RAISE EXCEPTION 'CONTENT_RULE: a script cannot move to another episode or change version' USING ERRCODE = 'check_violation';
    END IF;
    IF OLD.status = 'READY_TO_RECORD' AND NEW.status = 'READY_TO_RECORD' AND NEW.body IS DISTINCT FROM OLD.body THEN
      RAISE EXCEPTION 'CONTENT_RULE: script % is READY_TO_RECORD; move it back to DRAFT before editing the body', OLD.id
        USING ERRCODE = 'check_violation';
    END IF;
  END IF;
  IF NEW.status = 'LOCKED' AND (TG_OP = 'INSERT' OR OLD.status <> 'READY_TO_RECORD') THEN
    RAISE EXCEPTION 'CONTENT_RULE: only a READY_TO_RECORD script can be LOCKED' USING ERRCODE = 'check_violation';
  END IF;
  IF NEW.status IN ('READY_TO_RECORD', 'LOCKED') AND (TG_OP = 'INSERT' OR NEW.status IS DISTINCT FROM OLD.status) THEN
    SELECT count(*) INTO failures FROM script_gate_failures(NEW.id);
    IF failures > 0 THEN
      RAISE EXCEPTION 'CONTENT_RULE: script % fails the claim check (% problem(s)); every FACT line needs a CONFIRMED claim', NEW.id, failures
        USING ERRCODE = 'check_violation';
    END IF;
  END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

-- A script that leaves READY_TO_RECORD also pulls its episode back out of READY_TO_RECORD.
CREATE OR REPLACE FUNCTION scripts_after() RETURNS trigger AS $$
BEGIN
  IF OLD.status = 'READY_TO_RECORD' AND NEW.status IN ('DRAFT', 'IN_REVIEW') THEN
    UPDATE episodes SET status = 'SCRIPTING' WHERE id = NEW.episode_id AND status = 'READY_TO_RECORD';
  END IF;
  RETURN NULL;
END; $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION script_lines_guard() RETURNS trigger AS $$
DECLARE s TEXT; sid BIGINT;
BEGIN
  FOR sid IN SELECT DISTINCT x FROM unnest(ARRAY[
      CASE WHEN TG_OP <> 'INSERT' THEN OLD.script_id END,
      CASE WHEN TG_OP <> 'DELETE' THEN NEW.script_id END]) AS x WHERE x IS NOT NULL LOOP
    SELECT status INTO s FROM scripts WHERE id = sid;
    IF s IN ('READY_TO_RECORD', 'LOCKED') THEN
      RAISE EXCEPTION 'CONTENT_RULE: script % is %; move it back to DRAFT before changing its lines', sid, s USING ERRCODE = 'check_violation';
    END IF;
  END LOOP;
  RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END; $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION line_claims_guard() RETURNS trigger AS $$
DECLARE s TEXT; lid BIGINT;
BEGIN
  lid := CASE WHEN TG_OP = 'DELETE' THEN OLD.line_id ELSE NEW.line_id END;
  SELECT sc.status INTO s FROM script_lines l JOIN scripts sc ON sc.id = l.script_id WHERE l.id = lid;
  IF s IN ('READY_TO_RECORD', 'LOCKED') THEN
    RAISE EXCEPTION 'CONTENT_RULE: this script is %; move it back to DRAFT before changing claim links', s USING ERRCODE = 'check_violation';
  END IF;
  RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END; $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION claims_guard() RETURNS trigger AS $$
BEGIN
  -- Rewording a verified claim voids the verification: the new wording has not been checked.
  IF TG_OP = 'UPDATE' AND NEW.statement IS DISTINCT FROM OLD.statement
     AND OLD.status IN ('CONFIRMED', 'PARTIALLY_CONFIRMED') AND NEW.status = OLD.status THEN
    NEW.status := 'UNKNOWN';
    NEW.verified_at := NULL;
  END IF;
  IF NEW.status IN ('CONFIRMED', 'PARTIALLY_CONFIRMED') THEN
    IF NOT EXISTS (SELECT 1 FROM claim_sources WHERE claim_id = NEW.id) THEN
      RAISE EXCEPTION 'CONTENT_RULE: claim % cannot be % without at least one source', NEW.code, NEW.status USING ERRCODE = 'check_violation';
    END IF;
    IF NEW.verified_at IS NULL OR (TG_OP = 'UPDATE' AND NEW.status <> OLD.status AND NEW.verified_at IS NOT DISTINCT FROM OLD.verified_at) THEN
      NEW.verified_at := now();
    END IF;
  ELSE
    NEW.verified_at := NULL;
  END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

-- When a claim stops being CONFIRMED, every READY_TO_RECORD script that cites it goes back to IN_REVIEW (and the event is audited).
-- LOCKED scripts are history and are left alone; the P2 checker will flag them.
CREATE OR REPLACE FUNCTION claims_after() RETURNS trigger AS $$
DECLARE r RECORD;
BEGIN
  IF OLD.status = 'CONFIRMED' AND NEW.status <> 'CONFIRMED' THEN
    FOR r IN SELECT DISTINCT sc.id FROM scripts sc
               JOIN script_lines l ON l.script_id = sc.id
               JOIN line_claims lc ON lc.line_id = l.id
              WHERE lc.claim_id = NEW.id AND sc.status = 'READY_TO_RECORD' LOOP
      UPDATE scripts SET status = 'IN_REVIEW' WHERE id = r.id;
      INSERT INTO audit_events(at, actor, action, target, detail)
        VALUES (to_char(now() AT TIME ZONE 'utc', 'YYYY-MM-DD"T"HH24:MI:SS.US"+00:00"'), 'db', 'content.script.demoted',
                'script:' || r.id, 'claim ' || NEW.code || ' is now ' || NEW.status);
    END LOOP;
  END IF;
  RETURN NULL;
END; $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION claim_sources_guard() RETURNS trigger AS $$
DECLARE s TEXT;
BEGIN
  SELECT status INTO s FROM claims WHERE id = OLD.claim_id;     -- NULL while the claim itself is being deleted
  IF s IN ('CONFIRMED', 'PARTIALLY_CONFIRMED')
     AND NOT EXISTS (SELECT 1 FROM claim_sources WHERE claim_id = OLD.claim_id AND source_id <> OLD.source_id) THEN
    RAISE EXCEPTION 'CONTENT_RULE: a % claim needs at least one source; downgrade the claim first', s USING ERRCODE = 'check_violation';
  END IF;
  RETURN OLD;
END; $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION episodes_guard() RETURNS trigger AS $$
BEGIN
  IF NEW.status = 'READY_TO_RECORD' AND (TG_OP = 'INSERT' OR NEW.status IS DISTINCT FROM OLD.status) THEN
    IF NOT EXISTS (SELECT 1 FROM scripts WHERE episode_id = NEW.id AND status IN ('READY_TO_RECORD', 'LOCKED')) THEN
      RAISE EXCEPTION 'CONTENT_RULE: an episode needs a READY_TO_RECORD script before it can be READY_TO_RECORD' USING ERRCODE = 'check_violation';
    END IF;
  END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION content_append_only() RETURNS trigger AS $$
BEGIN RAISE EXCEPTION 'CONTENT_RULE: % is append-only; record a new row instead of changing history', TG_TABLE_NAME USING ERRCODE = 'check_violation'; END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION course_plan_guard() RETURNS trigger AS $$
DECLARE total BIGINT; n BIGINT;
BEGIN
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION 'CONTENT_RULE: the course plan cannot be deleted' USING ERRCODE = 'check_violation';
  END IF;
  IF NEW.status = 'READY' AND (TG_OP = 'INSERT' OR OLD.status <> 'READY') THEN
    SELECT coalesce(sum(duration_s), 0), count(*) INTO total, n FROM course_modules;
    IF n = 0 OR total <> 3600 THEN
      RAISE EXCEPTION 'CONTENT_RULE: the course must total exactly 60:00 to be READY (currently %:%, % module(s))',
        total / 60, lpad((total % 60)::text, 2, '0'), n USING ERRCODE = 'check_violation';
    END IF;
  END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION course_modules_guard() RETURNS trigger AS $$
BEGIN
  IF EXISTS (SELECT 1 FROM course_plan WHERE status = 'READY') THEN
    RAISE EXCEPTION 'CONTENT_RULE: the course plan is READY (60:00); set it back to DRAFT before changing modules' USING ERRCODE = 'check_violation';
  END IF;
  RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END; $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS scripts_guard_t ON scripts;
CREATE TRIGGER scripts_guard_t BEFORE INSERT OR UPDATE OR DELETE ON scripts FOR EACH ROW EXECUTE FUNCTION scripts_guard();
DROP TRIGGER IF EXISTS scripts_after_t ON scripts;
CREATE TRIGGER scripts_after_t AFTER UPDATE OF status ON scripts FOR EACH ROW EXECUTE FUNCTION scripts_after();
DROP TRIGGER IF EXISTS script_lines_guard_t ON script_lines;
CREATE TRIGGER script_lines_guard_t BEFORE INSERT OR UPDATE OR DELETE ON script_lines FOR EACH ROW EXECUTE FUNCTION script_lines_guard();
DROP TRIGGER IF EXISTS line_claims_guard_t ON line_claims;
CREATE TRIGGER line_claims_guard_t BEFORE INSERT OR UPDATE OR DELETE ON line_claims FOR EACH ROW EXECUTE FUNCTION line_claims_guard();
DROP TRIGGER IF EXISTS claims_guard_t ON claims;
CREATE TRIGGER claims_guard_t BEFORE INSERT OR UPDATE ON claims FOR EACH ROW EXECUTE FUNCTION claims_guard();
DROP TRIGGER IF EXISTS claims_after_t ON claims;
CREATE TRIGGER claims_after_t AFTER UPDATE OF status ON claims FOR EACH ROW EXECUTE FUNCTION claims_after();
DROP TRIGGER IF EXISTS claim_sources_guard_t ON claim_sources;
CREATE TRIGGER claim_sources_guard_t BEFORE DELETE ON claim_sources FOR EACH ROW EXECUTE FUNCTION claim_sources_guard();
DROP TRIGGER IF EXISTS episodes_guard_t ON episodes;
CREATE TRIGGER episodes_guard_t BEFORE INSERT OR UPDATE ON episodes FOR EACH ROW EXECUTE FUNCTION episodes_guard();
DROP TRIGGER IF EXISTS metrics_no_change ON metrics;
CREATE TRIGGER metrics_no_change BEFORE UPDATE OR DELETE ON metrics FOR EACH ROW EXECUTE FUNCTION content_append_only();
DROP TRIGGER IF EXISTS metrics_no_truncate ON metrics;
CREATE TRIGGER metrics_no_truncate BEFORE TRUNCATE ON metrics FOR EACH STATEMENT EXECUTE FUNCTION content_append_only();
DROP TRIGGER IF EXISTS course_plan_guard_t ON course_plan;
CREATE TRIGGER course_plan_guard_t BEFORE INSERT OR UPDATE OR DELETE ON course_plan FOR EACH ROW EXECUTE FUNCTION course_plan_guard();
DROP TRIGGER IF EXISTS course_modules_guard_t ON course_modules;
CREATE TRIGGER course_modules_guard_t BEFORE INSERT OR UPDATE OR DELETE ON course_modules FOR EACH ROW EXECUTE FUNCTION course_modules_guard();

-- ---------------------------------------------------------------------------------------------------------------------
-- 3. Row-level security: enabled AND forced, one policy for content_app, minimal grants. No grants on credentials/sessions.
-- ---------------------------------------------------------------------------------------------------------------------
DO $$
DECLARE
  t TEXT; seq TEXT;
  tbls TEXT[] := ARRAY['series','sources','moments','claims','claim_sources','episodes','ideas','scripts','script_lines','line_claims',
                       'shots','assets','posts','metrics','growth_log','content_lead_links','course_plan','course_modules','hide_list'];
  touched TEXT[] := ARRAY['series','sources','moments','claims','episodes','ideas','scripts','script_lines','shots','assets','posts',
                          'growth_log','content_lead_links','course_plan','course_modules','hide_list'];
BEGIN
  EXECUTE format('GRANT USAGE ON SCHEMA %I TO content_app', current_schema());
  FOREACH t IN ARRAY touched LOOP
    EXECUTE format('DROP TRIGGER IF EXISTS content_touch_t ON %I', t);
    EXECUTE format('CREATE TRIGGER content_touch_t BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION content_touch()', t);
  END LOOP;
  FOREACH t IN ARRAY tbls LOOP
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
    EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', t);
    EXECUTE format('DROP POLICY IF EXISTS content_app_all ON %I', t);
    EXECUTE format('CREATE POLICY content_app_all ON %I FOR ALL TO content_app USING (true) WITH CHECK (true)', t);
    EXECUTE format('REVOKE ALL ON %I FROM PUBLIC', t);
    IF t = 'metrics' THEN      -- append-only also at privilege level
      EXECUTE format('REVOKE UPDATE, DELETE, TRUNCATE ON %I FROM content_app', t);
      EXECUTE format('GRANT SELECT, INSERT ON %I TO content_app', t);
    ELSE
      EXECUTE format('GRANT SELECT, INSERT, UPDATE, DELETE ON %I TO content_app', t);
    END IF;
    IF t NOT IN ('claim_sources', 'line_claims') THEN        -- junction tables have no id column
      seq := pg_get_serial_sequence(format('%I.%I', current_schema(), t), 'id');
      IF seq IS NOT NULL THEN
        EXECUTE format('GRANT USAGE, SELECT ON SEQUENCE %s TO content_app', seq);
      END IF;
    END IF;
  END LOOP;
  EXECUTE 'GRANT USAGE, SELECT ON SEQUENCE claims_code_seq TO content_app';
  -- Only what the content screens need from the Outreach Desk: append to the audit log; read a prospect's id, name, business, stage.
  EXECUTE 'GRANT INSERT ON audit_events TO content_app';
  EXECUTE 'GRANT SELECT (id, name, business, stage) ON leads TO content_app';
END $$;

-- ---------------------------------------------------------------------------------------------------------------------
-- 4. Seed rows, written AS content_app (also proves the role, grants and policies work at migration time).
-- ---------------------------------------------------------------------------------------------------------------------
SET LOCAL ROLE content_app;
INSERT INTO series (slug, title) VALUES
  ('course', 'Course'), ('bootstrapper-experiment', 'Bootstrapper Experiment'), ('andrew-builds', 'Andrew Builds'), ('shorts', 'Shorts')
ON CONFLICT (slug) DO NOTHING;
INSERT INTO course_plan (id, title) VALUES (1, 'From Sales to SaaS') ON CONFLICT (id) DO NOTHING;
RESET ROLE;
