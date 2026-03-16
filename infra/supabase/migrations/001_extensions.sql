-- GeoAdmin Pro - Migration 001
-- Extensoes base

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

SELECT postgis_version();
