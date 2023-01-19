-- upgrade --
CREATE TABLE IF NOT EXISTS "leavedetail" (
    "leave_id" SERIAL NOT NULL PRIMARY KEY,
    "leave_type" VARCHAR(25) NOT NULL,
    "leave_status" VARCHAR(20) NOT NULL,
    "authorizer" VARCHAR(25) NOT NULL,
    "reacted_by" VARCHAR(25),
    "reacted_at" TIMESTAMP,
    "active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMP,
    "description" TEXT,
    "docurl" TEXT,
    "updated_at" TIMESTAMP,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL,
    "leave_end_id" INT NOT NULL UNIQUE REFERENCES "meeting" ("meeting_id") ON DELETE CASCADE,
    "leave_start_id" INT NOT NULL UNIQUE REFERENCES "meeting" ("meeting_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_leavedetail_leave_t_6b5c6d" ON "leavedetail" ("leave_type");
CREATE INDEX IF NOT EXISTS "idx_leavedetail_leave_s_0101f3" ON "leavedetail" ("leave_status");
CREATE INDEX IF NOT EXISTS "idx_leavedetail_authori_582c8c" ON "leavedetail" ("authorizer");
CREATE INDEX IF NOT EXISTS "idx_leavedetail_reacted_e52107" ON "leavedetail" ("reacted_by");
CREATE INDEX IF NOT EXISTS "idx_leavedetail_created_3769c1" ON "leavedetail" ("created_at");
COMMENT ON COLUMN "leavedetail"."leave_type" IS 'causal: causal\noptional_holiday: optional_holiday\nsick_leave: sick_leave\nunpaid_leave: unpaid_leave\npaternity_leave: paternity_leave\nmaternaity_leave: maternity_leave\nprivilege_leave: privilege';
COMMENT ON COLUMN "leavedetail"."leave_status" IS 'approved: Approved\npending: Pending\nrejected: Rejected';
COMMENT ON COLUMN "leavedetail"."authorizer" IS 'class_teacher: Class Teacher\nvice_class_teacher: Vice Class Teacher\nprincipal: Principal\nmanaging_director: Managing Director';
COMMENT ON COLUMN "leavedetail"."reacted_by" IS 'class_teacher: Class Teacher\nvice_class_teacher: Vice Class Teacher\nprincipal: Principal\nmanaging_director: Managing Director';
-- downgrade --
DROP TABLE IF EXISTS "leavedetail";
