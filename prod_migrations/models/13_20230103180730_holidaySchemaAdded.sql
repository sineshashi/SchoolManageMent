-- upgrade --
CREATE TABLE IF NOT EXISTS "generalholiday" (
    "holiday_id" SERIAL NOT NULL PRIMARY KEY,
    "start_date" DATE NOT NULL,
    "end_date" DATE NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "non_occasion" BOOL NOT NULL  DEFAULT False,
    "active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "admin_id" INT NOT NULL REFERENCES "admin" ("id") ON DELETE CASCADE,
    "semester_id" INT REFERENCES "academicsessionandsemester" ("semester_id") ON DELETE CASCADE,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_generalholi_start_d_e0096f" ON "generalholiday" ("start_date");
CREATE INDEX IF NOT EXISTS "idx_generalholi_end_dat_915b32" ON "generalholiday" ("end_date");
CREATE INDEX IF NOT EXISTS "idx_generalholi_admin_i_e60286" ON "generalholiday" ("admin_id");
CREATE INDEX IF NOT EXISTS "idx_generalholi_semeste_8fbeac" ON "generalholiday" ("semester_id");;
CREATE TABLE IF NOT EXISTS "weeklyholiday" (
    "holiday_id" SERIAL NOT NULL PRIMARY KEY,
    "day" SMALLINT NOT NULL,
    "active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "admin_id" INT NOT NULL REFERENCES "admin" ("id") ON DELETE CASCADE,
    "semester_id" INT REFERENCES "academicsessionandsemester" ("semester_id") ON DELETE CASCADE,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_weeklyholid_day_b6f86e" ON "weeklyholiday" ("day");
CREATE INDEX IF NOT EXISTS "idx_weeklyholid_active_62debd" ON "weeklyholiday" ("active");
CREATE INDEX IF NOT EXISTS "idx_weeklyholid_admin_i_ceca3d" ON "weeklyholiday" ("admin_id");
CREATE INDEX IF NOT EXISTS "idx_weeklyholid_semeste_6a3f77" ON "weeklyholiday" ("semester_id");
COMMENT ON COLUMN "weeklyholiday"."day" IS 'Day for weekly holiday.';;
CREATE TABLE "generalholiday_classsectionsemester" ("classsectionsemester_id" INT NOT NULL REFERENCES "classsectionsemester" ("section_id") ON DELETE CASCADE,"generalholiday_id" INT NOT NULL REFERENCES "generalholiday" ("holiday_id") ON DELETE CASCADE);
-- downgrade --
DROP TABLE IF EXISTS "generalholiday_classsectionsemester";
DROP TABLE IF EXISTS "generalholiday";
DROP TABLE IF EXISTS "weeklyholiday";
