-- upgrade --
CREATE TABLE IF NOT EXISTS "institutestaffleavedetail" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "admin_id" INT NOT NULL REFERENCES "admin" ("id") ON DELETE CASCADE,
    "session_id" INT NOT NULL REFERENCES "academicsession" ("session_id") ON DELETE CASCADE,
    "staff_id" INT NOT NULL REFERENCES "institutestaff" ("id") ON DELETE CASCADE,
    "leave_id" INT NOT NULL UNIQUE REFERENCES "leavedetail" ("leave_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_institutest_admin_i_354fd3" ON "institutestaffleavedetail" ("admin_id");
CREATE INDEX IF NOT EXISTS "idx_institutest_session_9549bb" ON "institutestaffleavedetail" ("session_id");
CREATE INDEX IF NOT EXISTS "idx_institutest_staff_i_fc3272" ON "institutestaffleavedetail" ("staff_id");
CREATE INDEX IF NOT EXISTS "idx_institutest_leave_i_408afd" ON "institutestaffleavedetail" ("leave_id");
-- downgrade --
DROP TABLE IF EXISTS "institutestaffleavedetail";
