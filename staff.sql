CREATE TABLE staff (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
name TEXT NOT NULL,
contract TEXT NOT NULL,
nonworking_days TEXT,
cando1 TEXT NOT NULL,
cando2 TEXT NOT NULL);

INSERT INTO staff (name, contract, cando1, cando2) VALUES ("Zoe","F","y","y");
INSERT INTO staff (name, contract, cando1, cando2) VALUES ("Tilly","F","y","y");
INSERT INTO staff (name, contract,  cando1, cando2) VALUES ("Hannah","P","pm2 3 4","y","y");
INSERT INTO staff (name, contract, cando1, cando2) VALUES ("Irfan","F","y","y");
INSERT INTO staff (name, contract, cando1, cando2) VALUES ("Oli","F","y","y");
INSERT INTO staff (name, contract, cando1, cando2) VALUES ("Beth","F","y","n");

CREATE TABLE unavailable (id INTEGER NOT NULL,
staff_id INTEGER NOT NULL,
date DATE NOT NULL,
PRIMARY KEY (id),
FOREIGN KEY (staff_id) REFERENCES staff(id));

DELETE FROM schedule;

INSERT INTO unavailable (staff_id, date) VALUES (1, '2023-05-05');
INSERT INTO unavailable (staff_id, date) VALUES (1, '2023-05-08');
INSERT INTO unavailable (staff_id, date) VALUES (1, '2023-05-09');
INSERT INTO unavailable (staff_id, date) VALUES (1, '2023-05-10');

CREATE TABLE public_holidays (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
date DATE NOT NULL,
name TEXT NOT NULL);

INSERT INTO public_holidays (date, name) VALUES ("2023-05-01", "Early May Bank Holiday");
INSERT INTO public_holidays (date, name) VALUES ("2023-05-08", "Coronation King Charles III");
INSERT INTO public_holidays (date, name) VALUES ("2023-05-29", "Spring Bank Holiday");
INSERT INTO public_holidays (date, name) VALUES ("2023-08-28", "Summer Bank Holiday");
INSERT INTO public_holidays (date, name) VALUES ("2023-12-25", "Christmas Day");
INSERT INTO public_holidays (date, name) VALUES ("2023-12-26", "Boxing Day");
INSERT INTO public_holidays (date, name) VALUES ("2024-01-01", "New Year's Day");

CREATE TABLE schedule (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, date DATE NOT NULL, AM_1 TEXT, AM_2 TEXT, PM_1 TEXT, PM_2 TEXT);