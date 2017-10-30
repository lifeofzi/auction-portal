-- phpMyAdmin SQL Dump
-- version 4.0.10deb1
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: Oct 30, 2017 at 10:46 AM
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

-- --------------------------------------------------------

--
-- Table structure for table `auctions`
--

CREATE TABLE IF NOT EXISTS `auctions` (
  `auction_id` varchar(80) NOT NULL DEFAULT '',
  `name` varchar(80) DEFAULT NULL,
  `admin_id` int(11) DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `entry_fee` int(11) DEFAULT NULL,
  PRIMARY KEY (`auction_id`),
  KEY `admin_id` (`admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `bids`
--

CREATE TABLE IF NOT EXISTS `bids` (
  `bid_id` varchar(80) NOT NULL DEFAULT '',
  `item_id` varchar(80) DEFAULT NULL,
  `bid_amount` float DEFAULT NULL,
  `bid_time` time DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `auction_id` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`bid_id`),
  KEY `item_id` (`item_id`),
  KEY `user_id` (`user_id`),
  KEY `auction_id` (`auction_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

CREATE TABLE IF NOT EXISTS `categories` (
  `category_id` varchar(80) NOT NULL DEFAULT '',
  `name` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `items`
--

CREATE TABLE IF NOT EXISTS `items` (
  `iterm_id` varchar(80) NOT NULL DEFAULT '',
  `auction_id` varchar(80) DEFAULT NULL,
  `name` varchar(80) DEFAULT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `picture1` varchar(80) DEFAULT NULL,
  `picture2` varchar(80) DEFAULT NULL,
  `picture3` varchar(80) DEFAULT NULL,
  `start_price` int(11) DEFAULT NULL,
  `increment_price` int(11) DEFAULT NULL,
  `category` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`iterm_id`),
  KEY `auction_id` (`auction_id`),
  KEY `category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `purchases`
--

CREATE TABLE IF NOT EXISTS `purchases` (
  `purchase_id` varchar(80) NOT NULL,
  `price` float NOT NULL,
  `user_id` int(11) NOT NULL,
  `item_id` varchar(80) NOT NULL,
  PRIMARY KEY (`purchase_id`),
  KEY `user_id` (`user_id`),
  KEY `item_id` (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL,
  `name` varchar(80) DEFAULT NULL,
  `avatar` int(11) DEFAULT NULL,
  `email` varchar(80) DEFAULT NULL,
  `password` varchar(80) DEFAULT NULL,
  `dateofjoin` date DEFAULT NULL,
  `account_balance` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `avatar`, `email`, `password`, `dateofjoin`, `account_balance`) VALUES
(0, 'Zaman Ishtiyaq', NULL, 'zi10@iitbbs.ac.in', 'password', '2017-10-11', 100);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `auctions`
--
ALTER TABLE `auctions`
  ADD CONSTRAINT `auction-user-id` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `bids`
--
ALTER TABLE `bids`
  ADD CONSTRAINT `bid-auction-fk` FOREIGN KEY (`auction_id`) REFERENCES `auctions` (`auction_id`),
  ADD CONSTRAINT `bid-item-fk` FOREIGN KEY (`item_id`) REFERENCES `items` (`iterm_id`),
  ADD CONSTRAINT `bid-user-fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `items`
--
ALTER TABLE `items`
  ADD CONSTRAINT `category-item-od` FOREIGN KEY (`category`) REFERENCES `categories` (`category_id`),
  ADD CONSTRAINT `auction-item-id` FOREIGN KEY (`auction_id`) REFERENCES `auctions` (`auction_id`);

--
-- Constraints for table `purchases`
--
ALTER TABLE `purchases`
  ADD CONSTRAINT `purchases-item-fk` FOREIGN KEY (`item_id`) REFERENCES `items` (`iterm_id`),
  ADD CONSTRAINT `purchases-user-fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;