CREATE DATABASE when2meet;
CREATE USER admin WITH PASSWORD 'orbital2425';
ALTER USER admin CREATEDB;
ALTER ROLE admin SET client_encoding TO 'utf8';
ALTER ROLE admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE admin SET timezone TO 'ASIA/SINGAPORE';
GRANT ALL PRIVILEGES ON DATABASE when2meet TO admin;\
ALTER DATABASE when2meet OWNER TO admin;
-- type \l to check if the database is setup correctly
