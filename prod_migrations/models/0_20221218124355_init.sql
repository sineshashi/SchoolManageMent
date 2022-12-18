-- upgrade --
CREATE TABLE IF NOT EXISTS "trigger" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL UNIQUE,
    "trigger_details" JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_trigger_name_3bb019" ON "trigger" ("name");
CREATE TABLE IF NOT EXISTS "userdb" (
    "user_id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(100) NOT NULL UNIQUE,
    "password" VARCHAR(200) NOT NULL,
    "active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_userdb_usernam_232fdd" ON "userdb" ("username");
CREATE INDEX IF NOT EXISTS "idx_userdb_active_586cba" ON "userdb" ("active");
CREATE INDEX IF NOT EXISTS "idx_userdb_created_826116" ON "userdb" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_userdb_updated_c36733" ON "userdb" ("updated_at");
CREATE TABLE IF NOT EXISTS "appstaff" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(300) NOT NULL,
    "phone_number" VARCHAR(50) NOT NULL UNIQUE,
    "email" VARCHAR(300) NOT NULL UNIQUE,
    "account_number" VARCHAR(250),
    "ifsc_code" VARCHAR(50),
    "account_holder_name" VARCHAR(500),
    "address_line1" TEXT NOT NULL,
    "address_line2" TEXT,
    "address_city" TEXT NOT NULL,
    "address_country" TEXT NOT NULL,
    "address_code" TEXT NOT NULL,
    "active" BOOL NOT NULL  DEFAULT True,
    "blocked" BOOL NOT NULL  DEFAULT False,
    "work_from_home" BOOL NOT NULL  DEFAULT True,
    "pic_url" TEXT,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL,
    "user_id" INT NOT NULL UNIQUE REFERENCES "userdb" ("user_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_appstaff_name_2566af" ON "appstaff" ("name");
CREATE INDEX IF NOT EXISTS "idx_appstaff_phone_n_25a8fd" ON "appstaff" ("phone_number");
CREATE INDEX IF NOT EXISTS "idx_appstaff_email_be88fa" ON "appstaff" ("email");
CREATE INDEX IF NOT EXISTS "idx_appstaff_active_b8768b" ON "appstaff" ("active");
CREATE INDEX IF NOT EXISTS "idx_appstaff_blocked_8c4630" ON "appstaff" ("blocked");
CREATE INDEX IF NOT EXISTS "idx_appstaff_work_fr_c2de71" ON "appstaff" ("work_from_home");
CREATE INDEX IF NOT EXISTS "idx_appstaff_user_id_c4d6f7" ON "appstaff" ("user_id");
CREATE TABLE IF NOT EXISTS "designation" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "role" VARCHAR(255) NOT NULL,
    "role_instance_id" INT NOT NULL,
    "designation" VARCHAR(255) NOT NULL,
    "permissions_json" JSONB NOT NULL,
    "active" BOOL NOT NULL  DEFAULT True,
    "from_time" TIMESTAMP,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "deactivated_at" TIMESTAMP,
    "deactivation_reason" TEXT,
    "user_id" INT NOT NULL REFERENCES "userdb" ("user_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_designation_role_ae4683" ON "designation" ("role");
CREATE INDEX IF NOT EXISTS "idx_designation_role_in_e3dca1" ON "designation" ("role_instance_id");
CREATE INDEX IF NOT EXISTS "idx_designation_designa_616555" ON "designation" ("designation");
COMMENT ON COLUMN "designation"."role" IS 'appstaff: appstaff\nsuperadmin: superadmin\nadmin: admin\ninstitutestaff: institutestaff';
CREATE TABLE IF NOT EXISTS "superadmin" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "phone_number" VARCHAR(50) NOT NULL UNIQUE,
    "email" VARCHAR(300) NOT NULL UNIQUE,
    "account_number" VARCHAR(250),
    "ifsc_code" VARCHAR(50),
    "account_holder_name" VARCHAR(500),
    "address_line1" TEXT NOT NULL,
    "address_line2" TEXT,
    "address_city" TEXT NOT NULL,
    "address_country" TEXT NOT NULL,
    "address_code" TEXT NOT NULL,
    "active" BOOL NOT NULL  DEFAULT True,
    "blocked" BOOL NOT NULL  DEFAULT False,
    "pic_url" TEXT,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "created_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL,
    "user_id" INT NOT NULL REFERENCES "userdb" ("user_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_superadmin_phone_n_33836d" ON "superadmin" ("phone_number");
CREATE INDEX IF NOT EXISTS "idx_superadmin_email_af15c7" ON "superadmin" ("email");
CREATE INDEX IF NOT EXISTS "idx_superadmin_active_d1d919" ON "superadmin" ("active");
CREATE INDEX IF NOT EXISTS "idx_superadmin_blocked_7b9310" ON "superadmin" ("blocked");
CREATE INDEX IF NOT EXISTS "idx_superadmin_user_id_efa060" ON "superadmin" ("user_id");
CREATE TABLE IF NOT EXISTS "admin" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "phone_number" VARCHAR(50) NOT NULL UNIQUE,
    "email" VARCHAR(300) NOT NULL UNIQUE,
    "account_number" VARCHAR(250),
    "ifsc_code" VARCHAR(50),
    "account_holder_name" VARCHAR(500),
    "address_line1" TEXT NOT NULL,
    "address_line2" TEXT,
    "address_city" TEXT NOT NULL,
    "address_country" TEXT NOT NULL,
    "address_code" TEXT NOT NULL,
    "active" BOOL NOT NULL  DEFAULT True,
    "blocked" BOOL NOT NULL  DEFAULT False,
    "pic_url" TEXT,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "created_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL,
    "super_admin_id" INT NOT NULL REFERENCES "superadmin" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "userdb" ("user_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_admin_phone_n_1a9e69" ON "admin" ("phone_number");
CREATE INDEX IF NOT EXISTS "idx_admin_email_f3e751" ON "admin" ("email");
CREATE INDEX IF NOT EXISTS "idx_admin_active_67ddeb" ON "admin" ("active");
CREATE INDEX IF NOT EXISTS "idx_admin_blocked_5df5b8" ON "admin" ("blocked");
CREATE INDEX IF NOT EXISTS "idx_admin_user_id_cd9f3b" ON "admin" ("user_id");
CREATE TABLE IF NOT EXISTS "institutestaff" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "super_admin_level" BOOL NOT NULL  DEFAULT False,
    "name" VARCHAR(500) NOT NULL,
    "phone_number" VARCHAR(20) NOT NULL UNIQUE,
    "email" VARCHAR(500) NOT NULL UNIQUE,
    "father_name" VARCHAR(500) NOT NULL,
    "mother_name" VARCHAR(500) NOT NULL,
    "dob" DATE NOT NULL,
    "account_number" VARCHAR(50),
    "ifsc_code" VARCHAR(20),
    "account_holder_name" VARCHAR(500),
    "address_line1" TEXT NOT NULL,
    "address_line2" TEXT,
    "address_city" TEXT NOT NULL,
    "address_country" TEXT NOT NULL,
    "address_code" TEXT NOT NULL,
    "alternate_phone_number" VARCHAR(20)  UNIQUE,
    "alternate_email" VARCHAR(500)  UNIQUE,
    "alternate_address_line1" TEXT,
    "alternate_address_line2" TEXT,
    "alternate_address_city" TEXT,
    "alternate_address_country" TEXT,
    "alternate_address_code" TEXT,
    "active" BOOL NOT NULL  DEFAULT True,
    "blocked" BOOL NOT NULL  DEFAULT False,
    "pic_url" TEXT,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "admin_id" INT NOT NULL REFERENCES "admin" ("id") ON DELETE CASCADE,
    "created_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL,
    "user_id" INT NOT NULL REFERENCES "userdb" ("user_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_institutest_super_a_7b632c" ON "institutestaff" ("super_admin_level");
CREATE INDEX IF NOT EXISTS "idx_institutest_name_213fe1" ON "institutestaff" ("name");
CREATE INDEX IF NOT EXISTS "idx_institutest_phone_n_599f81" ON "institutestaff" ("phone_number");
CREATE INDEX IF NOT EXISTS "idx_institutest_active_c92de9" ON "institutestaff" ("active");
CREATE INDEX IF NOT EXISTS "idx_institutest_blocked_94fb01" ON "institutestaff" ("blocked");
CREATE INDEX IF NOT EXISTS "idx_institutest_admin_i_f4973d" ON "institutestaff" ("admin_id");
CREATE INDEX IF NOT EXISTS "idx_institutest_user_id_fba12b" ON "institutestaff" ("user_id");
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
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
