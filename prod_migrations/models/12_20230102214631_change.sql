-- upgrade --
ALTER TABLE "student" ALTER COLUMN "email" DROP NOT NULL;
-- downgrade --
ALTER TABLE "student" ALTER COLUMN "email" SET NOT NULL;
