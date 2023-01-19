-- upgrade --
CREATE TABLE IF NOT EXISTS "adminleaveconfig" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "staff_leaves" JSONB NOT NULL,
    "student_leaves" JSONB NOT NULL,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "admin_id" INT NOT NULL REFERENCES "admin" ("id") ON DELETE CASCADE,
    "session_id" INT NOT NULL REFERENCES "academicsession" ("session_id") ON DELETE CASCADE,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_adminleavec_admin_i_6071a9" ON "adminleaveconfig" ("admin_id");
CREATE INDEX IF NOT EXISTS "idx_adminleavec_session_55d232" ON "adminleaveconfig" ("session_id");
-- downgrade --
DROP TABLE IF EXISTS "adminleaveconfig";
