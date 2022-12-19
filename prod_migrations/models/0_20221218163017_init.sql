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
    "address_line_1" TEXT NOT NULL,
    "address_line_2" TEXT,
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
CREATE TABLE IF NOT EXISTS "parentgaurdian" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "first_name" VARCHAR(500) NOT NULL,
    "middle_name" VARCHAR(500) NOT NULL  DEFAULT '',
    "last_name" VARCHAR(500) NOT NULL  DEFAULT '',
    "date_of_birth" DATE,
    "email" TEXT,
    "phone_number" TEXT,
    "identity_type" VARCHAR(255),
    "identity_number" VARCHAR(255),
    "identity_docurl" TEXT,
    "account_number" VARCHAR(50),
    "ifsc_code" VARCHAR(20),
    "account_holder_name" VARCHAR(500),
    "address_line_1" TEXT,
    "address_line_2" TEXT,
    "address_city" TEXT,
    "address_country" TEXT NOT NULL,
    "address_code" TEXT,
    "alternate_phone_number" VARCHAR(20)  UNIQUE,
    "alternate_email" VARCHAR(500)  UNIQUE,
    "alternate_address_line_1" TEXT,
    "alternate_address_line_2" TEXT,
    "alternate_address_city" TEXT,
    "alternate_address_country" TEXT,
    "alternate_address_code" TEXT,
    "active" BOOL NOT NULL  DEFAULT True,
    "blocked" BOOL NOT NULL  DEFAULT False,
    "pic_url" TEXT,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_parentgaurd_first_n_d32f4e" ON "parentgaurdian" ("first_name");
CREATE INDEX IF NOT EXISTS "idx_parentgaurd_active_25458f" ON "parentgaurdian" ("active");
CREATE INDEX IF NOT EXISTS "idx_parentgaurd_blocked_f4ea54" ON "parentgaurdian" ("blocked");
CREATE TABLE IF NOT EXISTS "superadmin" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "phone_number" VARCHAR(50) NOT NULL UNIQUE,
    "email" VARCHAR(300) NOT NULL UNIQUE,
    "account_number" VARCHAR(250),
    "ifsc_code" VARCHAR(50),
    "account_holder_name" VARCHAR(500),
    "address_line_1" TEXT NOT NULL,
    "address_line_2" TEXT,
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
    "address_line_1" TEXT NOT NULL,
    "address_line_2" TEXT,
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
CREATE TABLE IF NOT EXISTS "academicsessionandsemester" (
    "semester_id" SERIAL NOT NULL PRIMARY KEY,
    "academic_session_start_year" INT NOT NULL,
    "academic_session_end_year" INT NOT NULL,
    "academic_session_start_date" DATE,
    "semester_number" INT NOT NULL  DEFAULT 0,
    "semester_start_date" DATE,
    "semester_end_date" DATE,
    "active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "admin_id" INT NOT NULL REFERENCES "admin" ("id") ON DELETE CASCADE,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_academicses_academi_7d70cb" ON "academicsessionandsemester" ("academic_session_end_year");
CREATE INDEX IF NOT EXISTS "idx_academicses_active_1e8543" ON "academicsessionandsemester" ("active");
CREATE INDEX IF NOT EXISTS "idx_academicses_admin_i_5865f6" ON "academicsessionandsemester" ("admin_id");
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
    "address_line_1" TEXT NOT NULL,
    "address_line_2" TEXT,
    "address_city" TEXT NOT NULL,
    "address_country" TEXT NOT NULL,
    "address_code" TEXT NOT NULL,
    "alternate_phone_number" VARCHAR(20)  UNIQUE,
    "alternate_email" VARCHAR(500)  UNIQUE,
    "alternate_address_line_1" TEXT,
    "alternate_address_line_2" TEXT,
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
CREATE TABLE IF NOT EXISTS "classgroupdepartment" (
    "group_id" SERIAL NOT NULL PRIMARY KEY,
    "group_name" VARCHAR(255) NOT NULL,
    "active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "admin_id" INT NOT NULL REFERENCES "admin" ("id") ON DELETE CASCADE,
    "head_id" INT REFERENCES "institutestaff" ("id") ON DELETE SET NULL,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL,
    "vice_head_id" INT REFERENCES "institutestaff" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_classgroupd_active_f2178b" ON "classgroupdepartment" ("active");
CREATE INDEX IF NOT EXISTS "idx_classgroupd_admin_i_2d10f5" ON "classgroupdepartment" ("admin_id");
CREATE TABLE IF NOT EXISTS "class" (
    "class_id" SERIAL NOT NULL PRIMARY KEY,
    "class_name" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "admin_id" INT NOT NULL REFERENCES "admin" ("id") ON DELETE CASCADE,
    "class_group_id" INT NOT NULL REFERENCES "classgroupdepartment" ("group_id") ON DELETE CASCADE,
    "head_id" INT REFERENCES "institutestaff" ("id") ON DELETE SET NULL,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL,
    "vice_head_id" INT REFERENCES "institutestaff" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_class_class_n_0ae2d2" ON "class" ("class_name");
CREATE INDEX IF NOT EXISTS "idx_class_admin_i_8d56fc" ON "class" ("admin_id");
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
CREATE TABLE IF NOT EXISTS "student" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "first_name" VARCHAR(500) NOT NULL,
    "middle_name" VARCHAR(500) NOT NULL  DEFAULT '',
    "last_name" VARCHAR(500) NOT NULL  DEFAULT '',
    "date_of_birth" DATE NOT NULL,
    "email" TEXT NOT NULL,
    "phone_number" TEXT NOT NULL,
    "identity_type" VARCHAR(255),
    "identity_number" VARCHAR(255),
    "identity_docurl" TEXT,
    "account_number" VARCHAR(50),
    "ifsc_code" VARCHAR(20),
    "account_holder_name" VARCHAR(500),
    "address_line_1" TEXT NOT NULL,
    "address_line_2" TEXT NOT NULL,
    "address_city" TEXT NOT NULL,
    "address_country" TEXT NOT NULL,
    "address_code" TEXT NOT NULL,
    "gaurdian_relation" VARCHAR(255),
    "alternate_phone_number" VARCHAR(20)  UNIQUE,
    "alternate_email" VARCHAR(500)  UNIQUE,
    "alternate_address_line_1" TEXT,
    "alternate_address_line_2" TEXT,
    "alternate_address_city" TEXT,
    "alternate_address_country" TEXT,
    "alternate_address_code" TEXT,
    "active" BOOL NOT NULL  DEFAULT True,
    "blocked" BOOL NOT NULL  DEFAULT False,
    "pic_url" TEXT,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "admin_id" INT NOT NULL REFERENCES "admin" ("id") ON DELETE CASCADE,
    "father_id" INT REFERENCES "parentgaurdian" ("id") ON DELETE SET NULL,
    "gaurdian_id" INT REFERENCES "parentgaurdian" ("id") ON DELETE SET NULL,
    "mother_id" INT REFERENCES "parentgaurdian" ("id") ON DELETE SET NULL,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL,
    "user_id" INT NOT NULL REFERENCES "userdb" ("user_id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_student_first_n_549a08" ON "student" ("first_name");
CREATE INDEX IF NOT EXISTS "idx_student_active_896362" ON "student" ("active");
CREATE INDEX IF NOT EXISTS "idx_student_blocked_5f94b2" ON "student" ("blocked");
CREATE INDEX IF NOT EXISTS "idx_student_user_id_b8e15d" ON "student" ("user_id");
CREATE TABLE IF NOT EXISTS "classsectionsemester" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "section" VARCHAR(255),
    "active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "admin_id" INT NOT NULL REFERENCES "admin" ("id") ON DELETE CASCADE,
    "class_monitor_id" INT REFERENCES "student" ("id") ON DELETE SET NULL,
    "class_teacher_id" INT REFERENCES "institutestaff" ("id") ON DELETE SET NULL,
    "school_class_id" INT NOT NULL REFERENCES "class" ("class_id") ON DELETE CASCADE,
    "semester_id" INT REFERENCES "academicsessionandsemester" ("semester_id") ON DELETE SET NULL,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL,
    "vice_class_monitor_id" INT REFERENCES "student" ("id") ON DELETE SET NULL,
    "vice_class_teacher_id" INT REFERENCES "institutestaff" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_classsectio_section_8c0b89" ON "classsectionsemester" ("section");
CREATE INDEX IF NOT EXISTS "idx_classsectio_active_233320" ON "classsectionsemester" ("active");
CREATE INDEX IF NOT EXISTS "idx_classsectio_admin_i_7b376c" ON "classsectionsemester" ("admin_id");
CREATE INDEX IF NOT EXISTS "idx_classsectio_school__379a9d" ON "classsectionsemester" ("school_class_id");
CREATE INDEX IF NOT EXISTS "idx_classsectio_semeste_6ff00d" ON "classsectionsemester" ("semester_id");
CREATE TABLE IF NOT EXISTS "studentsememster" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "admin_id" INT NOT NULL REFERENCES "admin" ("id") ON DELETE CASCADE,
    "class_section_id" INT NOT NULL REFERENCES "classsectionsemester" ("id") ON DELETE CASCADE,
    "student_id" INT NOT NULL REFERENCES "student" ("id") ON DELETE CASCADE,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_studentseme_active_228897" ON "studentsememster" ("active");
CREATE INDEX IF NOT EXISTS "idx_studentseme_admin_i_e6d0f1" ON "studentsememster" ("admin_id");
CREATE INDEX IF NOT EXISTS "idx_studentseme_class_s_fa85ba" ON "studentsememster" ("class_section_id");
CREATE INDEX IF NOT EXISTS "idx_studentseme_student_144e22" ON "studentsememster" ("student_id");
CREATE TABLE IF NOT EXISTS "subjectgroupdepartment" (
    "group_id" SERIAL NOT NULL PRIMARY KEY,
    "group_name" VARCHAR(255) NOT NULL,
    "active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "admin_id" INT NOT NULL REFERENCES "admin" ("id") ON DELETE CASCADE,
    "head_id" INT REFERENCES "institutestaff" ("id") ON DELETE SET NULL,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL,
    "vice_head_id" INT REFERENCES "institutestaff" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_subjectgrou_active_c57767" ON "subjectgroupdepartment" ("active");
CREATE INDEX IF NOT EXISTS "idx_subjectgrou_admin_i_b27973" ON "subjectgroupdepartment" ("admin_id");
CREATE TABLE IF NOT EXISTS "subject" (
    "subject_id" SERIAL NOT NULL PRIMARY KEY,
    "subject_name" VARCHAR(255) NOT NULL,
    "active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "admin_id" INT NOT NULL REFERENCES "admin" ("id") ON DELETE CASCADE,
    "head_id" INT REFERENCES "institutestaff" ("id") ON DELETE SET NULL,
    "subject_group_id" INT NOT NULL REFERENCES "subjectgroupdepartment" ("group_id") ON DELETE CASCADE,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL,
    "vice_head_id" INT REFERENCES "institutestaff" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_subject_subject_38e66a" ON "subject" ("subject_name");
CREATE INDEX IF NOT EXISTS "idx_subject_active_7429b6" ON "subject" ("active");
CREATE INDEX IF NOT EXISTS "idx_subject_admin_i_b6eb41" ON "subject" ("admin_id");
CREATE TABLE IF NOT EXISTS "sectionsubject" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP,
    "admin_id" INT NOT NULL REFERENCES "admin" ("id") ON DELETE CASCADE,
    "assosiate_subject_teacher_id" INT REFERENCES "institutestaff" ("id") ON DELETE SET NULL,
    "section_id" INT NOT NULL REFERENCES "classsectionsemester" ("id") ON DELETE CASCADE,
    "subject_id" INT NOT NULL REFERENCES "subject" ("subject_id") ON DELETE CASCADE,
    "subject_teacher_id" INT REFERENCES "institutestaff" ("id") ON DELETE SET NULL,
    "updated_by_id" INT REFERENCES "userdb" ("user_id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_sectionsubj_active_b987a5" ON "sectionsubject" ("active");
CREATE INDEX IF NOT EXISTS "idx_sectionsubj_admin_i_b0f6b4" ON "sectionsubject" ("admin_id");
CREATE INDEX IF NOT EXISTS "idx_sectionsubj_assosia_7c85e5" ON "sectionsubject" ("assosiate_subject_teacher_id");
CREATE INDEX IF NOT EXISTS "idx_sectionsubj_section_24652d" ON "sectionsubject" ("section_id");
CREATE INDEX IF NOT EXISTS "idx_sectionsubj_subject_703fcc" ON "sectionsubject" ("subject_id");
CREATE INDEX IF NOT EXISTS "idx_sectionsubj_subject_2f8f59" ON "sectionsubject" ("subject_teacher_id");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "class_subject" (
    "class_id" INT NOT NULL REFERENCES "class" ("class_id") ON DELETE SET NULL,
    "subject_id" INT NOT NULL REFERENCES "subject" ("subject_id") ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS "students_with_subject" (
    "studentsememster_id" INT NOT NULL REFERENCES "studentsememster" ("id") ON DELETE CASCADE,
    "SET NULL" INT NOT NULL REFERENCES "sectionsubject" ("id") ON DELETE CASCADE
);
