-- upgrade --
ALTER TABLE "parentgaurdian" ADD "is_gaurdian" BOOL NOT NULL  DEFAULT False;
ALTER TABLE "parentgaurdian" ADD "prename" VARCHAR(20);
ALTER TABLE "parentgaurdian" ADD "user_id" INT  UNIQUE;
ALTER TABLE "student" ADD "gender" VARCHAR(20);
-- downgrade --
ALTER TABLE "student" DROP COLUMN "gender";
ALTER TABLE "parentgaurdian" DROP COLUMN "is_gaurdian";
ALTER TABLE "parentgaurdian" DROP COLUMN "prename";
ALTER TABLE "parentgaurdian" DROP COLUMN "user_id";
