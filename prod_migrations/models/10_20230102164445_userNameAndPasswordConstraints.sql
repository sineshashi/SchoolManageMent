-- upgrade --
ALTER TABLE "userdb" ALTER COLUMN "username" TYPE VARCHAR(20) USING "username"::VARCHAR(20);
ALTER TABLE "userdb" ALTER COLUMN "password" TYPE VARCHAR(16) USING "password"::VARCHAR(16);
-- downgrade --
ALTER TABLE "userdb" ALTER COLUMN "username" TYPE VARCHAR(100) USING "username"::VARCHAR(100);
ALTER TABLE "userdb" ALTER COLUMN "password" TYPE VARCHAR(200) USING "password"::VARCHAR(200);
