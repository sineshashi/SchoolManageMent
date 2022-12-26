-- upgrade --
ALTER TABLE "studentsememster" DROP CONSTRAINT "fk_students_classsec_d37c5784";
ALTER TABLE "classsectionsemester" RENAME COLUMN "section" TO "section_name";
ALTER TABLE "studentsememster" RENAME COLUMN "class_section_id" TO "section_id";
ALTER TABLE "studentsememster" ADD CONSTRAINT "fk_students_classsec_3de40395" FOREIGN KEY ("section_id") REFERENCES "classsectionsemester" ("section_id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "studentsememster" DROP CONSTRAINT "fk_students_classsec_3de40395";
ALTER TABLE "studentsememster" RENAME COLUMN "section_id" TO "class_section_id";
ALTER TABLE "classsectionsemester" RENAME COLUMN "section_name" TO "section";
ALTER TABLE "studentsememster" ADD CONSTRAINT "fk_students_classsec_d37c5784" FOREIGN KEY ("class_section_id") REFERENCES "classsectionsemester" ("section_id") ON DELETE CASCADE;
