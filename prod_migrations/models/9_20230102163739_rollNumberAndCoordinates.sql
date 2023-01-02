-- upgrade --
ALTER TABLE "admin" ADD "coordinates" TEXT;
ALTER TABLE "studentsememster" ADD "roll_number" VARCHAR(7);
-- downgrade --
ALTER TABLE "admin" DROP COLUMN "coordinates";
ALTER TABLE "studentsememster" DROP COLUMN "roll_number";
