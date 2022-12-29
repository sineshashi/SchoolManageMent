-- upgrade --
ALTER TABLE "academicsessionandsemester" ADD "current" BOOL NOT NULL  DEFAULT True;
-- downgrade --
ALTER TABLE "academicsessionandsemester" DROP COLUMN "current";
