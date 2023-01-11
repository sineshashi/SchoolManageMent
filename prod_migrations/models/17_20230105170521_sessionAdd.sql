-- upgrade --
CREATE TABLE IF NOT EXISTS "academicsession" (
    "session_id" SERIAL NOT NULL PRIMARY KEY,
    "academic_session_start_year" INT NOT NULL,
    "academic_session_end_year" INT NOT NULL,
    "current" BOOL NOT NULL  DEFAULT True,
    "active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "admin_id" INT NOT NULL REFERENCES "admin" ("id") ON DELETE CASCADE,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_academicses_academi_e02c8b" ON "academicsession" ("academic_session_end_year");
CREATE INDEX IF NOT EXISTS "idx_academicses_current_81e452" ON "academicsession" ("current");
CREATE INDEX IF NOT EXISTS "idx_academicses_active_f411c5" ON "academicsession" ("active");
CREATE INDEX IF NOT EXISTS "idx_academicses_admin_i_f0c55d" ON "academicsession" ("admin_id");;
ALTER TABLE "academicsessionandsemester" ADD "session_id" INT NOT NULL;
ALTER TABLE "academicsessionandsemester" DROP COLUMN "academic_session_start_date";
ALTER TABLE "academicsessionandsemester" DROP COLUMN "academic_session_start_year";
ALTER TABLE "academicsessionandsemester" DROP COLUMN "academic_session_end_year";
ALTER TABLE "academicsessionandsemester" ADD CONSTRAINT "fk_academic_academic_5b596746" FOREIGN KEY ("session_id") REFERENCES "academicsession" ("session_id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "academicsessionandsemester" DROP CONSTRAINT "fk_academic_academic_5b596746";
ALTER TABLE "academicsessionandsemester" ADD "academic_session_start_date" DATE;
ALTER TABLE "academicsessionandsemester" ADD "academic_session_start_year" INT NOT NULL;
ALTER TABLE "academicsessionandsemester" ADD "academic_session_end_year" INT NOT NULL;
ALTER TABLE "academicsessionandsemester" DROP COLUMN "session_id";
DROP TABLE IF EXISTS "academicsession";
