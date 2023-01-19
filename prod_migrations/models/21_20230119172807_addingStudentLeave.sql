-- upgrade --
CREATE TABLE IF NOT EXISTS "studentleavedetail" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "admin_id" INT NOT NULL REFERENCES "admin" ("id") ON DELETE CASCADE,
    "section_id" INT NOT NULL REFERENCES "classsectionsemester" ("section_id") ON DELETE CASCADE,
    "session_id" INT NOT NULL REFERENCES "academicsession" ("session_id") ON DELETE CASCADE,
    "student_id" INT NOT NULL REFERENCES "student" ("id") ON DELETE CASCADE,
    "leave_id" INT NOT NULL UNIQUE REFERENCES "leavedetail" ("leave_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_studentleav_admin_i_0463d2" ON "studentleavedetail" ("admin_id");
CREATE INDEX IF NOT EXISTS "idx_studentleav_section_795dc5" ON "studentleavedetail" ("section_id");
CREATE INDEX IF NOT EXISTS "idx_studentleav_session_a87f6f" ON "studentleavedetail" ("session_id");
CREATE INDEX IF NOT EXISTS "idx_studentleav_student_a07336" ON "studentleavedetail" ("student_id");
CREATE INDEX IF NOT EXISTS "idx_studentleav_leave_i_b40ac9" ON "studentleavedetail" ("leave_id");
-- downgrade --
DROP TABLE IF EXISTS "studentleavedetail";
