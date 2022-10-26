-- upgrade --
CREATE TABLE IF NOT EXISTS "educationdetail" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "level" VARCHAR(55) NOT NULL,
    "course" TEXT NOT NULL,
    "semester_or_year" INT NOT NULL  DEFAULT 0,
    "roll_number" INT,
    "year" INT NOT NULL,
    "institute_name" TEXT NOT NULL,
    "board_or_university" TEXT NOT NULL,
    "status" VARCHAR(20) NOT NULL,
    "subjects" JSONB NOT NULL,
    "obtained_marks" DOUBLE PRECISION,
    "maximum_marks" DOUBLE PRECISION,
    "grade" VARCHAR(20),
    "docurl" TEXT,
    "active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "institute_staff_id" INT NOT NULL REFERENCES "institutestaff" ("id") ON DELETE CASCADE,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_educationde_level_c949e5" ON "educationdetail" ("level");
CREATE INDEX IF NOT EXISTS "idx_educationde_active_149afc" ON "educationdetail" ("active");
CREATE INDEX IF NOT EXISTS "idx_educationde_institu_3bd307" ON "educationdetail" ("institute_staff_id");
COMMENT ON COLUMN "educationdetail"."level" IS 'high_school: High School Or Equivalent\nintermediate: Intermediate Or Equivalent\ngraduation: Graduation\npost_graduation: Post Graduation\nhigher_education: Higher Education\nfield_specific: Specific Courses like B.Ed. etc.\nother: Other';
COMMENT ON COLUMN "educationdetail"."status" IS 'passed: Passed\nfailed: Failed\nappearing: Appearing';
-- downgrade --
DROP TABLE IF EXISTS "educationdetail";
