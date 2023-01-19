-- upgrade --
CREATE TABLE IF NOT EXISTS "meeting" (
    "meeting_id" SERIAL NOT NULL PRIMARY KEY,
    "date" DATE NOT NULL,
    "meeting" SMALLINT NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_meeting_date_4f6c4f" ON "meeting" ("date");
CREATE INDEX IF NOT EXISTS "idx_meeting_meeting_145408" ON "meeting" ("meeting");
COMMENT ON COLUMN "meeting"."meeting" IS 'first: 0\nsecond: 1';
-- downgrade --
DROP TABLE IF EXISTS "meeting";
