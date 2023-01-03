-- upgrade --
ALTER TABLE "generalholiday" ALTER COLUMN "picurl" TYPE TEXT USING "picurl"::TEXT;
-- downgrade --
ALTER TABLE "generalholiday" ALTER COLUMN "description" TYPE TEXT USING "description"::TEXT;
