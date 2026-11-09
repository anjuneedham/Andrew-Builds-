import unittest
from urllib.parse import urlsplit, parse_qsl

from core import db


class DatabaseUrl(unittest.TestCase):
    def test_prefers_database_url(self):
        env = {"DATABASE_URL": "postgresql://a:b@h1/db", "POSTGRES_URL": "postgres://c:d@h2/db"}
        self.assertEqual(db.database_url(env), "postgresql://a:b@h1/db")

    def test_falls_back_to_integration_vars_pooled_first(self):
        env = {"POSTGRES_URL_NON_POOLING": "postgres://x:y@direct/db", "POSTGRES_URL": "postgres://c:d@pool/db"}
        self.assertEqual(db.database_url(env), "postgres://c:d@pool/db")
        self.assertEqual(db.database_url({"POSTGRES_URL_NON_POOLING": "postgres://x:y@direct/db"}), "postgres://x:y@direct/db")

    def test_strips_options_psycopg_rejects_keeps_sslmode(self):
        env = {"POSTGRES_URL": "postgres://u:p@h:6543/postgres?sslmode=require&supa=base-pooler.x&pgbouncer=true"}
        out = db.database_url(env)
        q = dict(parse_qsl(urlsplit(out).query))
        self.assertEqual(q, {"sslmode": "require"})
        self.assertEqual(urlsplit(out).netloc, "u:p@h:6543")

    def test_ignores_non_postgres_values_and_empty(self):
        self.assertEqual(db.database_url({"DATABASE_URL": "mysql://x", "POSTGRES_URL": ""}), "")
        self.assertEqual(db.database_url({}), "")


if __name__ == "__main__":
    unittest.main()
