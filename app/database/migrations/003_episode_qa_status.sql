-- Adds the QA stage to episode status: EDITING -> QA -> READY_TO_PUBLISH (decision Q8, approved by Andrew).
-- Additive and re-runnable: replaces only the episodes.status CHECK; no data is touched, every existing value stays valid.
DO $$
DECLARE c RECORD;
BEGIN
  FOR c IN SELECT conname FROM pg_constraint
            WHERE conrelid = 'episodes'::regclass AND contype = 'c' AND pg_get_constraintdef(oid) LIKE '%READY_TO_RECORD%'
              AND pg_get_constraintdef(oid) LIKE '%IDEA%' LOOP
    EXECUTE format('ALTER TABLE episodes DROP CONSTRAINT %I', c.conname);
  END LOOP;
  ALTER TABLE episodes ADD CONSTRAINT episodes_status_check CHECK (status IN
    ('IDEA','SCRIPTING','READY_TO_RECORD','RECORDED','EDITING','QA','READY_TO_PUBLISH','PUBLISHED','ARCHIVED'));
END $$;
