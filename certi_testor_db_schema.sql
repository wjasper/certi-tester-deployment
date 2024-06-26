DROP DATABASE IF EXISTS certi_tsi;

CREATE DATABASE certi_tsi;

USE certi_tsi;

DROP TABLE IF EXISTS penetration_test;
DROP TABLE IF EXISTS loading_test;
DROP TABLE IF EXISTS gravimetric_test;
DROP TABLE IF EXISTS test_record;

CREATE TABLE test_record (
    sample_tag VARCHAR(255) PRIMARY KEY NOT NULL,
    test_type VARCHAR(100),
    operator VARCHAR(100),
    comment TEXT
);


CREATE TABLE penetration_test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sample_tag VARCHAR(255),
    flow_rate DOUBLE,
    penetration DOUBLE,
    photometer_reading DOUBLE,
    resistance DOUBLE,
    test_time DATETIME,
    FOREIGN KEY (sample_tag) REFERENCES test_record(sample_tag) ON DELETE CASCADE
);


CREATE TABLE loading_test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sample_tag VARCHAR(255),
    flow_rate DOUBLE,
    penetration DOUBLE,
    photometer_reading DOUBLE,
    resistance DOUBLE,
    mass_challenged_filter DOUBLE,
    test_time DATETIME,
    FOREIGN KEY (sample_tag) REFERENCES test_record(sample_tag) ON DELETE CASCADE
);

CREATE TABLE gravimetric_test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sample_tag VARCHAR(255),
    flow_rate DOUBLE,
    photometer_reading DOUBLE,
    resistance DOUBLE,
    concentration DOUBLE,
    time_elapsed DOUBLE,
    weight_difference DOUBLE,
    test_time DATETIME,
    FOREIGN KEY (sample_tag) REFERENCES test_record(sample_tag) ON DELETE CASCADE
)
