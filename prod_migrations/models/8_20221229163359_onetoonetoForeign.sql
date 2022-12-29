-- upgrade --
ALTER TABLE "parentgaurdian" ADD CONSTRAINT "fk_parentga_userdb_46ef3c66" FOREIGN KEY ("user_id") REFERENCES "userdb" ("user_id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "parentgaurdian" DROP CONSTRAINT "fk_parentga_userdb_46ef3c66";
