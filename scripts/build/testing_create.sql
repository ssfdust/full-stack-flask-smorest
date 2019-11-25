CREATE ROLE "smorest-admin" WITH LOGIN ENCRYPTED PASSWORD 'mySmorest2019';
CREATE DATABASE "smorest-testing-db";
GRANT ALL PRIVILEGES ON DATABASE "smorest-testing-db" to "smorest-admin";
