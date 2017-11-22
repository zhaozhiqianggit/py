-- MySQL dump 10.13  Distrib 5.6.19, for osx10.9 (x86_64)
--
-- Host: 172.16.1.81    Database: frontera
-- ------------------------------------------------------
-- Server version	5.6.37

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `frontera`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `frontera` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `frontera`;

--
-- Table structure for table `metadata`
--

DROP TABLE IF EXISTS `metadata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `metadata` (
  `fingerprint` varchar(40) NOT NULL,
  `url` varchar(1024) NOT NULL,
  `depth` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `fetched_at` datetime DEFAULT NULL,
  `status_code` varchar(20) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `error` varchar(128) DEFAULT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  PRIMARY KEY (`fingerprint`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `queue`
--

DROP TABLE IF EXISTS `queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `partition_id` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `url` varchar(1024) NOT NULL,
  `fingerprint` varchar(40) NOT NULL,
  `host_crc32` int(11) NOT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  `created_at` bigint(20) DEFAULT NULL,
  `depth` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_queue_score` (`score`),
  KEY `ix_queue_created_at` (`created_at`),
  KEY `ix_queue_partition_id` (`partition_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `revisiting_queue`
--

DROP TABLE IF EXISTS `revisiting_queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `revisiting_queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `partition_id` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `url` varchar(1024) NOT NULL,
  `fingerprint` varchar(40) NOT NULL,
  `host_crc32` int(11) NOT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  `created_at` bigint(20) DEFAULT NULL,
  `depth` smallint(6) DEFAULT NULL,
  `crawl_at` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_revisiting_queue_partition_id` (`partition_id`),
  KEY `ix_revisiting_queue_score` (`score`),
  KEY `ix_revisiting_queue_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=217679 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `seeds`
--

DROP TABLE IF EXISTS `seeds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seeds` (
  `url` varchar(250) NOT NULL DEFAULT '',
  `ref_no` int(11) NOT NULL,
  `status` smallint(6) NOT NULL,
  `ts` bigint(20) NOT NULL,
  PRIMARY KEY (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `states`
--

DROP TABLE IF EXISTS `states`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `states` (
  `fingerprint` varchar(40) NOT NULL,
  `state` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`fingerprint`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Current Database: `frontera_keyword`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `frontera_keyword` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `frontera_keyword`;

--
-- Table structure for table `metadata`
--

DROP TABLE IF EXISTS `metadata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `metadata` (
  `fingerprint` varchar(40) NOT NULL,
  `url` varchar(1024) NOT NULL,
  `depth` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `fetched_at` datetime DEFAULT NULL,
  `status_code` varchar(20) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `error` varchar(128) DEFAULT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  PRIMARY KEY (`fingerprint`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `queue`
--

DROP TABLE IF EXISTS `queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `partition_id` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `url` varchar(1024) NOT NULL,
  `fingerprint` varchar(40) NOT NULL,
  `host_crc32` int(11) NOT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  `created_at` bigint(20) DEFAULT NULL,
  `depth` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_queue_score` (`score`),
  KEY `ix_queue_partition_id` (`partition_id`),
  KEY `ix_queue_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `revisiting_queue`
--

DROP TABLE IF EXISTS `revisiting_queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `revisiting_queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `partition_id` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `url` varchar(1024) NOT NULL,
  `fingerprint` varchar(40) NOT NULL,
  `host_crc32` int(11) NOT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  `created_at` bigint(20) DEFAULT NULL,
  `depth` smallint(6) DEFAULT NULL,
  `crawl_at` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_revisiting_queue_created_at` (`created_at`),
  KEY `ix_revisiting_queue_partition_id` (`partition_id`),
  KEY `ix_revisiting_queue_score` (`score`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `seeds_keyword`
--

DROP TABLE IF EXISTS `seeds_keyword`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seeds_keyword` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(250) NOT NULL DEFAULT '',
  `ref_no` int(11) NOT NULL,
  `status` smallint(6) NOT NULL,
  `asin` varchar(20) NOT NULL DEFAULT '',
  `uuid` varchar(50) NOT NULL DEFAULT '',
  `keyword` varchar(1024) NOT NULL DEFAULT '',
  `ts` bigint(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `states`
--

DROP TABLE IF EXISTS `states`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `states` (
  `fingerprint` varchar(40) NOT NULL,
  `state` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`fingerprint`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Current Database: `frontera_simulatecart`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `frontera_simulatecart` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `frontera_simulatecart`;

--
-- Table structure for table `metadata`
--

DROP TABLE IF EXISTS `metadata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `metadata` (
  `fingerprint` varchar(40) NOT NULL,
  `url` varchar(1024) NOT NULL,
  `depth` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `fetched_at` datetime DEFAULT NULL,
  `status_code` varchar(20) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `error` varchar(128) DEFAULT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  PRIMARY KEY (`fingerprint`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `queue`
--

DROP TABLE IF EXISTS `queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `partition_id` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `url` varchar(1024) NOT NULL,
  `fingerprint` varchar(40) NOT NULL,
  `host_crc32` int(11) NOT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  `created_at` bigint(20) DEFAULT NULL,
  `depth` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_queue_created_at` (`created_at`),
  KEY `ix_queue_score` (`score`),
  KEY `ix_queue_partition_id` (`partition_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `revisiting_queue`
--

DROP TABLE IF EXISTS `revisiting_queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `revisiting_queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `partition_id` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `url` varchar(1024) NOT NULL,
  `fingerprint` varchar(40) NOT NULL,
  `host_crc32` int(11) NOT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  `created_at` bigint(20) DEFAULT NULL,
  `depth` smallint(6) DEFAULT NULL,
  `crawl_at` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_revisiting_queue_partition_id` (`partition_id`),
  KEY `ix_revisiting_queue_score` (`score`),
  KEY `ix_revisiting_queue_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=502 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `seeds_simulatecart`
--

DROP TABLE IF EXISTS `seeds_simulatecart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seeds_simulatecart` (
  `url` varchar(250) NOT NULL DEFAULT '',
  `ref_no` int(11) NOT NULL,
  `status` smallint(6) NOT NULL,
  `asin` varchar(20) NOT NULL DEFAULT '',
  `ts` bigint(20) NOT NULL,
  PRIMARY KEY (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `states`
--

DROP TABLE IF EXISTS `states`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `states` (
  `fingerprint` varchar(40) NOT NULL,
  `state` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`fingerprint`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Current Database: `frontera_competing`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `frontera_competing` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `frontera_competing`;

--
-- Table structure for table `metadata`
--

DROP TABLE IF EXISTS `metadata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `metadata` (
  `fingerprint` varchar(40) NOT NULL,
  `url` varchar(1024) NOT NULL,
  `depth` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `fetched_at` datetime DEFAULT NULL,
  `status_code` varchar(20) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `error` varchar(128) DEFAULT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  PRIMARY KEY (`fingerprint`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `queue`
--

DROP TABLE IF EXISTS `queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `partition_id` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `url` varchar(1024) NOT NULL,
  `fingerprint` varchar(40) NOT NULL,
  `host_crc32` int(11) NOT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  `created_at` bigint(20) DEFAULT NULL,
  `depth` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_queue_score` (`score`),
  KEY `ix_queue_partition_id` (`partition_id`),
  KEY `ix_queue_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `revisiting_queue`
--

DROP TABLE IF EXISTS `revisiting_queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `revisiting_queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `partition_id` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `url` varchar(1024) NOT NULL,
  `fingerprint` varchar(40) NOT NULL,
  `host_crc32` int(11) NOT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  `created_at` bigint(20) DEFAULT NULL,
  `depth` smallint(6) DEFAULT NULL,
  `crawl_at` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_revisiting_queue_created_at` (`created_at`),
  KEY `ix_revisiting_queue_partition_id` (`partition_id`),
  KEY `ix_revisiting_queue_score` (`score`)
) ENGINE=InnoDB AUTO_INCREMENT=2693 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `seeds_competing`
--

DROP TABLE IF EXISTS `seeds_competing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seeds_competing` (
  `url` varchar(250) NOT NULL DEFAULT '',
  `ref_no` int(11) NOT NULL,
  `status` smallint(6) NOT NULL,
  `asin` varchar(20) NOT NULL DEFAULT '',
  `ts` bigint(20) NOT NULL,
  PRIMARY KEY (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `states`
--

DROP TABLE IF EXISTS `states`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `states` (
  `fingerprint` varchar(40) NOT NULL,
  `state` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`fingerprint`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Current Database: `frontera_simulatecart_bsr`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `frontera_simulatecart_bsr` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `frontera_simulatecart_bsr`;

--
-- Table structure for table `metadata`
--

DROP TABLE IF EXISTS `metadata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `metadata` (
  `fingerprint` varchar(40) NOT NULL,
  `url` varchar(1024) NOT NULL,
  `depth` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `fetched_at` datetime DEFAULT NULL,
  `status_code` varchar(20) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `error` varchar(128) DEFAULT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  PRIMARY KEY (`fingerprint`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `queue`
--

DROP TABLE IF EXISTS `queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `partition_id` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `url` varchar(1024) NOT NULL,
  `fingerprint` varchar(40) NOT NULL,
  `host_crc32` int(11) NOT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  `created_at` bigint(20) DEFAULT NULL,
  `depth` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_queue_created_at` (`created_at`),
  KEY `ix_queue_score` (`score`),
  KEY `ix_queue_partition_id` (`partition_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `revisiting_queue`
--

DROP TABLE IF EXISTS `revisiting_queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `revisiting_queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `partition_id` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `url` varchar(1024) NOT NULL,
  `fingerprint` varchar(40) NOT NULL,
  `host_crc32` int(11) NOT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  `created_at` bigint(20) DEFAULT NULL,
  `depth` smallint(6) DEFAULT NULL,
  `crawl_at` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_revisiting_queue_partition_id` (`partition_id`),
  KEY `ix_revisiting_queue_score` (`score`),
  KEY `ix_revisiting_queue_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=598075 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `seeds_bsr_simulatecart`
--

DROP TABLE IF EXISTS `seeds_bsr_simulatecart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seeds_bsr_simulatecart` (
  `url` varchar(250) NOT NULL DEFAULT '',
  `ref_no` int(11) NOT NULL,
  `status` smallint(6) NOT NULL,
  `asin` varchar(20) NOT NULL DEFAULT '',
  `ts` bigint(20) NOT NULL,
  PRIMARY KEY (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `states`
--

DROP TABLE IF EXISTS `states`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `states` (
  `fingerprint` varchar(40) NOT NULL,
  `state` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`fingerprint`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Current Database: `frontera_category`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `frontera_category` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `frontera_category`;

--
-- Table structure for table `metadata`
--

DROP TABLE IF EXISTS `metadata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `metadata` (
  `fingerprint` varchar(40) NOT NULL,
  `url` varchar(1024) NOT NULL,
  `depth` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `fetched_at` datetime DEFAULT NULL,
  `status_code` varchar(20) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `error` varchar(128) DEFAULT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  PRIMARY KEY (`fingerprint`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `queue`
--

DROP TABLE IF EXISTS `queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `partition_id` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `url` varchar(1024) NOT NULL,
  `fingerprint` varchar(40) NOT NULL,
  `host_crc32` int(11) NOT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  `created_at` bigint(20) DEFAULT NULL,
  `depth` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_queue_created_at` (`created_at`),
  KEY `ix_queue_score` (`score`),
  KEY `ix_queue_partition_id` (`partition_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `revisiting_queue`
--

DROP TABLE IF EXISTS `revisiting_queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `revisiting_queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `partition_id` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `url` varchar(1024) NOT NULL,
  `fingerprint` varchar(40) NOT NULL,
  `host_crc32` int(11) NOT NULL,
  `meta` blob,
  `headers` blob,
  `cookies` blob,
  `method` varchar(6) DEFAULT NULL,
  `created_at` bigint(20) DEFAULT NULL,
  `depth` smallint(6) DEFAULT NULL,
  `crawl_at` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_revisiting_queue_partition_id` (`partition_id`),
  KEY `ix_revisiting_queue_score` (`score`),
  KEY `ix_revisiting_queue_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=8912 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `seeds`
--

DROP TABLE IF EXISTS `seeds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seeds` (
  `url` varchar(250) NOT NULL DEFAULT '',
  `ref_no` int(11) NOT NULL,
  `status` smallint(6) NOT NULL,
  `ts` bigint(20) NOT NULL,
  PRIMARY KEY (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `states`
--

DROP TABLE IF EXISTS `states`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `states` (
  `fingerprint` varchar(40) NOT NULL,
  `state` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`fingerprint`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-10-23 11:29:38
