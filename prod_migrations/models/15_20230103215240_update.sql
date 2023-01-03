-- upgrade --
ALTER TABLE "generalholiday" ADD "picurl" TEXT;
-- downgrade --
ALTER TABLE "generalholiday" DROP COLUMN "picurl";
