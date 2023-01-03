-- upgrade --
CREATE INDEX "idx_generalholi_non_occ_ec9419" ON "generalholiday" ("non_occasion");
-- downgrade --
DROP INDEX "idx_generalholi_non_occ_ec9419";
