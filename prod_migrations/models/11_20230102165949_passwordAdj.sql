-- upgrade --
ALTER TABLE "userdb" ALTER COLUMN "password" TYPE VARCHAR(100) USING "password"::VARCHAR(100);
-- downgrade --
ALTER TABLE "userdb" ALTER COLUMN "password" TYPE VARCHAR(16) USING "password"::VARCHAR(16);
