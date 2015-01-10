-----------------------------------
-- User Table
----------------------------------
	-- FOREIGN KEY(followers) REFERENCES Followers(id_user) ON UPDATE CASCADE
	-- FOREIGN KEY(following) REFERENCES Following(id_user) ON UPDATE CASCADE,
	-- FOREIGN KEY(subscriptions) REFERENCES Subscriptions(id_user) ON UPDATE CASCADE
DROP TABLE IF EXISTS User;

CREATE TABLE IF NOT EXISTS User (
	id INT NOT NULL AUTO_INCREMENT,
	username VARCHAR(50),
	email VARCHAR(50) NOT NULL,
	name VARCHAR(200),
	about TEXT,
	isAnonymous TINYINT(1) NOT NULL DEFAULT '0',
	PRIMARY KEY(email),
	UNIQUE KEY(id)
	)
	ENGINE = InnoDB
	DEFAULT CHARACTER SET='utf8';

-----------------------------------
-- Forum Table
-----------------------------------
DROP TABLE IF EXISTS Forum;

CREATE TABLE IF NOT EXISTS Forum (
	id INT NOT NULL AUTO_INCREMENT,
	name VARCHAR(255) NOT NULL,
	short_name VARCHAR(150) NOT NULL,
	user VARCHAR(50) NOT NULL,
	PRIMARY KEY(short_name),
	UNIQUE KEY(id, name),
	FOREIGN KEY(user) REFERENCES User(email) ON UPDATE CASCADE ON DELETE CASCADE
	)
	ENGINE=InnoDB
	DEFAULT CHARACTER SET = 'utf8';


-----------------------------------
-- Thread Table (Тема)
-- slug - коротокое название темы
-----------------------------------
DROP TABLE IF EXISTS Thread;

CREATE TABLE IF NOT EXISTS Thread (
	id INT NOT NULL AUTO_INCREMENT,
	title VARCHAR(255) NOT NULL,
	slug VARCHAR(150) NOT NULL,
	message TEXT NOT NULL,
	likes INT NOT NULL DEFAULT '0',
	dislikes INT NOT NULL DEFAULT '0',
	isClosed TINYINT(1) NOT NULL DEFAULT '0',
	isDeleted TINYINT(1) NOT NULL DEFAULT '0',
	date DATETIME NOT NULL,
	forum VARCHAR(150) NOT NULL,
	user VARCHAR(50) NOT NULL,
	posts INT NOT NULL DEFAULT '0',
	PRIMARY KEY(id),
	UNIQUE KEY(title, slug),
	FOREIGN KEY(forum) REFERENCES Forum(short_name) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY(user) REFERENCES User(email) ON UPDATE CASCADE ON DELETE CASCADE
	)
	ENGINE=InnoDB
	DEFAULT CHARACTER SET = 'utf8';


-----------------------------------
-- Post Table (комментарий) НЕ ДОЛЖНЫ РАБИТЬ
-----------------------------------
DROP TABLE IF EXISTS Post;

CREATE TABLE IF NOT EXISTS Post (
	id INT NOT NULL AUTO_INCREMENT,
	message TEXT NOT NULL,
	likes INT NOT NULL DEFAULT '0',
	dislikes INT NOT NULL DEFAULT '0',
	isApproved TINYINT(1) NOT NULL DEFAULT '0' COMMENT 'Утвержденный',
	isDeleted TINYINT(1) NOT NULL DEFAULT '0',
	isEdited TINYINT(1) NOT NULL DEFAULT '0',
	isHighlighted TINYINT(1) NOT NULL DEFAULT '0' COMMENT 'Подсвеченный',
	isSpam TINYINT(1) NOT NULL DEFAULT '0',
	date DATETIME NOT NULL,
	parent INT DEFAULT NULL,
	forum VARCHAR(150) NOT NULL,
	thread INT NOT NULL,
	user VARCHAR(50) NOT NULL,
	PRIMARY KEY(id),
	FOREIGN KEY(forum) REFERENCES Forum(short_name) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY(thread) REFERENCES Thread(id) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY(user) REFERENCES User(email) ON UPDATE CASCADE ON DELETE CASCADE
	)
	ENGINE=InnoDB
	DEFAULT CHARACTER SET = 'utf8';


-----------------------------------
-- Followers (подписчики), 
-- Following (те, на кого подписан),
-- Subscriptions (подписки на thread-ы)
-- Tables
----------------------------------
DROP TABLE IF EXISTS Followers;

CREATE TABLE IF NOT EXISTS Followers (
	follower VARCHAR(50) NOT NULL,
	followee VARCHAR(50) NOT NULL,
	CONSTRAINT FOREIGN KEY(follower) REFERENCES User(email) ON UPDATE CASCADE,
	CONSTRAINT FOREIGN KEY(followee) REFERENCES User(email) ON UPDATE CASCADE
	)
	ENGINE=InnoDB
	DEFAULT CHARACTER SET = 'utf8';


DROP TABLE IF EXISTS Subscriptions;

CREATE TABLE IF NOT EXISTS Subscriptions (
	user VARCHAR(50) NOT NULL,
	thread INT NOT NULL COMMENT 'id thread-а, на который подписан user',
	CONSTRAINT FOREIGN KEY(user) REFERENCES User(email),
	CONSTRAINT FOREIGN KEY(thread) REFERENCES Thread(id)
	)
	ENGINE=InnoDB
	DEFAULT CHARACTER SET='utf8';


-- DROP ALL TABLES
DROP TABLE IF EXISTS Followers;
DROP TABLE IF EXISTS Subscriptions;
DROP TABLE IF EXISTS Post;
DROP TABLE IF EXISTS Thread;
DROP TABLE IF EXISTS Forum;
DROP TABLE IF EXISTS User;


TRUNCATE TABLE Followers;
TRUNCATE TABLE Subscriptions;
TRUNCATE TABLE Post;
TRUNCATE TABLE Thread;
TRUNCATE TABLE Forum;
TRUNCATE TABLE User; 
