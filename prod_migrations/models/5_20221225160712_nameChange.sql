-- upgrade --
ALTER TABLE "classsectionsemester" RENAME COLUMN "id" TO "section_id";
ALTER TABLE "designation" ALTER COLUMN "role" TYPE VARCHAR(255) USING "role"::VARCHAR(255);
-- downgrade --
ALTER TABLE "designation" ALTER COLUMN "role" TYPE VARCHAR(255) USING "role"::VARCHAR(255);
ALTER TABLE "classsectionsemester" RENAME COLUMN "section_id" TO "id";
