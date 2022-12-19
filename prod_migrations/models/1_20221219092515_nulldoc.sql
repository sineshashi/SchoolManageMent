-- upgrade --
ALTER TABLE "admin" ADD "dob" DATE;
ALTER TABLE "appstaff" ADD "dob" DATE;
ALTER TABLE "parentgaurdian" ALTER COLUMN "date_of_birth" SET NOT NULL;
ALTER TABLE "superadmin" ADD "dob" DATE;
-- downgrade --
ALTER TABLE "admin" DROP COLUMN "dob";
ALTER TABLE "appstaff" DROP COLUMN "dob";
ALTER TABLE "superadmin" DROP COLUMN "dob";
ALTER TABLE "parentgaurdian" ALTER COLUMN "date_of_birth" DROP NOT NULL;
