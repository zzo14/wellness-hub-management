DROP SCHEMA IF EXISTS health_wellness_hub;
CREATE SCHEMA health_wellness_hub;
USE health_wellness_hub;

CREATE TABLE IF NOT EXISTS `userrole` (
  `userID` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `role` ENUM('member', 'therapist', 'manager') NOT NULL,
  `date_joined` DATE NOT NULL,
  `title` VARCHAR(50) NOT NULL,
  `first_name` VARCHAR(50) NOT NULL,
  `last_name` VARCHAR(50) NOT NULL,
  `position` VARCHAR(50) NOT NULL,
  `phone` VARCHAR(10) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `address` VARCHAR(255) NULL,
  `date_of_birth` DATE NULL,
  `therapist_profile` LONGTEXT NULL,
  `profile_image` VARCHAR(255) NULL,
  `health_information` LONGTEXT NULL,
  `is_active` TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (`userID`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE);
    
CREATE TABLE IF NOT EXISTS `payment_type` (
  `payment_type_id` INT NOT NULL AUTO_INCREMENT,
  `description` ENUM('subscription', 'therapeutic', 'other') NOT NULL,
  PRIMARY KEY (`payment_type_id`));
  
CREATE TABLE IF NOT EXISTS `fees` (
  `fees_id` INT NOT NULL AUTO_INCREMENT,
  `fees_name` VARCHAR(45) NOT NULL,
  `payment_type_id` INT NULL,
  `price` DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (`fees_id`),
  UNIQUE INDEX `fees_name_UNIQUE` (`fees_name` ASC) VISIBLE,
  CONSTRAINT `fk_fees_type_id`
    FOREIGN KEY (`payment_type_id`)
    REFERENCES `payment_type` (`payment_type_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE);
    
CREATE TABLE IF NOT EXISTS `payment_transaction` (
  `payment_id` INT NOT NULL AUTO_INCREMENT,
  `member_id` INT NOT NULL,
  `fees_id` INT NULL,
  `payment_date` DATE NOT NULL,
  `amount` DECIMAL(10,2) NULL,
  PRIMARY KEY (`payment_id`),
  CONSTRAINT `fk_payment_member_id`
    FOREIGN KEY (`member_id`)
    REFERENCES `userrole` (`userID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_payment_fees_id`
    FOREIGN KEY (`fees_id`)
    REFERENCES `fees` (`fees_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS `membership` (
  `member_id` INT NOT NULL,
  `membership_status` TINYINT NOT NULL DEFAULT 1,
  `expiry_date` DATE NOT NULL,
  `first_joined` DATE NOT NULL,
  `renewed` TINYINT NOT NULL DEFAULT 0,
  `payment_id` INT NULL,
  PRIMARY KEY (`member_id`),
  CONSTRAINT `fk_membership_id`
    FOREIGN KEY (`member_id`)
    REFERENCES `userrole` (`userID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_membership_payment_id` 
    FOREIGN KEY (`payment_id`)
    REFERENCES `payment_transaction` (`payment_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE);
  
CREATE TABLE IF NOT EXISTS `room` (
  `room_id` INT NOT NULL AUTO_INCREMENT,
  `room_name` VARCHAR(100) NOT NULL,
  `capacity` INT NULL,
  PRIMARY KEY (`room_id`),
  UNIQUE INDEX `room_name_UNIQUE` (`room_name` ASC) VISIBLE);

CREATE TABLE IF NOT EXISTS `class_info` (
  `type_id` INT NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(100) NOT NULL,
  `description` TEXT NOT NULL,
  PRIMARY KEY (`type_id`)
);
    
CREATE TABLE IF NOT EXISTS `class` (
  `class_id` INT NOT NULL AUTO_INCREMENT,
  `type_id` INT NOT NULL,
  `repeat_days` SET('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NULL,
  `start_time` TIME NOT NULL,
  `end_time` TIME NOT NULL,
  `duration` INT NOT NULL,
  `room_id` INT NULL,
  `therapist_id` INT NOT NULL,
  PRIMARY KEY (`class_id`),
  CONSTRAINT `fk_class_therapist_id`
    FOREIGN KEY (`therapist_id`)
    REFERENCES `userrole` (`userID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_class_room_id`
    FOREIGN KEY (`room_id`)
    REFERENCES `room` (`room_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
   CONSTRAINT `fk_class_type_id`
    FOREIGN KEY (`type_id`)
    REFERENCES `class_info` (`type_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);
    
CREATE TABLE IF NOT EXISTS `session` (
  `type_id` INT NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(100) NOT NULL,
  `description` TEXT NOT NULL,
  PRIMARY KEY (`type_id`)
);

CREATE TABLE IF NOT EXISTS `therapeutic` (
  `therapeutic_id` INT NOT NULL AUTO_INCREMENT,
  `date` DATE NOT NULL,
  `start_time` TIME NOT NULL,
  `end_time` TIME NOT NULL,
  `duration` INT NOT NULL,
  `type_id` INT NOT NULL,
  `room_id` INT,
  `fees_id` INT NOT NULL,
  `therapist_id` INT NOT NULL,
   `is_available` TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (`therapeutic_id`),
  CONSTRAINT `fk_therapeutic_fees_id`
    FOREIGN KEY (`fees_id`)
    REFERENCES `fees` (`fees_id`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE,
  CONSTRAINT `fk_therapeutic_therapist_id`
    FOREIGN KEY (`therapist_id`)
    REFERENCES `userrole` (`userID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_therapeutic_room_id`
    FOREIGN KEY (`room_id`)
    REFERENCES `room` (`room_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
	CONSTRAINT `fk_therapeutic_type_id`
    FOREIGN KEY (`type_id`)
    REFERENCES `session` (`type_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS `class_booking` (
  `class_booking_id` INT NOT NULL AUTO_INCREMENT,
  `member_id` INT NOT NULL,
  `class_id` INT NOT NULL,
  `date` DATE NOT NULL,
  PRIMARY KEY (`class_booking_id`),
  CONSTRAINT `fk_class_booking_member_id`
    FOREIGN KEY (`member_id`)
    REFERENCES `userrole` (`userID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_class_booking_class_id` 
    FOREIGN KEY (`class_id`)
    REFERENCES `class` (`class_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS `therapeutic_booking` (
  `therapeutic_booking_id` INT NOT NULL AUTO_INCREMENT,
  `member_id` INT NOT NULL,
  `therapeutic_id` INT NOT NULL,
  `payment_id` INT NOT NULL,
  PRIMARY KEY (`therapeutic_booking_id`),
  CONSTRAINT `fk_therapeutic_booking_member_id`
    FOREIGN KEY (`member_id`)
    REFERENCES `userrole` (`userID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_therapeutic_booking_therapeutic_id`
    FOREIGN KEY (`therapeutic_id`)
    REFERENCES `therapeutic` (`therapeutic_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_therapeutic_booking_payment_id`
    FOREIGN KEY (`payment_id`)
    REFERENCES `payment_transaction` (`payment_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS `class_attendance_record` (
  `class_booking_id` INT NOT NULL,
  `member_id` INT NOT NULL,
  `is_attended` TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (`class_booking_id`, `member_id`),
  CONSTRAINT `fk_class_record_booking_id`
    FOREIGN KEY (`class_booking_id`)
    REFERENCES `class_booking` (`class_booking_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_class_record_member_id`
    FOREIGN KEY (`member_id`)
    REFERENCES `userrole` (`userID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE IF NOT EXISTS `therapeutic_attendance_record` (
  `therapeutic_booking_id` INT NOT NULL,
  `member_id` INT NOT NULL,
  `is_attended` TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (`therapeutic_booking_id`, `member_id`),
  CONSTRAINT `fk_therapeutic_record_booking_id`
    FOREIGN KEY (`therapeutic_booking_id`)
    REFERENCES `therapeutic_booking` (`therapeutic_booking_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_therapeutic_record_member_id`
    FOREIGN KEY (`member_id`)
    REFERENCES `userrole` (`userID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);
    
CREATE TABLE IF NOT EXISTS `news` (
  `news_id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(255) NOT NULL,
  `content` LONGTEXT NOT NULL,
  `publish_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `manager_Id` INT NOT NULL,
  PRIMARY KEY (`news_id`),
  CONSTRAINT `fk_news_manager_id`
    FOREIGN KEY (`manager_Id`)
    REFERENCES `userrole` (`userID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

INSERT INTO `userrole` (`username`, `password_hash`, `role`, `date_joined`, `title`, `first_name`, `last_name`, `position`, `phone`, `email`, `is_active`, `address`, `date_of_birth`, `profile_image`, `health_information`, `therapist_profile`) VALUES
	('john_doe', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2021-05-14', 'Mr.', 'John', 'Doe', 'Civil engineer, contracting', '0244358688', 'john_doe@example.org', 1, '8232 Hunt Landing Jonestown, MI 23901', 
    '2002-07-07', 'default_profile.jpg', 'Anxiety, asthma', NULL),
	('charlessamuel', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2023-07-03', 'Mr.', 'Amber', 'Walker', 'Plant breeder/geneticist', '0223317070', 'kristopher77@example.net', 1, 
    '084 Allison Port Suite 000 West Alexanderhaven, ND 58367', '1995-12-11', 'default_profile.jpg', NULL, NULL),
	('alishamorgan', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2023-11-14', 'Dr.', 'Maria', 'Davila', 'Engineer, land', '0254574383', 'lgood@example.org', 1, '1335 Watkins Plains Andreafort, ID 26667', 
    '1995-08-07', 'default_profile.jpg', 'Depression', NULL),
	('victorialogan', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2024-01-29', 'Ind.', 'Mitchell', 'Ramos', 'Therapist, speech and language', '0270108803', 'smithchloe@example.org', 1, 
    '85725 Amy Vista Suite 630 South Samuel, SD 41427', '1976-08-20', 'default_profile.jpg', 'High blood pressure', NULL),
	('selena66', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2023-10-08', 'Ms.', 'Vicki', 'Davis', 'Teaching laboratory technician', '0243582352', 'carterbrooke@example.com', 1, 
    '62357 Amber Islands New Jessica, WV 63905', '1977-03-03', 'default_profile.jpg', 'Diabetes', NULL),
	('grimesnicole', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2024-01-27', 'Mrs.', 'Jennifer', 'Hernandez', 'Physiological scientist', '0289846116', 'evansbenjamin@example.org', 1, 
    '77329 Morris Groves Garciaville, OH 95967', '1980-06-19', 'default_profile.jpg', NULL, NULL),
	('max34', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2021-06-16', 'Dr.', 'Mario', 'Harris', 'Structural engineer', '0261876772', 'hoodjoyce@example.net', 1, 
    '536 Malik Alley Apt. 586 New Anthonyport, AK 26578', '1974-02-08', 'default_profile.jpg', 'High blood pressure', NULL),
	('nblankenship', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2021-10-01', 'Mx.', 'Joshua', 'Guerrero', 'Engineer, chemical', '0292929984', 'wgill@example.net', 1, 
    '428 William Avenue Apt. 338 Suarezmouth, TN 60256', '1966-08-21', 'default_profile.jpg', 'Arthritis', NULL),
	('lindasolis', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2021-07-05', 'Mrs.', 'Anna', 'Moreno', 'Writer', '0258093793', 'yateseric@example.com', 1, 
    '991 Murray Prairie Nelsonburgh, MH 73798', '1958-09-17', 'default_profile.jpg', 'High blood pressure, asthma', NULL),
	('catherinegreen', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2022-01-15', 'Mx.', 'Richard', 'Campos', 'Sports coach', '0213025330', 'masonthomas@example.net', 1, 
    'PSC 1340, Box 0681 APO AA 78966', '1997-05-11', 'default_profile.jpg', 'Dermatitis', NULL),
	('bethellis', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2022-06-22', 'Mr.', 'Melissa', 'Conner', 'Engineer, site', '0242797641', 'linda73@example.org', 1, 
    '1163 Anita Bridge Suite 071 South Paul, CT 27378', '1995-03-13', 'default_profile.jpg', 'Depression', NULL),
	('macdonaldchristopher', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2022-07-20', 'Mrs.', 'Andrea', 'Glenn', 'Farm manager', '0203698824', 'fhart@example.org', 1, 
    '74897 Ivan Islands New Robert, MT 60438', '1967-03-02', 'default_profile.jpg', 'Back pain', NULL),
	('tanyabell', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2022-01-09', 'Mx.', 'Emily', 'Wright', 'Health physicist', '0227114086', 'timothy19@example.org', 1, 
    '2644 James Ports Tommybury, HI 98030', '1977-07-13', 'default_profile.jpg', 'GERD', NULL),
	('turnerstacey', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2023-02-26', 'Mrs.', 'Craig', 'Hensley', 'Nurse, mental health', '0210079486', 'fieldsdavid@example.net', 1, 
    '54350 Jared Lodge Suite 727 Stephanieport, LA 26376', '1993-01-14', 'default_profile.jpg', 'Dermatitis, psoriasis', NULL),
	('sandra26', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2021-05-23', 'Mr.', 'John', 'Brown', 'Engineer, building services', '0202563762', 'mary71@example.com', 1, 
    '1659 Ryan Mountains Port Danielton, PR 81365', '1975-12-09', 'default_profile.jpg', NULL, NULL),
	('qjohnson', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2023-03-12', 'Mr.', 'Susan', 'Waters', 'Careers adviser', '0248965311', 'lisa98@example.net', 1, 
    '010 Hayden Hills Kellyfort, KS 86760', '1968-06-28', 'default_profile.jpg', 'Obesity, anxiety', NULL),
	('carlos30', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2022-11-21', 'Mrs.', 'Carmen', 'Arnold', 'Librarian, academic', '0236788821', 'curtisbarnes@example.com', 1, 
    '3999 Jennifer Fords Suite 106 Barbaramouth, ID 31787', '1986-03-07', 'default_profile.jpg', 'Sleep apnea', NULL),
	('jennifercox', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2022-07-23', 'Mx.', 'Ashley', 'Brennan', 'Manufacturing systems engineer', '0209820274', 'destinyrodriguez@example.com', 1, 
    '79085 Woods Field East Cindy, WY 98679', '2005-12-23', 'default_profile.jpg', NULL, NULL),
	('william37', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2023-01-02', 'Dr.', 'Alyssa', 'Lopez', 'Secretary, company', '0282630108', 'clarkamanda@example.net', 1, 
    '7379 Schneider Keys Apt. 804 Jacobfort, DE 26355', '2004-02-10', 'default_profile.jpg', 'Asthma', NULL),
	('torreslori', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'member', '2023-01-22', 'Mx.', 'Aaron', 'Cohen', 'Training and development officer', '0221590101', 'xward@example.com', 1, 
    '352 Richard Canyon Suite 909 South Dillon, GA 69162', '1993-09-25', 'default_profile.jpg', NULL, NULL),
	('jane_doe', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'therapist', '2022-07-12', 'Dr.', 'Jane', 'Doe', 'Acupuncture Specialist', '0248431818', 'jane_doe@example.com', 1, NULL, NULL, 'Jane_Doe.jpg', NULL, 'With a profound background in traditional Chinese medicine, Jane specializes in acupuncture. She focuses on enhancing patient well-being by restoring energy balance and reducing pain through strategic needle placements.'),
	('connorsnyder', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'therapist', '2022-04-17', 'Dr.', 'Matthew', 'Ramos', 'Massage Therapist', '0221119494', 'matthew_ramos@example.net', 1, NULL, NULL, 'Matthew_Ramos.jpg', NULL, 'Matthew is an expert in both classic and deep tissue massage. He uses his skills to help clients relieve muscle tension and improve circulation, providing relaxation and therapeutic benefits tailored to individual needs.'),
	('qrobles', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'therapist', '2023-04-15', 'Dr.', 'David', 'Robinson', 'Chiropractor', '0288532960', 'david_robinson@example.com', 1, NULL, NULL, 'David_Robinson.jpg', NULL, "Dr. Robinson specializes in chiropractic care, focusing on spinal adjustments to alleviate pain and improve functional abilities. His approach enhances the body's natural healing process and promotes overall health and wellness."),
	('madeline64', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'therapist', '2022-01-25', 'Dr.', 'Anthony', 'Ayala', 'Reflexologist', '0208108661', 'anthony_ayala@example.net', 1, NULL, NULL, 'Anthony_Ayala.jpg', NULL, 'Anthony is a certified reflexologist known for his expertise in applying pressure to specific reflex points on the feet. His treatments are designed to improve nerve functions and blood supply throughout the body, leading to increased energy and better health.'),
	('matthewfranklin', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'therapist', '2022-09-23', 'Dr.', 'David', 'Barrera', 'Dietitian', '0265187422', 'david_barrera@example.com', 1, NULL, NULL, 'David_Barrera.jpg', NULL, "David is a professional dietitian who provides personalized dietary guidance. His sessions focus on educating clients about nutritional choices to support health and well-being, tailored to each individual's unique health requirements."),
	('admin', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'manager', '2021-11-13', 'Mr.', 'Cody', 'Perez', 'Engineer, mining', '0261328500', 'cody_perez@example.com', 1, NULL, NULL, NULL, NULL, NULL),
	('olee', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'manager', '2023-10-31', 'Mrs.', 'Danielle', 'Anderson', 'Forensic scientist', '0202612514', 'danielle_anderson@example.com', 1, NULL, NULL, NULL, NULL, NULL);

INSERT INTO `payment_type` (`description`) VALUES
	('subscription'),
	('therapeutic'),
	('other');

INSERT INTO `fees` (`fees_name`, `payment_type_id`, `price`) VALUES
	('Monthly Membership', 1, 200.00),
	('Annual Membership', 1, 2000.00),
	('Acupuncture', 2, 150.00),
	('Classic Massage', 2, 100.00),
	('Deep Tissue Massage', 2, 120.00),
	('Reflexology', 2, 90.00),
	('Chiropractic Care', 2, 200.00),
	('Dietary Guidance', 2, 80.00),
	('Anxiety Management', 2, 110.00),
	('Wellness Coaching', 2, 130.00),
	('Personalized Exercise Programs', 2, 140.00);

INSERT INTO `payment_transaction` (`member_id`, `fees_id`, `payment_date`, `amount`) VALUES
	(1, 1, '2024-01-15', 200.00),
    (2, 2, '2024-01-16', 2000.00),
    (3, 1, '2024-01-17', 200.00),
    (4, 2, '2024-01-30', 2000.00),
    (5, 1, '2024-02-19', 200.00),
    (6, 1, '2024-02-20', 200.00),
    (7, 2, '2024-03-21', 2000.00),
    (8, 1, '2024-03-22', 200.00),
    (9, 1, '2024-04-23', 200.00),
    (10, 2, '2024-04-24', 2000.00),
    (11, 1, '2024-02-25', 200.00),
    (12, 1, '2024-03-26', 200.00),
    (13, 2, '2024-01-27', 2000.00),
    (14, 1, '2024-02-28', 200.00),
    (15, 2, '2024-03-29', 2000.00),
    (16, 1, '2024-04-30', 200.00),
    (17, 2, '2024-01-31', 2000.00),
    (18, 1, '2024-02-01', 200.00),
    (19, 1, '2024-03-02', 200.00),
    (20, 2, '2024-04-03', 2000.00),
    (1, 3, '2024-01-15', 150.00),   -- Acupuncture for member 1
    (1, 7, '2024-02-16', 200.00),   -- Chiropractic Care for member 1
    (2, 5, '2024-03-17', 120.00),   -- Deep Tissue Massage for member 2
    (2, 6, '2024-04-18', 90.00),    -- Reflexology for member 2
    (3, 7, '2024-01-19', 200.00),   -- Chiropractic Care for member 3
    (4, 8, '2024-02-20', 80.00),    -- Dietary Guidance for member 4
    (4, 10, '2024-03-21', 130.00),  -- Wellness Coaching for member 4
    (5, 9, '2024-04-22', 110.00),   -- Anxiety Management for member 5
    (6, 11, '2024-01-23', 140.00),  -- Personalized Exercise Programs for member 6
    (10, 3, '2024-02-24', 150.00),  -- Acupuncture for member 10
    (10, 4, '2024-03-25', 100.00),  -- Classic Massage for member 10
    (11, 5, '2024-04-26', 120.00),  -- Deep Tissue Massage for member 11
    (12, 7, '2024-01-27', 200.00),  -- Chiropractic Care for member 12
    (13, 9, '2024-02-28', 110.00),  -- Anxiety Management for member 13
    (13, 10, '2024-03-29', 130.00), -- Wellness Coaching for member 13
    (15, 4, '2024-04-30', 100.00),  -- Classic Massage for member 15
    (16, 6, '2024-01-31', 90.00),   -- Reflexology for member 16
    (17, 6, '2024-02-01', 90.00),   -- Reflexology for member 17
    (1, 1, '2023-01-15', 200.00),  -- Monthly Membership for member 1
    (2, 1, '2023-02-15', 200.00),  -- Monthly Membership for member 2
    (3, 1, '2023-03-15', 200.00),  -- Monthly Membership for member 3
    (4, 2, '2023-04-15', 2000.00), -- Annual Membership for member 4
    (5, 1, '2023-05-15', 200.00),  -- Monthly Membership for member 5
    (6, 1, '2023-06-15', 200.00),  -- Monthly Membership for member 6
    (7, 1, '2023-07-15', 200.00),  -- Monthly Membership for member 7
    (8, 2, '2023-08-15', 2000.00), -- Annual Membership for member 8
    (9, 1, '2023-09-15', 200.00),  -- Monthly Membership for member 9
    (10, 1, '2023-10-15', 200.00), -- Monthly Membership for member 10
    (11, 2, '2023-11-15', 2000.00),-- Annual Membership for member 11
    (12, 1, '2023-12-15', 200.00), -- Monthly Membership for member 12
    (1, 3, '2023-01-10', 150.00),  -- Acupuncture for member 1
    (2, 4, '2023-02-20', 100.00),  -- Classic Massage for member 2
    (3, 5, '2023-03-15', 120.00),  -- Deep Tissue Massage for member 3
    (4, 6, '2023-04-22', 90.00),   -- Reflexology for member 4
    (5, 7, '2023-05-10', 200.00),  -- Chiropractic Care for member 5
    (6, 8, '2023-06-30', 80.00),   -- Dietary Guidance for member 6
    (7, 9, '2023-07-14', 110.00),  -- Anxiety Management for member 7
    (8, 10, '2023-08-19', 130.00), -- Wellness Coaching for member 8
    (9, 11, '2023-09-23', 140.00), -- Personalized Exercise Programs for member 9
    (10, 3, '2023-10-05', 150.00), -- Acupuncture for member 10
    (11, 4, '2023-11-17', 100.00), -- Classic Massage for member 11
    (12, 5, '2023-12-21', 120.00); -- Deep Tissue Massage for member 12

INSERT INTO `membership` (`member_id`, `membership_status`, `expiry_date`, `first_joined`, `renewed`, `payment_id`) VALUES
	(1, 1, '2025-12-11', '2021-09-05', 0, 1),
	(2, 1, '2024-11-05', '2021-08-17', 1, 2),
	(3, 1, '2025-10-14', '2023-04-23', 0, 3),
	(4, 1, '2025-03-07', '2023-04-23', 1, 4),
	(5, 1, '2024-09-24', '2022-09-05', 0, 5),
	(6, 1, '2024-08-03', '2022-11-07', 0, 6),
	(7, 0, '2023-07-09', '2021-07-18', 0, 7),
	(8, 0, '2023-10-26', '2023-08-03', 0, 8),
	(9, 0, '2022-11-21', '2022-01-05', 0, 9),
	(10, 1, '2025-09-28', '2023-02-21', 0, 10),
	(11, 1, '2025-03-03', '2022-01-21', 1, 11),
	(12, 1, '2024-08-24', '2023-05-13', 0, 12),
	(13, 1, '2024-10-24', '2021-08-22', 1, 13),
	(14, 0, '2023-12-17', '2023-11-09', 0, 14),
	(15, 1, '2024-10-24', '2022-08-18', 1, 15),
	(16, 1, '2025-07-13', '2024-02-11', 0, 16),
	(17, 1, '2024-11-05', '2023-06-13', 1, 17),
	(18, 1, '2024-06-14', '2023-08-17', 1, 18),
	(19, 1, '2024-10-01', '2022-10-23', 1, 19),
	(20, 1, '2026-01-17', '2022-11-29', 1, 20);

INSERT INTO `room` (`room_name`, `capacity`) VALUES
	('Therapy Room 1', 1),
	('Therapy Room 2', 1),
	('Therapy Room 3', 1),
	('Therapy Room 4', 1),
	('Therapy Room 5', 1),
	('Group Class Room 1', 15),
	('Group Class Room 2', 15),
	('Group Class Room 3', 15),
	('Yoga Studio', 15),
	('Fitness Studio', 15);

INSERT INTO `class_info` (`type`, `description`) VALUES 
	('Yoga Class', 'Find your flow and reconnect with your body and mind through invigorating yoga classes suitable for all levels'),
	('Pilates Class', 'Discover the joy of sculpting a powerful physique while mastering the harmony between mind and body'),
	('Meditation Class', 'Cultivate peace of mind and enhance mental clarity with guided meditation sessions designed to soothe your soul'),
	('Fitness Class', 'Get ready to sweat, groove, and feel amazing in our high-energy fitness classes - Experience the ultimate fusion of fun and effectiveness as you embark on your fitness journey with us'),
	('Mindfulness Class', 'Embrace the present moment and reduce stress with mindfulness practices that promote greater clarity and emotional well-being');

INSERT INTO `class` (`type_id`, `repeat_days`, `start_time`, `end_time`, `duration`, `room_id`, `therapist_id`) VALUES
	(1, 'Monday,Wednesday', '09:00:00', '10:00:00', 60, 9, 21),
	(2, 'Tuesday,Thursday', '11:00:00', '12:00:00', 60, 10, 22),
	(3, 'Wednesday,Friday', '13:00:00', '14:00:00', 60, 6, 23),
	(4, 'Monday,Friday', '15:00:00', '16:00:00', 60, 6, 24);

INSERT INTO `session` (`type`, `description`) VALUES 
	('Acupuncture', 'Experience the ancient art of needle therapy to harmonize the energy flow of your body and promote overall well-being'),
	('Classic Massage', 'Indulge in a blissful session of relaxation as our skilled therapists use gentle strokes to ease tension and rejuvenate your body and mind'),
	('Deep Tissue Massage', 'Dive into deep relaxation with our targeted muscle therapy, designed to release chronic tension and restore mobility for a renewed sense of vitality'),
	('Reflexology', 'Treat your feet to a holistic wellness experience as pressure points are expertly stimulated, promoting relaxation, improved circulation, and enhanced energy flow throughout your body'),
	('Chiropractic Care', 'Discover the benefits of spinal alignment as our chiropractors work to alleviate discomfort, improve mobility, and enhance the natural healing abilities of your body'),
	('Dietary Guidance', 'Take the first step towards optimal health with personalized nutrition advice tailored to your unique needs and goals, helping you make informed choices for a nourished body and mind'),
	('Anxiety Management', 'Equip yourself with effective strategies and support to navigate the challenges of life with greater ease, fostering resilience, and cultivating a sense of calm and well-being'),
	('Wellness Coaching', 'Embark on a transformative journey towards holistic wellness with one-on-one guidance and motivation, empowering you to create sustainable lifestyle changes for long-term vitality and fulfillment'),
	('Personalized Exercise Programs', 'Elevate your fitness journey with a custom-designed exercise plan crafted to your fitness level, preferences, and goals, ensuring every workout is purposeful, enjoyable, and effective');

INSERT INTO `therapeutic` (`date`, `start_time`, `end_time`, `duration`, `type_id`, `room_id`, `fees_id`, `therapist_id`, `is_available`) VALUES
	('2024-06-03', '10:00:00', '10:45:00', 45, 1, 1, 3, 21, 0),
	('2024-06-03', '11:00:00', '11:45:00', 45, 1, 1, 3, 21, 0),
	('2024-06-04', '10:00:00', '10:45:00', 45, 2, 2, 4, 22, 0),
	('2024-06-04', '13:00:00', '13:45:00', 45, 2, 2, 4, 22, 0),
	('2024-06-05', '10:00:00', '10:45:00', 45, 3, 3, 5, 23, 0),
	('2024-06-05', '11:00:00', '11:45:00', 45, 3, 3, 5, 23, 0),
	('2024-06-06', '10:00:00', '10:45:00', 45, 4, 4, 6, 24, 0),
	('2024-06-06', '11:00:00', '11:45:00', 45, 4, 4, 6, 24, 0),
	('2024-06-07', '10:00:00', '10:45:00', 45, 5, 5, 7, 25, 0),
	('2024-06-07', '11:00:00', '11:45:00', 45, 5, 5, 7, 25, 0),
	('2024-06-10', '10:00:00', '10:45:00', 45, 1, 1, 3, 21, 0),
	('2024-06-10', '11:00:00', '11:45:00', 45, 1, 1, 3, 21, 0),
	('2024-06-11', '10:00:00', '10:45:00', 45, 2, 2, 4, 22, 0),
	('2024-06-11', '13:00:00', '13:45:00', 45, 2, 2, 4, 22, 0),
	('2024-06-12', '10:00:00', '10:45:00', 45, 3, 3, 5, 23, 0),
	('2024-06-12', '11:00:00', '11:45:00', 45, 3, 3, 5, 23, 0),
	('2024-06-13', '10:00:00', '10:45:00', 45, 4, 4, 6, 24, 0),
	('2024-06-13', '11:00:00', '11:45:00', 45, 4, 4, 6, 24, 0),
	('2024-06-14', '10:00:00', '10:45:00', 45, 5, 5, 7, 25, 0),
	('2024-06-14', '11:00:00', '11:45:00', 45, 5, 5, 7, 25, 0),
	('2024-06-03', '13:00:00', '13:45:00', 45, 1, 1, 3, 21, 1),
	('2024-06-03', '14:00:00', '14:45:00', 45, 1, 1, 3, 21, 1),
	('2024-06-04', '14:00:00', '14:45:00', 45, 2, 2, 4, 22, 1),
	('2024-06-04', '15:00:00', '15:45:00', 45, 2, 2, 4, 22, 1);
    
INSERT INTO `class_booking` (`member_id`, `class_id`, `date`) VALUES
    (1, 1, '2024-06-03'),  -- Monday
    (2, 1, '2024-06-03'),  -- Monday
    (3, 1, '2024-06-03'),  -- Monday
    (4, 1, '2024-06-03'),  -- Wednesday
    (5, 1, '2024-06-03'),  -- Wednesday
    (6, 1, '2024-06-03'),  -- Wednesday
    (7, 1, '2024-06-03'),  -- Monday
    (8, 1, '2024-06-03'),  -- Monday
    (9, 1, '2024-06-03'),  -- Monday
    (2, 2, '2024-06-04'),  -- Tuesday
    (10, 2, '2024-06-04'), -- Tuesday
    (11, 2, '2024-06-04'), -- Tuesday
    (12, 2, '2024-06-06'), -- Thursday
    (13, 2, '2024-06-06'), -- Thursday
    (14, 2, '2024-06-06'), -- Thursday
    (15, 1, '2024-06-12'), -- Wednesday
    (16, 1, '2024-06-12'), -- Wednesday
    (17, 1, '2024-06-12'), -- Wednesday
    (18, 2, '2024-06-11'), -- Tuesday
    (19, 2, '2024-06-11'), -- Tuesday
    (20, 2, '2024-06-11'), -- Tuesday
    (1, 2, '2024-06-13'),  -- Thursday
    (3, 2, '2024-06-13'),  -- Thursday
    (5, 2, '2024-06-13'),  -- Thursday
    (6, 4, '2024-06-14'),  -- Friday
    (7, 4, '2024-06-14'),  -- Friday
    (8, 4, '2024-06-14'),  -- Friday
    (9, 1, '2024-06-17'),  -- Monday
    (10, 1, '2024-06-17'), -- Monday
    (11, 1, '2024-06-17'), -- Monday
    (12, 3, '2024-06-19'), -- Wednesday
    (13, 3, '2024-06-19'), -- Wednesday
    (14, 3, '2024-06-19'), -- Wednesday
    (15, 4, '2024-06-21'), -- Friday
    (16, 4, '2024-06-21'), -- Friday
    (17, 4, '2024-06-21'), -- Friday
    (18, 1, '2024-06-24'), -- Monday
    (19, 1, '2024-06-24'), -- Monday
    (20, 1, '2024-06-24'); -- Monday

INSERT INTO `class_attendance_record` (`class_booking_id`, `member_id`, `is_attended`) VALUES
    (1, 1, 1),
    (2, 2, 1),
    (3, 3, 1),
    (4, 4, 1),
    (5, 5, 1),
    (6, 6, 1),
    (7, 7, 1),
    (8, 8, 1),
    (9, 9, 1),
    (10, 2, 1),
    (11, 10, 1),
    (12, 11, 1),
    (13, 12, 1),
    (14, 13, 1),
    (15, 14, 1),
    (16, 15, 1),
    (17, 16, 1),
    (18, 17, 1),
    (19, 18, 1),
    (20, 19, 1),
    (21, 20, 1),
    (22, 1, 1),
    (23, 3, 1),
    (24, 5, 1),
    (25, 6, 1),
    (26, 7, 1),
    (27, 8, 1),
    (28, 9, 1),
    (29, 10, 1),
    (30, 11, 1),
    (31, 12, 1),
    (32, 13, 1),
    (33, 14, 1),
    (34, 15, 1),
    (35, 16, 1),
    (36, 17, 1),
    (37, 18, 1),
    (38, 19, 1),
    (39, 20, 1);
    
INSERT INTO `therapeutic_booking` (`member_id`, `therapeutic_id`, `payment_id`) VALUES
	(1, 1, 21), (1, 5, 22), (2, 3, 23), (2, 6, 24), (3, 2, 25),
	(4, 7, 26), (4, 10, 27), (5, 9, 28), (6, 11, 29), (10, 13, 30),
	(10, 14, 31), (11, 15, 32), (12, 17, 33), (13, 19, 34), (13, 20, 35),
	(15, 12, 36), (16, 4, 37), (17, 16, 38), (18, 8, 39), (19, 18, 40);

INSERT INTO `therapeutic_attendance_record` (`therapeutic_booking_id`, `member_id`, `is_attended`) VALUES
	(1, 1, 1), (2, 1, 1), (3, 2, 1), (4, 2, 1), (5, 3, 1),
	(6, 4, 1), (7, 4, 1), (8, 5, 1), (9, 6, 1), (10, 10, 1),
	(11, 10, 1), (12, 11, 1), (13, 12, 1), (14, 13, 1), (15, 13, 1),
	(16, 15, 1), (17, 16, 1), (18, 17, 1), (19, 18, 1), (20, 19, 1);

INSERT INTO `news` (`title`, `content`, `publish_time`, `manager_Id`) VALUES
	('Welcome to the Health and Wellness Hub', 'We are excited to announce the opening of our new Health and Wellness Hub!', '2023-01-01 08:00:00', 26),
	('New Yoga Classes', 'Join our new yoga classes starting this month.', '2023-03-01 09:00:00', 27);