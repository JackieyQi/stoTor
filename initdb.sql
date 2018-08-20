create database `sto_adb` default character set utf8 collate utf8_general_ci;

grant all privileges on sto_adb.* to ster@localhost identified by '111111';

flush privileges;

CREATE TABLE IF NOT EXISTS `sto_adb`.`user` (
	  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
	  `mail` varchar(30) NOT NULL DEFAULT '',
	  `phone` varchar(30) NOT NULL DEFAULT '',
	  `status` tinyint(1) NOT NULL DEFAULT 0,
	  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	  PRIMARY KEY (`id`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `sto_adb`.`user_sto` (
	  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
	  `code` char(6) NOT NULL DEFAULT '' COMMENT '000001',
	  `price_in` smallint(5) unsigned NOT NULL DEFAULT 0 COMMENT '100.01to10001',
	  `price_out` smallint(5) unsigned NOT NULL DEFAULT 0,
	  `price_top` smallint(5) unsigned NOT NULL DEFAULT 0,
	  `price_bot` smallint(5) unsigned NOT NULL DEFAULT 0,
	  `time_in` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	  `time_out` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	  PRIMARY KEY (`id`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `sto_adb`.`user_profit` (
	  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
	  `start_ass` mediumint(7) NOT NULL DEFAULT 0,
	  `end_ass` mediumint(7) NOT NULL DEFAULT 0,
	  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	  `rate` mediumint(7) NOT NULL DEFAULT 0 COMMENT '100.01%to1.0001',
	  PRIMARY KEY (`id`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `sto_adb`.`sto_market_cap` (
	  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
	  `code` char(6) NOT NULL DEFAULT '' COMMENT '000001',
	  `cap1` int(10) NOT NULL DEFAULT 0,
	  `cap5` int(10) NOT NULL DEFAULT 0,
	  `cap10` int(10) NOT NULL DEFAULT 0,
	  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	  PRIMARY KEY (`id`),
	  KEY `code` (`code`, `create_time`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `sto_adb`.`sto_src_turnover` (
	  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
	  `code` char(6) NOT NULL DEFAULT '' COMMENT '000001',
	  `turnover` varchar(11) NOT NULL DEFAULT '',
	  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	  PRIMARY KEY (`id`),
	  KEY `code` (`code`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `sto_adb`.`sto_code` (
	  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
	  `code` char(6) NOT NULL DEFAULT '' COMMENT '000001',
	  `name` varchar(32) NOT NULL DEFAULT '',
	  `symbol` char(2) NOT NULL DEFAULT '',
	  `type` tinyint(1) NOT NULL DEFAULT 0,
	  PRIMARY KEY (`id`),
	  UNIQUE KEY `code` (`code`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;


