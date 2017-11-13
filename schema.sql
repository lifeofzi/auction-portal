-- phpMyAdmin SQL Dump
-- version 4.0.10deb1
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: Nov 13, 2017 at 11:36 AM
-- Server version: 5.5.57-0ubuntu0.14.04.1
-- PHP Version: 5.5.9-1ubuntu4.22

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `AuctionPortal`
--
CREATE DATABASE IF NOT EXISTS `AuctionPortal` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `AuctionPortal`;

DELIMITER $$
--
-- Procedures
--
DROP PROCEDURE IF EXISTS `finish_auction`$$
CREATE DEFINER=`k1997r`@`%` PROCEDURE `finish_auction`()
    NO SQL
begin
declare finished integer default 0;
declare aid integer;
declare bd_amt float;
declare uid integer;
declare cur1 cursor for select auction_id from auctions where end_time < NOW() and status=FALSE;
declare continue handler for not found set finished=1;

open cur1;

get_auctions:LOOP
	SET finished = 0 ;
	FETCH cur1 into aid;
	select finished,aid;
	if finished = 1 then leave get_auctions; end if;
	
	select user_id,bid_amount
	into uid,bd_amt
	from bids 
	where auction_id=aid and bid_amount=(select max(bid_amount) from bids where auction_id=aid);
	
    	select bd_amt,uid;  
		if bd_amt is not null then
	
		update users join bids on bids.user_id=users.id
		set account_balance=account_balance+bids.bid_amount
		where bids.auction_id=aid and users.id != uid;


		insert into purchases(auction_id,price,user_id) values(aid,bd_amt,uid);
		end if;
	
		update auctions set status=TRUE where auction_id=aid;
end loop get_auctions;

close cur1;

END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `auctions`
--

DROP TABLE IF EXISTS `auctions`;
CREATE TABLE IF NOT EXISTS `auctions` (
  `name` varchar(80) DEFAULT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `admin_id` int(11) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `start_price` float NOT NULL DEFAULT '0',
  `increment_price` float NOT NULL DEFAULT '0',
  `picture1` varchar(800) NOT NULL,
  `picture2` varchar(800) NOT NULL,
  `picture3` varchar(800) NOT NULL,
  `category_id` int(8) NOT NULL,
  `auction_id` int(8) NOT NULL AUTO_INCREMENT,
  `status` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`auction_id`),
  KEY `admin_id` (`admin_id`),
  KEY `category_id` (`category_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=47 ;

--
-- Triggers `auctions`
--
DROP TRIGGER IF EXISTS `trig_init_price_check`;
DELIMITER //
CREATE TRIGGER `trig_init_price_check` BEFORE INSERT ON `auctions`
 FOR EACH ROW BEGIN 
    IF NEW.increment_price <0
	THEN 
	SET NEW.increment_price =0;
	END IF ;

	IF NEW.start_price < 0
	THEN 
	SET NEW.start_price =0;
	END IF ;

    END
//
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `bids`
--

DROP TABLE IF EXISTS `bids`;
CREATE TABLE IF NOT EXISTS `bids` (
  `bid_id` int(10) NOT NULL AUTO_INCREMENT,
  `bid_amount` float DEFAULT NULL,
  `bid_time` datetime DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `auction_id` int(8) DEFAULT NULL,
  PRIMARY KEY (`bid_id`),
  KEY `user_id` (`user_id`),
  KEY `auction_id` (`auction_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=68 ;

--
-- Triggers `bids`
--
DROP TRIGGER IF EXISTS `update_balance`;
DELIMITER //
CREATE TRIGGER `update_balance` BEFORE INSERT ON `bids`
 FOR EACH ROW BEGIN
		SET @bal := (SELECT account_balance FROM users WHERE id=NEW.user_id);
		IF @bal < NEW.bid_amount
		THEN signal sqlstate '45000';
		END IF;
		IF @bal >= NEW.bid_amount
		THEN UPDATE users SET account_balance=account_balance-NEW.bid_amount WHERE id=NEW.user_id;
		END IF;
	END
//
DELIMITER ;
DROP TRIGGER IF EXISTS `update_balance_onupdate`;
DELIMITER //
CREATE TRIGGER `update_balance_onupdate` BEFORE UPDATE ON `bids`
 FOR EACH ROW BEGIN
		SET @bal := (SELECT account_balance FROM users WHERE id=NEW.user_id);
		SET @prev_bid := (SELECT bid_amount FROM bids WHERE user_id=NEW.user_id AND auction_id=NEW.auction_id);
		IF @bal < NEW.bid_amount
		THEN signal sqlstate '45000';
		END IF;
		IF @bal >= NEW.bid_amount
		THEN UPDATE users SET account_balance=account_balance-NEW.bid_amount+@prev_bid WHERE id=NEW.user_id;
		END IF;
	END
//
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
CREATE TABLE IF NOT EXISTS `categories` (
  `category_id` int(8) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`category_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=11 ;

-- --------------------------------------------------------

--
-- Table structure for table `purchases`
--

DROP TABLE IF EXISTS `purchases`;
CREATE TABLE IF NOT EXISTS `purchases` (
  `purchase_id` int(80) NOT NULL AUTO_INCREMENT,
  `price` float NOT NULL,
  `user_id` int(11) NOT NULL,
  `auction_id` int(8) NOT NULL,
  PRIMARY KEY (`purchase_id`),
  KEY `user_id` (`user_id`),
  KEY `item_id` (`auction_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=14 ;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  `avatar` int(11) DEFAULT NULL,
  `email` varchar(80) DEFAULT NULL,
  `password` varchar(80) DEFAULT NULL,
  `dateofjoin` date DEFAULT NULL,
  `account_balance` int(11) DEFAULT '1000',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1023 ;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `auctions`
--
ALTER TABLE `auctions`
  ADD CONSTRAINT `auction-user-id` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `auctions_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`);

--
-- Constraints for table `bids`
--
ALTER TABLE `bids`
  ADD CONSTRAINT `bid-user-fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `bids_ibfk_1` FOREIGN KEY (`auction_id`) REFERENCES `auctions` (`auction_id`);

--
-- Constraints for table `purchases`
--
ALTER TABLE `purchases`
  ADD CONSTRAINT `purchases-user-fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `purchases_ibfk_1` FOREIGN KEY (`auction_id`) REFERENCES `auctions` (`auction_id`);

DELIMITER $$
--
-- Events
--
DROP EVENT `finish_auctions`$$
CREATE DEFINER=`k1997r`@`%` EVENT `finish_auctions` ON SCHEDULE EVERY 1 MINUTE STARTS '2017-11-13 05:20:44' ON COMPLETION NOT PRESERVE ENABLE DO call finish_auction()$$

DELIMITER ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
