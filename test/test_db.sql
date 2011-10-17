DROP TABLE IF EXISTS machines;
CREATE TABLE machines (
   id INTEGER PRIMARY KEY,
   os_id INT UNSIGNED NOT NULL,
   is_throttling TINYINT UNSIGNED NOT NULL DEFAULT '0',
   cpu_speed VARCHAR(255),
   name VARCHAR(255) NOT NULL,
   is_active TINYINT UNSIGNED NOT NULL DEFAULT '0',
   date_added INT UNSIGNED NOT NULL
);

--
-- Dumping data for table branches
--

INSERT INTO branches(id, name) VALUES (56,'places');


DROP TABLE IF EXISTS branches;
CREATE TABLE branches (
   id INTEGER PRIMARY KEY,
   name VARCHAR(255) NOT NULL
);

--
-- Dumping data for table machines
--

INSERT INTO machines(id, os_id, is_throttling, cpu_speed, name, is_active, date_added) VALUES (14,1,0,'1.63','talos-rev1-xp03',1,1317783423);

