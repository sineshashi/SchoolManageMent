-- upgrade --
ALTER TABLE "class" ADD "active" BOOL NOT NULL  DEFAULT True;
ALTER TABLE "student" ADD "sr_number" VARCHAR(55);
-- downgrade --
ALTER TABLE "class" DROP COLUMN "active";
ALTER TABLE "student" DROP COLUMN "sr_number";
