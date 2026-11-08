"""P0 foundation tests for the content platform: migration, enumerations, database-enforced rules, row-level security,
API authentication, and the app shell. Needs TEST_DATABASE_URL (a THROWAWAY Postgres). RLS tests additionally need that
URL's role to be a superuser (they create temporary roles); otherwise they are skipped loudly.

All sample data is labelled TEST/SAMPLE and is rolled back or dropped with its schema."""

import json
import re
import secrets
import unittest
import uuid
from urllib.parse import urlsplit, urlunsplit

import psycopg

from core import db
from core.content import access, meta, status
from dashboard import app as dash
from tests import authutil
from tests.dbutil import URL, make_conn, require_db

LEGACY_TABLES = {"settings", "owner_credentials", "sessions", "auth_attempts", "audit_events", "leads", "activity_events",
                 "sales_tasks", "playbooks", "playbook_runs", "schema_migrations"}
CheckViolation = psycopg.errors.CheckViolation


def _admin():
    return db.connect(URL)


def _is_superuser() -> bool:
    c = _admin()
    try:
        return bool(c.execute("SELECT rolsuper FROM pg_roles WHERE rolname = current_user").fetchone()[0])
    finally:
        c.close()


# ---------------------------------------------------------------------------------------------------------------------
# Migration
# ---------------------------------------------------------------------------------------------------------------------
class MigrationTest(unittest.TestCase):
    def setUp(self):
        self.conn = make_conn()

    def test_applies_and_is_recorded(self):
        names = [r["name"] for r in self.conn.execute("SELECT name FROM schema_migrations ORDER BY name")]
        self.assertEqual(names, ["001_schema.sql", "002_content.sql"])
        self.assertEqual(db.migrate(self.conn), [], "the runner must not re-apply a recorded migration")

    def test_sql_is_idempotent_when_run_again(self):
        sql = (db.MIGRATIONS / "002_content.sql").read_text()
        before = self._shape()
        for _ in range(2):
            with self.conn.transaction():
                self.conn.raw.execute(sql)
        self.assertEqual(self._shape(), before, "re-running the migration changed the schema or duplicated seed rows")

    def _shape(self):
        q = self.conn.execute
        return {
            "tables": sorted(r[0] for r in q("SELECT tablename FROM pg_tables WHERE schemaname = current_schema()")),
            "columns": [tuple(r.values()) for r in q("SELECT table_name, column_name, data_type FROM information_schema.columns "
                                                    "WHERE table_schema = current_schema() ORDER BY 1, 2")],
            "triggers": sorted(r[0] for r in q("SELECT tgname FROM pg_trigger WHERE NOT tgisinternal")),
            "policies": sorted(f"{r[0]}.{r[1]}" for r in q("SELECT tablename, policyname FROM pg_policies WHERE schemaname = current_schema()")),
            "series": q("SELECT count(*) FROM series").fetchone()[0], "plan": q("SELECT count(*) FROM course_plan").fetchone()[0],
        }

    def test_expected_tables_exist_and_meta_lists_them_all(self):
        actual = {r[0] for r in self.conn.execute("SELECT tablename FROM pg_tables WHERE schemaname = current_schema()")}
        self.assertEqual(actual - LEGACY_TABLES, set(meta.TABLES), "meta.TABLES must list exactly the content tables")
        for needed in ("episodes", "scripts", "claims", "sources", "shots", "assets", "posts", "metrics"):
            self.assertIn(needed, actual)

    def test_existing_tables_are_not_modified(self):
        """Run only 001, snapshot every legacy column, then 002, and compare: additive means additive."""
        c = db.connect(URL)
        schema = "t_" + uuid.uuid4().hex[:10]
        c.execute(f'CREATE SCHEMA "{schema}"')
        c.close()
        try:
            c = db.connect(URL, schema=schema)
            with c.transaction():
                c.raw.execute((db.MIGRATIONS / "001_schema.sql").read_text())

            def snap():
                cols = [tuple(r.values()) for r in c.execute(
                    "SELECT table_name, column_name, data_type, is_nullable, column_default FROM information_schema.columns "
                    "WHERE table_schema = current_schema() AND table_name = ANY(?) ORDER BY 1, 2", (sorted(LEGACY_TABLES - {"schema_migrations"}),))]
                trg = sorted(r[0] for r in c.execute("SELECT tgname FROM pg_trigger t JOIN pg_class k ON k.oid = t.tgrelid "
                                                    "WHERE NOT tgisinternal AND k.relname = ANY(?)", (sorted(LEGACY_TABLES),)))
                rls = sorted((r[0], r[1]) for r in c.execute("SELECT relname, relrowsecurity FROM pg_class "
                                                            "WHERE relnamespace = current_schema()::regnamespace AND relname = ANY(?)", (sorted(LEGACY_TABLES),)))
                return cols, trg, rls
            before = snap()
            with c.transaction():
                c.raw.execute((db.MIGRATIONS / "002_content.sql").read_text())
            self.assertEqual(snap(), before)
            c.close()
        finally:
            a = _admin()
            a.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
            a.close()

    def test_seed_rows(self):
        with access.content_session(self.conn):
            slugs = [r["slug"] for r in self.conn.execute("SELECT slug FROM series ORDER BY id")]
            plan = self.conn.execute("SELECT status, target_duration_s FROM course_plan").fetchone()
        self.assertEqual(slugs, ["course", "bootstrapper-experiment", "andrew-builds", "shorts"])
        self.assertEqual((plan["status"], plan["target_duration_s"]), ("DRAFT", 3600))


class EnumDriftTest(unittest.TestCase):
    """The database CHECK constraints are authoritative; meta.ENUMS must say exactly the same thing."""

    def test_python_enumerations_match_database_checks(self):
        conn = make_conn()
        defs = {}
        for r in conn.execute("SELECT k.relname AS tbl, pg_get_constraintdef(c.oid) AS def FROM pg_constraint c JOIN pg_class k ON k.oid = c.conrelid "
                              "WHERE c.contype = 'c' AND c.connamespace = current_schema()::regnamespace"):
            defs.setdefault(r["tbl"], []).append(r["def"])
        for (table, col), values in meta.ENUMS.items():
            found = None
            for d in defs.get(table, []):
                m = re.search(rf"\(?{col}\)?(?:::text)? = ANY \(\(?ARRAY\[(.*?)\]", d)
                if m:
                    found = tuple(re.findall(r"'([^']+)'", m.group(1)))
            self.assertIsNotNone(found, f"no CHECK found for {table}.{col}")
            self.assertEqual(sorted(found), sorted(values), f"{table}.{col} drifted between meta.py and the database")

    def test_factual_and_non_factual_kinds_partition_line_kinds(self):
        kinds = set(meta.ENUMS[("script_lines", "kind")])
        self.assertEqual(set(meta.FACTUAL_KINDS) | set(meta.NON_FACTUAL_KINDS), kinds)
        self.assertFalse(set(meta.FACTUAL_KINDS) & set(meta.NON_FACTUAL_KINDS))
        for k in ("OPINION", "REFLECTION", "QUESTION", "HYPOTHESIS"):  # the brief: these must be distinguishable from facts
            self.assertIn(k, meta.NON_FACTUAL_KINDS)


# ---------------------------------------------------------------------------------------------------------------------
# Database-enforced rules. The same tests run twice: as the connecting role, and as content_app (the role the API uses),
# proving the triggers work with the application's real, minimal privileges.
# ---------------------------------------------------------------------------------------------------------------------
class RuleTests:
    conn = None

    def enter_role(self):
        pass

    def setUp(self):
        self._tx = self.conn.raw.transaction(force_rollback=True)  # every test is rolled back; seeds survive
        self._tx.__enter__()
        self.enter_role()

    def tearDown(self):
        self._tx.__exit__(None, None, None)

    # --- helpers
    def q(self, sql, params=()):
        return self.conn.execute(sql, params)

    def one(self, sql, params=()):
        return self.conn.execute(sql, params).fetchone()[0]

    def fails(self, exc, sql, params=(), contains=None, rule=None):
        """The statement must fail with `exc`; if `rule` is True/False, also check it is/is not one of our CONTENT_RULE messages."""
        with self.assertRaises(exc) as cm:
            with self.conn.transaction():  # savepoint: the outer test transaction survives
                self.conn.execute(sql, params)
        msg = access.rule_message(cm.exception)
        if rule is True:
            self.assertIsNotNone(msg, f"expected a CONTENT_RULE message, got: {cm.exception}")
        if rule is False:
            self.assertIsNone(msg)
        if contains:
            self.assertIn(contains.lower(), str(cm.exception).lower())
        return cm.exception

    def deferred_unique(self, sql, params=()):
        """DEFERRABLE INITIALLY DEFERRED constraints are checked at commit; force the check now to prove the duplicate is rejected."""
        with self.assertRaises(psycopg.errors.UniqueViolation):
            with self.conn.transaction():
                self.conn.execute(sql, params)
                self.conn.execute("SET CONSTRAINTS ALL IMMEDIATE")

    def episode(self, code="E001", series="andrew-builds"):
        sid = self.one("SELECT id FROM series WHERE slug = ?", (series,))
        return self.one("INSERT INTO episodes(series_id, code, title) VALUES (?,?,?) RETURNING id", (sid, code, f"SAMPLE episode {code}"))

    def script(self, ep, version=1):
        return self.one("INSERT INTO scripts(episode_id, version) VALUES (?,?) RETURNING id", (ep, version))

    def line(self, script, pos, text="SAMPLE line", kind="FACT"):
        return self.one("INSERT INTO script_lines(script_id, position, text, kind) VALUES (?,?,?,?) RETURNING id", (script, pos, text, kind))

    def source(self, kind="document", ref="SAMPLE source"):
        return self.one("INSERT INTO sources(kind, reference) VALUES (?,?) RETURNING id", (kind, ref))

    def claim(self, state="UNKNOWN", statement="SAMPLE claim", limitations=None):
        cid = self.one("INSERT INTO claims(statement, project) VALUES (?, 'andrew-builds') RETURNING id", (statement,))
        if state in ("CONFIRMED", "PARTIALLY_CONFIRMED"):
            self.q("INSERT INTO claim_sources(claim_id, source_id) VALUES (?,?)", (cid, self.source()))
        if state != "UNKNOWN":
            self.q("UPDATE claims SET status = ?, limitations = ? WHERE id = ?", (state, limitations, cid))
        return cid

    def link(self, line, claim):
        self.q("INSERT INTO line_claims(line_id, claim_id) VALUES (?,?)", (line, claim))

    def set_status(self, script, state):
        self.q("UPDATE scripts SET status = ? WHERE id = ?", (state, script))

    def status_of(self, table, id_):
        return self.one(f"SELECT status FROM {table} WHERE id = ?", (id_,))

    def ready_script(self, ep=None, code="E001"):
        ep = ep or self.episode(code)
        s = self.script(ep)
        l = self.line(s, 1, "SAMPLE confirmed fact")
        self.link(l, self.claim("CONFIRMED"))
        self.set_status(s, "READY_TO_RECORD")
        return ep, s, l

    # --- claim gate
    def test_empty_script_cannot_be_ready(self):
        s = self.script(self.episode())
        self.fails(CheckViolation, "UPDATE scripts SET status = 'READY_TO_RECORD' WHERE id = ?", (s,), "claim check", rule=True)
        self.assertEqual([r["out_reason"] for r in self.q("SELECT * FROM script_gate_failures(?)", (s,))], ["EMPTY_SCRIPT"])

    def test_fact_line_without_claim_blocks_ready(self):
        s = self.script(self.episode())
        l = self.line(s, 1, "SAMPLE: a factual sentence with no claim")
        self.fails(CheckViolation, "UPDATE scripts SET status = 'READY_TO_RECORD' WHERE id = ?", (s,), rule=True)
        rows = self.q("SELECT * FROM script_gate_failures(?)", (s,)).fetchall()
        self.assertEqual([(r["out_line_id"], r["out_reason"]) for r in rows], [(l, "FACT_WITHOUT_CLAIM")])

    def test_planned_unknown_or_partial_claim_blocks_ready(self):
        for state, limits in (("PLANNED", None), ("UNKNOWN", None), ("PARTIALLY_CONFIRMED", "SAMPLE: only the first month is verified")):
            with self.subTest(state=state):
                with self.conn.transaction():  # savepoint per sub-case
                    s = self.script(self.episode(code="E-" + state[:4]))
                    c = self.claim(state, limitations=limits)
                    self.link(self.line(s, 1), c)
                    self.fails(CheckViolation, "UPDATE scripts SET status = 'READY_TO_RECORD' WHERE id = ?", (s,), rule=True)
                    reasons = [r["out_reason"] for r in self.q("SELECT * FROM script_gate_failures(?)", (s,))]
                    self.assertEqual(reasons, ["CLAIM_" + state])
                    self.assertEqual(self.status_of("scripts", s), "DRAFT")

    def test_confirmed_claim_lets_script_become_ready(self):
        _, s, _ = self.ready_script()
        self.assertEqual(self.status_of("scripts", s), "READY_TO_RECORD")
        self.assertEqual(self.q("SELECT * FROM script_gate_failures(?)", (s,)).fetchall(), [])

    def test_one_unresolved_claim_among_confirmed_ones_still_blocks(self):
        s = self.script(self.episode())
        l = self.line(s, 1)
        self.link(l, self.claim("CONFIRMED"))
        self.link(l, self.claim("PLANNED"))
        self.fails(CheckViolation, "UPDATE scripts SET status = 'READY_TO_RECORD' WHERE id = ?", (s,), rule=True)

    def test_non_factual_lines_need_no_claims(self):
        s = self.script(self.episode())
        for i, kind in enumerate(meta.NON_FACTUAL_KINDS, start=1):
            self.line(s, i, f"SAMPLE {kind.lower()} line", kind)
        self.set_status(s, "READY_TO_RECORD")
        self.assertEqual(self.status_of("scripts", s), "READY_TO_RECORD")

    def test_new_lines_default_to_fact_so_nothing_slips_through(self):
        s = self.script(self.episode())
        l = self.one("INSERT INTO script_lines(script_id, position, text) VALUES (?,1,'SAMPLE unmarked line') RETURNING id", (s,))
        self.assertEqual(self.one("SELECT kind FROM script_lines WHERE id = ?", (l,)), "FACT")
        self.fails(CheckViolation, "UPDATE scripts SET status = 'READY_TO_RECORD' WHERE id = ?", (s,), rule=True)

    def test_realistic_script_reports_every_failing_line(self):
        """A mixed SAMPLE script: only the lines that break the rules are reported."""
        s = self.script(self.episode(code="E-SAMPLE"))
        ok_claim = self.claim("CONFIRMED", "SAMPLE: the Outreach Desk records outreach and never sends messages")
        planned = self.claim("PLANNED", "SAMPLE: TradeNotes will launch publicly")
        l1 = self.line(s, 1, "The Outreach Desk records outreach and never sends messages.")
        l2 = self.line(s, 2, "I think a rendered page is not proof that a feature works.", "OPINION")
        l3 = self.line(s, 3, "Will anyone watch a build-in-public series?", "QUESTION")
        l4 = self.line(s, 4, "Showing real failures may build more trust than polished demos.", "HYPOTHESIS")
        l5 = self.line(s, 5, "TradeNotes will launch publicly.")
        l6 = self.line(s, 6, "TradeNotes is a trading journal.")  # FACT, no claim
        self.link(l1, ok_claim)
        self.link(l5, planned)
        rows = [(r["out_position"], r["out_reason"]) for r in self.q("SELECT * FROM script_gate_failures(?)", (s,))]
        self.assertEqual(rows, [(5, "CLAIM_PLANNED"), (6, "FACT_WITHOUT_CLAIM")])
        self.fails(CheckViolation, "UPDATE scripts SET status = 'READY_TO_RECORD' WHERE id = ?", (s,), "2 problem", rule=True)

    def test_script_cannot_be_inserted_directly_as_ready_or_locked(self):
        ep = self.episode()
        for state in ("READY_TO_RECORD", "LOCKED"):
            self.fails(CheckViolation, "INSERT INTO scripts(episode_id, version, status) VALUES (?,?,?)", (ep, 1, state), rule=True)

    # --- locking
    def test_ready_script_is_frozen_until_moved_back_to_draft(self):
        ep, s, l = self.ready_script()
        other_claim = self.claim("CONFIRMED", "SAMPLE other")
        attempts = [
            ("UPDATE script_lines SET text = 'changed after approval' WHERE id = ?", (l,)),
            ("UPDATE script_lines SET kind = 'OPINION' WHERE id = ?", (l,)),
            ("INSERT INTO script_lines(script_id, position, text, kind) VALUES (?,2,'late line','OPINION')", (s,)),
            ("DELETE FROM script_lines WHERE id = ?", (l,)),
            ("INSERT INTO line_claims(line_id, claim_id) VALUES (?,?)", (l, other_claim)),
            ("DELETE FROM line_claims WHERE line_id = ?", (l,)),
            ("UPDATE scripts SET body = 'edited after approval' WHERE id = ?", (s,)),
            ("DELETE FROM scripts WHERE id = ?", (s,)),
        ]
        for sql, params in attempts:
            with self.subTest(sql=sql):
                self.fails(CheckViolation, sql, params, rule=True)
        self.set_status(s, "DRAFT")  # the sanctioned way out
        self.q("UPDATE script_lines SET text = 'edited while DRAFT' WHERE id = ?", (l,))
        self.q("UPDATE scripts SET body = 'edited while DRAFT' WHERE id = ?", (s,))
        self.assertEqual(self.status_of("episodes", ep), "IDEA")

    def test_line_cannot_be_moved_into_a_ready_script(self):
        _, ready, _ = self.ready_script()
        draft = self.script(self.episode(code="E002"))
        l = self.line(draft, 1)
        self.fails(CheckViolation, "UPDATE script_lines SET script_id = ? WHERE id = ?", (ready, l), rule=True)

    def test_locked_script_is_final(self):
        ep, s, l = self.ready_script()
        self.set_status(s, "LOCKED")
        for sql, params in (("UPDATE scripts SET status = 'DRAFT' WHERE id = ?", (s,)), ("UPDATE scripts SET body = 'x' WHERE id = ?", (s,)),
                            ("DELETE FROM scripts WHERE id = ?", (s,)), ("UPDATE script_lines SET text = 'x' WHERE id = ?", (l,))):
            with self.subTest(sql=sql):
                self.fails(CheckViolation, sql, params, rule=True)

    def test_only_ready_script_can_be_locked(self):
        s = self.script(self.episode())
        self.line(s, 1, "SAMPLE opinion", "OPINION")
        self.fails(CheckViolation, "UPDATE scripts SET status = 'LOCKED' WHERE id = ?", (s,), "only a ready_to_record", rule=True)

    def test_script_cannot_change_episode_or_version(self):
        s = self.script(self.episode())
        other = self.episode(code="E002")
        self.fails(CheckViolation, "UPDATE scripts SET episode_id = ? WHERE id = ?", (other, s), rule=True)
        self.fails(CheckViolation, "UPDATE scripts SET version = 9 WHERE id = ?", (s,), rule=True)

    # --- claims
    def test_confirmed_claim_needs_a_source(self):
        c = self.claim()
        self.fails(CheckViolation, "UPDATE claims SET status = 'CONFIRMED' WHERE id = ?", (c,), "without at least one source", rule=True)
        self.fails(CheckViolation, "INSERT INTO claims(statement, project, status) VALUES ('SAMPLE','andrew-builds','CONFIRMED')", rule=True)
        self.q("INSERT INTO claim_sources(claim_id, source_id) VALUES (?,?)", (c, self.source("founder_answer", "SAMPLE: Andrew said so")))
        self.q("UPDATE claims SET status = 'CONFIRMED' WHERE id = ?", (c,))
        self.assertIsNotNone(self.one("SELECT verified_at FROM claims WHERE id = ?", (c,)))

    def test_only_confirmed_or_partial_claims_carry_a_verified_date(self):
        c = self.claim("CONFIRMED")
        self.q("UPDATE claims SET status = 'PLANNED' WHERE id = ?", (c,))
        self.assertIsNone(self.one("SELECT verified_at FROM claims WHERE id = ?", (c,)))

    def test_partially_confirmed_must_state_limitations(self):
        c = self.claim()
        self.q("INSERT INTO claim_sources(claim_id, source_id) VALUES (?,?)", (c, self.source()))
        for lim in (None, "", "   "):
            self.fails(CheckViolation, "UPDATE claims SET status = 'PARTIALLY_CONFIRMED', limitations = ? WHERE id = ?", (lim, c), rule=False)
        self.q("UPDATE claims SET status = 'PARTIALLY_CONFIRMED', limitations = 'SAMPLE: verified for one project only' WHERE id = ?", (c,))
        self.assertEqual(self.status_of("claims", c), "PARTIALLY_CONFIRMED")

    def test_last_source_of_a_verified_claim_cannot_be_removed(self):
        c = self.claim("CONFIRMED")
        self.fails(CheckViolation, "DELETE FROM claim_sources WHERE claim_id = ?", (c,), rule=True)
        second = self.source("url", "SAMPLE second")
        self.q("INSERT INTO claim_sources(claim_id, source_id) VALUES (?,?)", (c, second))
        self.q("DELETE FROM claim_sources WHERE claim_id = ? AND source_id = ?", (c, second))  # one source remains: allowed
        self.q("UPDATE claims SET status = 'UNKNOWN' WHERE id = ?", (c,))
        self.q("DELETE FROM claim_sources WHERE claim_id = ?", (c,))  # downgraded first: allowed

    def test_verified_claim_can_be_deleted_with_its_source_links(self):
        c = self.claim("CONFIRMED")
        self.q("DELETE FROM claims WHERE id = ?", (c,))
        self.assertEqual(self.one("SELECT count(*) FROM claim_sources WHERE claim_id = ?", (c,)), 0)

    def test_rewording_a_verified_claim_voids_the_verification(self):
        c = self.claim("CONFIRMED", "SAMPLE: the number is 5")
        self.q("UPDATE claims SET statement = 'SAMPLE: the number is 5000' WHERE id = ?", (c,))
        row = self.q("SELECT status, verified_at FROM claims WHERE id = ?", (c,)).fetchone()
        self.assertEqual((row["status"], row["verified_at"]), ("UNKNOWN", None))

    def test_editing_notes_does_not_reset_a_verified_claim(self):
        c = self.claim("CONFIRMED")
        self.q("UPDATE claims SET notes = 'SAMPLE note' WHERE id = ?", (c,))
        self.assertEqual(self.status_of("claims", c), "CONFIRMED")

    def test_downgrading_a_claim_pulls_ready_scripts_and_episode_back_and_audits(self):
        ep, s, l = self.ready_script()
        self.q("UPDATE episodes SET status = 'READY_TO_RECORD' WHERE id = ?", (ep,))
        claim = self.one("SELECT claim_id FROM line_claims WHERE line_id = ?", (l,))
        before = self.one("SELECT count(*) FROM audit_events WHERE action = 'content.script.demoted'") if self._can_read_audit() else None
        self.q("UPDATE claims SET status = 'UNKNOWN' WHERE id = ?", (claim,))
        self.assertEqual(self.status_of("scripts", s), "IN_REVIEW")
        self.assertEqual(self.status_of("episodes", ep), "SCRIPTING")
        if before is not None:
            self.assertEqual(self.one("SELECT count(*) FROM audit_events WHERE action = 'content.script.demoted'"), before + 1)

    def _can_read_audit(self):
        return True  # overridden for content_app, which may append to but not read the audit log

    def test_downgrading_an_unrelated_claim_leaves_scripts_alone(self):
        _, s, _ = self.ready_script()
        other = self.claim("CONFIRMED", "SAMPLE unrelated")
        self.q("UPDATE claims SET status = 'PLANNED' WHERE id = ?", (other,))
        self.assertEqual(self.status_of("scripts", s), "READY_TO_RECORD")

    def test_locked_script_is_history_and_not_demoted(self):
        _, s, l = self.ready_script()
        self.set_status(s, "LOCKED")
        claim = self.one("SELECT claim_id FROM line_claims WHERE line_id = ?", (l,))
        self.q("UPDATE claims SET status = 'UNKNOWN' WHERE id = ?", (claim,))
        self.assertEqual(self.status_of("scripts", s), "LOCKED")

    def test_claim_codes_are_generated_unique_and_well_formed(self):
        a, b = self.claim(), self.claim()
        codes = [self.one("SELECT code FROM claims WHERE id = ?", (x,)) for x in (a, b)]
        self.assertTrue(all(re.fullmatch(r"C-\d{3,}", c) for c in codes), codes)
        self.assertNotEqual(*codes)
        self.fails(CheckViolation, "INSERT INTO claims(code, statement, project) VALUES ('X-1','SAMPLE','andrew-builds')", rule=False)

    def test_things_in_use_cannot_be_deleted(self):
        ep, s, l = self.ready_script()
        self.set_status(s, "DRAFT")
        claim = self.one("SELECT claim_id FROM line_claims WHERE line_id = ?", (l,))
        src = self.one("SELECT source_id FROM claim_sources WHERE claim_id = ?", (claim,))
        fk = psycopg.errors.ForeignKeyViolation
        self.fails(fk, "DELETE FROM claims WHERE id = ?", (claim,))
        self.fails(fk, "DELETE FROM sources WHERE id = ?", (src,))
        self.fails(fk, "DELETE FROM episodes WHERE id = ?", (ep,))

    # --- episodes
    def test_episode_needs_a_ready_script_before_ready_to_record(self):
        ep = self.episode()
        self.fails(CheckViolation, "UPDATE episodes SET status = 'READY_TO_RECORD' WHERE id = ?", (ep,), "ready_to_record script", rule=True)
        self.fails(CheckViolation, "INSERT INTO episodes(series_id, code, title, status) SELECT id,'E9','SAMPLE','READY_TO_RECORD' FROM series LIMIT 1", rule=True)
        s = self.script(ep)
        self.line(s, 1, "SAMPLE opinion", "OPINION")
        self.set_status(s, "READY_TO_RECORD")
        self.q("UPDATE episodes SET status = 'READY_TO_RECORD' WHERE id = ?", (ep,))
        self.assertEqual(self.status_of("episodes", ep), "READY_TO_RECORD")

    def test_episode_constraints(self):
        sid = self.one("SELECT id FROM series WHERE slug = 'shorts'")
        ep = self.episode()
        self.fails(psycopg.errors.UniqueViolation, "INSERT INTO episodes(series_id, code, title) VALUES (?,?,?)",
                   (self.one("SELECT series_id FROM episodes WHERE id = ?", (ep,)), "E001", "dup"))
        self.fails(CheckViolation, "UPDATE episodes SET parent_episode_id = id WHERE id = ?", (ep,), rule=False)
        self.q("INSERT INTO episodes(series_id, code, title, parent_episode_id, target_duration_s) VALUES (?,?,?,?,45)", (sid, "SH1", "SAMPLE short", ep))
        self.fails(CheckViolation, "UPDATE episodes SET target_duration_s = 0 WHERE id = ?", (ep,), rule=False)
        self.fails(CheckViolation, "UPDATE episodes SET status = 'LIVE' WHERE id = ?", (ep,), rule=False)

    def test_production_and_asset_paths_must_be_relative_and_safe(self):
        ep = self.episode()
        for good in ("production/episode-001/EPISODE_001_MASTER_SCRIPT.md", "production/episode-002/captions/EPISODE_002_long.srt"):
            self.q("UPDATE episodes SET production_path = ? WHERE id = ?", (good, ep))
        for bad in ("/etc/passwd", "production/../secrets.txt", "other/place.md", "production/a b;rm.md", "http://x.example/y"):
            with self.subTest(production_path=bad):
                self.fails(CheckViolation, "UPDATE episodes SET production_path = ? WHERE id = ?", (bad, ep), rule=False)
        for good in ("production/episode-001/captions/EPISODE_001_long_scratch.srt", "graphics/thumb v2.png"):
            self.q("INSERT INTO assets(episode_id, kind, path) VALUES (?, 'caption', ?)", (ep, good))
        for bad in ("/abs/path.png", "../up.png", "a/../b.png", "C:\\win.png", "https://cdn.example/x.png", "  "):
            with self.subTest(asset_path=bad):
                self.fails(CheckViolation, "INSERT INTO assets(episode_id, kind, path) VALUES (?, 'raw', ?)", (ep, bad), rule=False)

    def test_asset_hide_list_result_and_timestamp_go_together(self):
        self.fails(CheckViolation, "INSERT INTO assets(kind, path, hide_list_result) VALUES ('caption','a.srt','PASSED')", rule=False)
        self.fails(CheckViolation, "INSERT INTO assets(kind, path, hide_list_checked_at) VALUES ('caption','a.srt', now())", rule=False)
        self.q("INSERT INTO assets(kind, path, hide_list_result, hide_list_checked_at) VALUES ('caption','a.srt','PASSED', now())")
        self.fails(CheckViolation, "INSERT INTO assets(kind, path, hide_list_result, hide_list_checked_at) VALUES ('caption','b.srt','MAYBE', now())", rule=False)

    # --- posts, metrics
    def _post(self, status="DRAFT"):
        ep = self.episode()
        return self.one("INSERT INTO posts(episode_id, platform) VALUES (?, 'youtube') RETURNING id", (ep,))

    def test_post_status_needs_matching_timestamps(self):
        p = self._post()
        self.fails(CheckViolation, "UPDATE posts SET status = 'APPROVED' WHERE id = ?", (p,), rule=False)
        self.fails(CheckViolation, "UPDATE posts SET status = 'PUBLISHED', approved_at = now() WHERE id = ?", (p,), rule=False)
        self.fails(CheckViolation, "UPDATE posts SET status = 'PUBLISHED', approved_at = now(), published_at = now() - interval '1 day' WHERE id = ?", (p,), rule=False)
        self.q("UPDATE posts SET status = 'PUBLISHED', approved_at = now() - interval '1 hour', published_at = now() WHERE id = ?", (p,))
        self.fails(CheckViolation, "UPDATE posts SET platform = 'facebook' WHERE id = ?", (p,), rule=False)

    def test_metrics_are_append_only_and_manual(self):
        p = self._post()
        m = self.one("INSERT INTO metrics(post_id, views, likes, followers_gained) VALUES (?, 120, 7, -2) RETURNING id", (p,))  # negative net follows is legitimate
        self.assertEqual(self.one("SELECT source FROM metrics WHERE id = ?", (m,)), "manual")
        self.q("INSERT INTO metrics(post_id, views) VALUES (?, 125)", (p,))  # a correction is a new row
        self.assertEqual(self.one("SELECT count(*) FROM metrics WHERE post_id = ?", (p,)), 2)
        denied = (CheckViolation, psycopg.errors.InsufficientPrivilege)  # superuser hits the trigger, content_app hits the missing privilege first
        self.fails(denied, "UPDATE metrics SET views = 999 WHERE id = ?", (m,))
        self.fails(denied, "DELETE FROM metrics WHERE id = ?", (m,))
        self.fails(denied, "TRUNCATE metrics")
        self.fails(CheckViolation, "INSERT INTO metrics(post_id, views) VALUES (?, -1)", (p,), rule=False)
        self.fails(CheckViolation, "INSERT INTO metrics(post_id, source) VALUES (?, 'scraped')", (p,), rule=False)
        self.fails(psycopg.errors.ForeignKeyViolation, "DELETE FROM posts WHERE id = ?", (p,))  # metrics history keeps its post

    # --- course
    def _modules(self, *seconds):
        for i, s in enumerate(seconds, start=1):
            self.q("INSERT INTO course_modules(position, title, duration_s) VALUES (?, ?, ?)", (i, f"SAMPLE module {i}", s))

    def test_course_must_total_exactly_sixty_minutes_to_be_ready(self):
        ready = "UPDATE course_plan SET status = 'READY' WHERE id = 1"
        self.fails(CheckViolation, ready, contains="0:00", rule=True)  # no modules
        self._modules(1800, 1799)
        self.fails(CheckViolation, ready, contains="59:59", rule=True)
        self.q("INSERT INTO course_modules(position, title, duration_s) VALUES (3, 'SAMPLE extra', 2)")  # 3601
        self.fails(CheckViolation, ready, contains="60:01", rule=True)
        self.q("UPDATE course_modules SET duration_s = 1 WHERE position = 3")  # 3600
        self.q(ready)
        self.assertEqual(self.one("SELECT status FROM course_plan"), "READY")

    def test_ready_course_is_frozen_until_set_back_to_draft(self):
        self._modules(1800, 1800)
        self.q("UPDATE course_plan SET status = 'READY' WHERE id = 1")
        for sql in ("INSERT INTO course_modules(position, title, duration_s) VALUES (3,'late',1)", "UPDATE course_modules SET duration_s = 1799 WHERE position = 1",
                    "DELETE FROM course_modules WHERE position = 2"):
            with self.subTest(sql=sql):
                self.fails(CheckViolation, sql, rule=True)
        self.q("UPDATE course_plan SET status = 'DRAFT' WHERE id = 1")
        self.q("UPDATE course_modules SET duration_s = 1799 WHERE position = 1")

    def test_course_plan_is_a_protected_singleton_with_a_fixed_length(self):
        self.fails(CheckViolation, "UPDATE course_plan SET target_duration_s = 3000 WHERE id = 1", rule=False)
        self.fails(CheckViolation, "INSERT INTO course_plan(id, title) VALUES (2, 'second')", rule=False)
        self.fails(CheckViolation, "DELETE FROM course_plan", rule=True)
        self.fails(CheckViolation, "INSERT INTO course_modules(position, title, duration_s) VALUES (1,'x',0)", rule=False)
        self.fails(CheckViolation, "INSERT INTO course_modules(position, title, duration_s) VALUES (1,'x',3601)", rule=False)

    def test_module_positions_are_unique_but_can_be_swapped_in_one_transaction(self):
        self._modules(1800, 1800)
        self.deferred_unique("INSERT INTO course_modules(position, title, duration_s) VALUES (1, 'dup', 10)")
        with self.conn.transaction():
            self.q("UPDATE course_modules SET position = 3 - position")  # swap 1 <-> 2
        self.assertEqual(self.one("SELECT title FROM course_modules WHERE position = 1"), "SAMPLE module 2")

    # --- small tables
    def test_other_constraints(self):
        src = self.source("commit", "SAMPLE commit reference")
        self.q("INSERT INTO moments(occurred_at, kind, project, summary, source_id) VALUES (now(), 'failure', 'agriloop', 'SAMPLE failure', ?)", (src,))
        self.fails(psycopg.errors.NotNullViolation, "INSERT INTO moments(occurred_at, kind, project, summary) VALUES (now(), 'failure', 'agriloop', 'no source')")
        self.fails(CheckViolation, "INSERT INTO moments(occurred_at, kind, project, summary, source_id) VALUES (now(), 'party', 'agriloop', 'x', ?)", (src,), rule=False)
        self.fails(psycopg.errors.ForeignKeyViolation, "DELETE FROM sources WHERE id = ?", (src,))
        self.q("INSERT INTO growth_log(week_start, platform, followers) VALUES ('2026-11-02', 'youtube', 12)")  # a Monday
        self.fails(CheckViolation, "INSERT INTO growth_log(week_start, platform, followers) VALUES ('2026-11-03', 'youtube', 12)", rule=False)
        self.fails(psycopg.errors.UniqueViolation, "INSERT INTO growth_log(week_start, platform, followers) VALUES ('2026-11-02', 'youtube', 13)")
        self.fails(CheckViolation, "INSERT INTO growth_log(week_start, platform, followers) VALUES ('2026-11-09', 'tiktok', -1)", rule=False)
        self.q("INSERT INTO hide_list(term, category) VALUES ('SAMPLE Name', 'person')")
        self.fails(psycopg.errors.UniqueViolation, "INSERT INTO hide_list(term, category) VALUES ('  sample name ', 'person')")
        self.fails(CheckViolation, "INSERT INTO hide_list(term, category) VALUES ('   ', 'other')", rule=False)
        self.fails(CheckViolation, "INSERT INTO hide_list(term, category) VALUES ('x', 'friend')", rule=False)
        self.assertTrue(self.one("SELECT private FROM sources WHERE id = ?", (src,)), "sources are private until the owner says otherwise")
        self.fails(CheckViolation, "INSERT INTO ideas(title, status) VALUES ('x', 'MAYBE')", rule=False)

    def test_script_line_positions_can_be_swapped_in_one_transaction(self):
        s = self.script(self.episode())
        a, b = self.line(s, 1, "SAMPLE a", "OPINION"), self.line(s, 2, "SAMPLE b", "OPINION")
        self.deferred_unique("INSERT INTO script_lines(script_id, position, text, kind) VALUES (?, 1, 'dup', 'OPINION')", (s,))
        with self.conn.transaction():
            self.q("UPDATE script_lines SET position = 3 - position WHERE script_id = ?", (s,))
        self.assertEqual(self.one("SELECT position FROM script_lines WHERE id = ?", (a,)), 2)

    def test_updated_at_is_maintained(self):
        sid = self.one("INSERT INTO sources(kind, reference, created_at, updated_at) VALUES ('url','SAMPLE','2000-01-01','2000-01-01') RETURNING id")
        self.q("UPDATE sources SET reference = 'SAMPLE changed' WHERE id = ?", (sid,))
        self.assertGreater(self.one("SELECT extract(year FROM updated_at) FROM sources WHERE id = ?", (sid,)), 2000)
        self.assertEqual(self.one("SELECT extract(year FROM created_at) FROM sources WHERE id = ?", (sid,)), 2000)

    def test_shots_and_ideas_constraints(self):
        ep = self.episode()
        self.q("INSERT INTO shots(episode_id, code, description) VALUES (?, 'S01', 'SAMPLE shot')", (ep,))
        self.assertEqual(self.one("SELECT status FROM shots WHERE code = 'S01'"), "PLANNED")
        self.fails(psycopg.errors.UniqueViolation, "INSERT INTO shots(episode_id, code) VALUES (?, 'S01')", (ep,))
        self.fails(CheckViolation, "INSERT INTO shots(episode_id, code, status) VALUES (?, 'S02', 'DONE')", (ep,), rule=False)
        self.fails(CheckViolation, "INSERT INTO shots(episode_id, code, checklist) VALUES (?, 'S03', '{}'::jsonb)", (ep,), rule=False)


class RulesAsConnectingRole(RuleTests, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = make_conn()


# ---------------------------------------------------------------------------------------------------------------------
# Row-level security and privileges, as a NON-superuser table owner (what a real Neon DATABASE_URL role is).
# Superusers bypass RLS, so this cannot be tested as one.
# ---------------------------------------------------------------------------------------------------------------------
class OwnerSchema:
    """Class-level fixture: a non-superuser role that owns a fresh schema with all migrations applied by that role."""

    @classmethod
    def setUpClass(cls):
        require_db()
        if not _is_superuser():
            raise unittest.SkipTest("TEST_DATABASE_URL role is not a superuser; RLS tests need to create temporary roles")
        tag = uuid.uuid4().hex[:8]
        cls.owner, cls.probe, cls.schema, cls.pw = f"ab_t_owner_{tag}", f"ab_t_probe_{tag}", f"t_{tag}", secrets.token_hex(12)
        a = _admin()
        a.execute(f"CREATE ROLE {cls.owner} LOGIN CREATEROLE NOSUPERUSER PASSWORD '{cls.pw}'")
        a.execute(f"CREATE ROLE {cls.probe} NOLOGIN")
        a.execute(f"GRANT {cls.probe} TO {cls.owner}")
        a.execute(f'CREATE SCHEMA "{cls.schema}" AUTHORIZATION {cls.owner}')
        # If content_app already exists (created by another test), a CREATEROLE user needs ADMIN OPTION on it, as its creator would have.
        if a.execute("SELECT 1 FROM pg_roles WHERE rolname = 'content_app'").fetchone():
            a.execute(f"GRANT content_app TO {cls.owner} WITH ADMIN OPTION, INHERIT FALSE, SET FALSE")
        a.close()
        u = urlsplit(URL)
        cls.url = urlunsplit((u.scheme, f"{cls.owner}:{cls.pw}@{u.hostname}" + (f":{u.port}" if u.port else ""), u.path, "", ""))
        cls.conn = db.connect(cls.url, schema=cls.schema)
        db.migrate(cls.conn)

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "conn", None) is None:
            return
        cls.conn.close()
        a = _admin()
        a.execute(f'DROP SCHEMA IF EXISTS "{cls.schema}" CASCADE')
        for r in (cls.probe, cls.owner):
            a.execute(f"DROP OWNED BY {r}")
            a.execute(f"DROP ROLE IF EXISTS {r}")
        a.close()


class RulesAsContentApp(RuleTests, OwnerSchema, unittest.TestCase):
    """The whole rule suite again, as the role the API really uses, with the real (minimal) privileges."""

    def enter_role(self):
        self.conn.execute("SET LOCAL ROLE content_app")

    def _can_read_audit(self):
        return False  # content_app may append to audit_events but deliberately cannot read it

    def test_rule_suite_really_runs_as_content_app(self):
        self.assertEqual(self.one("SELECT current_user"), "content_app")


class RlsAndPrivilegesTest(OwnerSchema, unittest.TestCase):
    def setUp(self):
        self._tx = self.conn.raw.transaction(force_rollback=True)
        self._tx.__enter__()

    def tearDown(self):
        self._tx.__exit__(None, None, None)

    def one(self, sql, params=()):
        return self.conn.execute(sql, params).fetchone()[0]

    def denied(self, sql, params=()):
        with self.assertRaises(psycopg.errors.InsufficientPrivilege):
            with self.conn.transaction():
                self.conn.execute(sql, params)

    def test_migration_ran_as_a_non_superuser(self):
        self.assertFalse(self.one("SELECT rolsuper FROM pg_roles WHERE rolname = current_user"))

    def test_rls_is_enabled_and_forced_on_every_content_table(self):
        rows = self.conn.execute("SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class "
                                 "WHERE relnamespace = current_schema()::regnamespace AND relname = ANY(?)", (list(meta.TABLES),)).fetchall()
        self.assertEqual(len(rows), len(meta.TABLES))
        for r in rows:
            self.assertTrue(r["relrowsecurity"] and r["relforcerowsecurity"], r["relname"])
        pols = self.conn.execute("SELECT tablename, roles FROM pg_policies WHERE schemaname = current_schema()").fetchall()
        self.assertEqual({p["tablename"] for p in pols}, set(meta.TABLES))
        for p in pols:
            self.assertEqual(list(p["roles"]), ["content_app"], f"{p['tablename']}: the only policy must be for content_app")

    def test_default_deny_even_the_table_owner_sees_nothing_without_the_role(self):
        self.assertEqual(self.one("SELECT count(*) FROM series"), 0, "FORCE RLS: the owner must not see rows outside content_app")
        self.assertEqual(self.one("SELECT count(*) FROM course_plan"), 0)
        with self.assertRaises(psycopg.errors.InsufficientPrivilege):  # and cannot write either
            with self.conn.transaction():
                self.conn.execute("INSERT INTO series(slug, title) VALUES ('sneaky', 'x')")
        self.conn.execute("SET LOCAL ROLE content_app")
        self.assertEqual(self.one("SELECT count(*) FROM series"), 4)

    def test_an_unrelated_role_with_select_grants_still_sees_nothing(self):
        self.conn.execute(f'GRANT USAGE ON SCHEMA "{self.schema}" TO {self.probe}')
        self.conn.execute(f'GRANT SELECT ON ALL TABLES IN SCHEMA "{self.schema}" TO {self.probe}')
        self.conn.execute(f"SET LOCAL ROLE {self.probe}")
        for t in ("series", "course_plan"):
            self.assertEqual(self.one(f"SELECT count(*) FROM {t}"), 0, t)
        with self.assertRaises(psycopg.errors.InsufficientPrivilege):
            with self.conn.transaction():
                self.conn.execute("INSERT INTO series(slug, title) VALUES ('x', 'y')")

    def test_content_app_cannot_reach_credentials_sessions_or_other_sales_data(self):
        self.conn.execute("SET LOCAL ROLE content_app")
        for t in ("owner_credentials", "sessions", "auth_attempts", "settings", "sales_tasks", "playbooks", "activity_events", "audit_events"):
            with self.subTest(table=t):
                self.denied(f"SELECT count(*) FROM {t}")
        self.denied("SELECT email FROM leads")
        self.denied("SELECT phone, notes FROM leads")
        self.denied("UPDATE leads SET name = 'x'")
        self.denied("CREATE TABLE sneaky (a int)")
        self.denied("CREATE ROLE sneaky")
        self.assertEqual(self.one("SELECT count(*) FROM (SELECT id, name, business, stage FROM leads) x"), 0)  # allowed columns

    def test_content_app_can_append_to_the_audit_log_but_never_change_it(self):
        self.conn.execute("SET LOCAL ROLE content_app")
        self.conn.execute("INSERT INTO audit_events(at, actor, action) VALUES ('2026-11-08T00:00:00+00:00', 'owner', 'content.test')")
        self.denied("UPDATE audit_events SET action = 'x'")
        self.denied("DELETE FROM audit_events")

    def test_metrics_cannot_be_changed_even_by_privilege(self):
        self.conn.execute("SET LOCAL ROLE content_app")
        sid = self.one("SELECT id FROM series LIMIT 1")
        ep = self.one("INSERT INTO episodes(series_id, code, title) VALUES (?, 'M1', 'SAMPLE') RETURNING id", (sid,))
        p = self.one("INSERT INTO posts(episode_id, platform) VALUES (?, 'tiktok') RETURNING id", (ep,))
        m = self.one("INSERT INTO metrics(post_id, views) VALUES (?, 10) RETURNING id", (p,))
        self.denied("UPDATE metrics SET views = 11 WHERE id = ?", (m,))
        self.denied("DELETE FROM metrics WHERE id = ?", (m,))
        self.denied("TRUNCATE metrics")

    def test_deleting_a_prospect_removes_its_content_links_despite_forced_rls(self):
        self.conn.execute("INSERT INTO leads(id, name, created_at) VALUES ('lead_sample', 'SAMPLE Prospect', '2026-11-08')")
        self.conn.execute("SET LOCAL ROLE content_app")
        sid = self.one("SELECT id FROM series LIMIT 1")
        ep = self.one("INSERT INTO episodes(series_id, code, title) VALUES (?, 'L1', 'SAMPLE') RETURNING id", (sid,))
        p = self.one("INSERT INTO posts(episode_id, platform) VALUES (?, 'instagram') RETURNING id", (ep,))
        self.conn.execute("INSERT INTO content_lead_links(post_id, lead_id, cta_code) VALUES (?, 'lead_sample', 'SAMPLE-CTA')", (p,))
        self.assertEqual(self.one("SELECT count(*) FROM content_lead_links"), 1)
        with self.assertRaises(psycopg.errors.UniqueViolation):  # the same prospect cannot be linked to a post twice
            with self.conn.transaction():
                self.conn.execute("INSERT INTO content_lead_links(post_id, lead_id) VALUES (?, 'lead_sample')", (p,))
        self.conn.execute("RESET ROLE")
        self.conn.execute("DELETE FROM leads WHERE id = 'lead_sample'")  # the Outreach Desk's own delete path, run as the connecting role
        self.conn.execute("SET LOCAL ROLE content_app")
        self.assertEqual(self.one("SELECT count(*) FROM content_lead_links"), 0)

    def test_foreign_key_to_leads_rejects_unknown_prospects(self):
        self.conn.execute("SET LOCAL ROLE content_app")
        sid = self.one("SELECT id FROM series LIMIT 1")
        ep = self.one("INSERT INTO episodes(series_id, code, title) VALUES (?, 'L2', 'SAMPLE') RETURNING id", (sid,))
        p = self.one("INSERT INTO posts(episode_id, platform) VALUES (?, 'instagram') RETURNING id", (ep,))
        with self.assertRaises(psycopg.errors.ForeignKeyViolation):
            with self.conn.transaction():
                self.conn.execute("INSERT INTO content_lead_links(post_id, lead_id) VALUES (?, 'no_such_lead')", (p,))


# ---------------------------------------------------------------------------------------------------------------------
# API: authentication, routing, and that it really runs as content_app
# ---------------------------------------------------------------------------------------------------------------------
class ContentApiTest(OwnerSchema, unittest.TestCase):
    ROUTES = [("GET", "/api/content/meta"), ("GET", "/api/content/health"), ("GET", "/api/content/nope"), ("GET", "/api/content/"),
              ("POST", "/api/content/anything"), ("GET", "/api/content")]

    def call(self, method, path, token=None, body=b""):
        code, ctype, out = dash.handle(method, path, ("Bearer " + token) if token else None, self.conn, body)
        return code, json.loads(out)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.token, _, _ = authutil.session(cls.conn)

    def test_every_content_route_is_401_without_a_session(self):
        for method, path in self.ROUTES:
            with self.subTest(route=f"{method} {path}"):
                self.assertEqual(self.call(method, path)[0], 401)
                self.assertEqual(self.call(method, path, "not-a-real-token")[0], 401)
                self.assertEqual(self.call(method, path, "")[0], 401)

    def test_a_revoked_session_is_401(self):
        # revoke the shared token and it must stop working; then restore it for the remaining tests in this class
        self.assertEqual(self.call("GET", "/api/content/meta", self.token)[0], 200)
        authutil.ol.logout(self.conn, self.token)
        self.assertEqual(self.call("GET", "/api/content/meta", self.token)[0], 401)
        self.conn.execute("UPDATE sessions SET revoked = FALSE")  # un-revoke for the remaining tests in this class

    def test_meta_is_served_to_the_owner(self):
        code, body = self.call("GET", "/api/content/meta", self.token)
        self.assertEqual(code, 200)
        self.assertEqual(body["role"], "content_app")
        self.assertEqual(body["course_total_seconds"], 3600)
        self.assertEqual(body["enums"]["claims.status"], ["CONFIRMED", "PARTIALLY_CONFIRMED", "PLANNED", "UNKNOWN"])
        self.assertIn("REFLECTION", body["non_factual_kinds"])
        self.assertTrue(all(w["phase"] for w in body["not_built"]))

    def test_health_runs_as_content_app_and_sees_the_seed_rows(self):
        code, body = self.call("GET", "/api/content/health", self.token)
        self.assertEqual(code, 200)
        self.assertEqual(body["queried_as"], "content_app")
        self.assertTrue(body["content_migrated"] and body["rls_ok"])
        rows = {t["name"]: t["rows"] for t in body["tables"]}
        # The connecting role sees 0 rows here (FORCE RLS). Seeing 4 proves the request ran as content_app.
        self.assertEqual((rows["series"], rows["course_plan"], rows["claims"]), (4, 1, 0))
        self.assertEqual({t["name"] for t in body["tables"]}, set(meta.TABLES))

    def test_unknown_routes_and_methods_are_404_for_the_owner(self):
        for method, path in (("GET", "/api/content/nope"), ("POST", "/api/content/meta"), ("GET", "/api/content/"), ("GET", "/api/content")):
            with self.subTest(route=f"{method} {path}"):
                self.assertEqual(self.call(method, path, self.token)[0], 404)

    def test_the_role_does_not_leak_out_of_a_request(self):
        self.call("GET", "/api/content/health", self.token)
        self.assertEqual(self.one("SELECT current_user"), self.owner)

    def one(self, sql, params=()):
        return self.conn.execute(sql, params).fetchone()[0]

    def test_sales_routes_are_unaffected(self):
        self.assertEqual(self.call("GET", "/api/sales/meta")[0], 401)
        self.assertEqual(self.call("GET", "/api/sales/meta", self.token)[0], 200)


class ErrorTranslationTest(unittest.TestCase):
    def test_rule_message_exposes_only_our_own_messages(self):
        conn = make_conn()
        ep = conn.execute("INSERT INTO episodes(series_id, code, title) SELECT id,'E1','SAMPLE' FROM series LIMIT 1 RETURNING id").fetchone()[0]
        with self.assertRaises(CheckViolation) as ours:
            conn.execute("INSERT INTO scripts(episode_id, version, status) VALUES (?, 1, 'READY_TO_RECORD')", (ep,))
        self.assertIn("claim check", access.rule_message(ours.exception))
        self.assertNotIn("CONTENT_RULE", access.rule_message(ours.exception))
        with self.assertRaises(CheckViolation) as theirs:  # a plain table CHECK: its text (constraint name) must never reach a client
            conn.execute("UPDATE episodes SET status = 'LIVE' WHERE id = ?", (ep,))
        self.assertIsNone(access.rule_message(theirs.exception))
        self.assertIsNone(access.rule_message(ValueError("x")))


# ---------------------------------------------------------------------------------------------------------------------
# Shell: static assets, navigation, offline cache list
# ---------------------------------------------------------------------------------------------------------------------
class ShellTest(unittest.TestCase):
    def test_content_page_script_is_referenced_served_and_cached_offline(self):
        self.assertIn('<script src="/js/content.js"></script>', dash.PAGE)
        self.assertIsNotNone(dash.static_file("/js/content.js"))
        sw = dash.static_file("/sw.js")[1].decode()
        for src in re.findall(r'<script src="(/js/[^"]+)"', dash.PAGE):
            self.assertIn(f'"{src}"', sw, f"{src} is loaded by the page but missing from the service-worker shell list")
        self.assertIn("od-shell-v2", sw, "the shell cache version must be bumped when the shell file list changes")

    def test_content_is_in_the_navigation(self):
        main = dash.static_file("/js/main.js")[1].decode()
        self.assertIn('["content", "Content"]', main)

    def test_content_page_uses_no_innerhtml(self):
        src = dash.static_file("/js/content.js")[1].decode()
        for bad in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval("):
            self.assertNotIn(bad, src)

    def test_csp_still_forbids_inline_script(self):
        self.assertIn("script-src 'self'", dash.HEADERS["Content-Security-Policy"])
        self.assertNotIn("<script>", dash.PAGE.replace('<script src=', ''))


if __name__ == "__main__":
    unittest.main()
