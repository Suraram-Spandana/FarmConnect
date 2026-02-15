-- MySQL dump 10.13  Distrib 5.5.60, for Win64 (AMD64)
--
-- Host: localhost    Database: farmconnect
-- ------------------------------------------------------
-- Server version	5.5.60

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
-- Table structure for table `cart`
--

DROP TABLE IF EXISTS `cart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cart` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `consumer_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `consumer_id` (`consumer_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`consumer_id`) REFERENCES `users` (`id`),
  CONSTRAINT `cart_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart`
--

LOCK TABLES `cart` WRITE;
/*!40000 ALTER TABLE `cart` DISABLE KEYS */;
/*!40000 ALTER TABLE `cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `orders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL,
  `consumer_id` int(11) NOT NULL,
  `farmer_id` int(11) DEFAULT NULL,
  `quantity` int(11) NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `order_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `status` varchar(20) DEFAULT 'Pending',
  `address` text,
  `payment_status` varchar(20) DEFAULT 'Unpaid',
  `phone` varchar(20) DEFAULT NULL,
  `farmer_seen` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`),
  KEY `consumer_id` (`consumer_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`consumer_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,6,5,1,1,60.00,'2025-10-26 18:08:01','Cancelled','sri, 45, abc, hyd, hyd, ts, PIN: 508001','Paid','1234567890',1),(2,3,5,3,1,50.00,'2025-10-26 17:07:19','Cancelled','sri, 45, abc, hyd, hyd, ts, PIN: 508001','Paid','1234567890',0),(4,3,5,3,1,50.00,'2025-10-26 18:10:19','Cancelled','Address Not Provided','Paid','0000000000',0),(5,4,5,1,4,400.00,'2025-10-26 18:08:06','Accepted','Address Not Provided','Paid','0000000000',1),(6,7,5,4,1,150.00,'2025-10-26 18:10:01','Cancelled','Address Not Provided','Paid','0000000000',0),(7,6,5,1,1,60.00,'2025-10-26 18:53:25','Pending','Address Not Provided','Paid','0000000000',1),(8,8,7,6,1,50.00,'2025-10-28 10:08:43','Cancelled','Address Not Provided','Paid','0000000000',1),(9,3,7,3,1,50.00,'2025-11-07 16:31:34','Cancelled','Address Not Provided','Paid','0000000000',0),(10,9,7,6,1,40.00,'2025-10-28 10:10:31','Pending','Address Not Provided','Paid','0000000000',0),(11,5,7,1,1,120.00,'2025-11-01 05:40:03','Pending','Address Not Provided','Paid','0000000000',0),(12,11,10,9,1,50.00,'2025-11-22 10:35:52','Accepted','Address Not Provided','Paid','0000000000',1),(13,10,10,8,1,50.00,'2025-11-02 16:43:06','Pending','Address Not Provided','Paid','0000000000',0),(14,15,7,11,1,50.00,'2025-11-07 16:31:44','Cancelled','Address Not Provided','Paid','0000000000',0),(15,16,7,9,1,50.00,'2025-11-22 10:30:32','Cancelled','Address Not Provided','Paid','0000000000',1),(16,3,7,3,2,100.00,'2025-11-22 10:40:37','Cancelled','Address Not Provided','Paid','0000000000',0);
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `products` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `farmer_id` int(11) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `description` text,
  `price` decimal(10,2) DEFAULT NULL,
  `quantity` int(11) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `category` varchar(50) NOT NULL DEFAULT 'generic',
  PRIMARY KEY (`id`),
  KEY `farmer_id` (`farmer_id`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`farmer_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (3,3,'tomato','per kg',50.00,1,NULL,'vegetables'),(4,1,'fruits','per kg',100.00,-3,'e24a2837f7044e12a73e940e8a01cc01_fruits.jpeg','fruits'),(5,1,'potato','fresh',120.00,0,NULL,'vegetables'),(6,1,'carrot','fresh',60.00,0,'Carrot.jpg','vegetables'),(7,4,'carrot','per kg',150.00,1,'Carrot.jpg','vegetables'),(8,6,'potato','fresh and direct from farm',50.00,0,NULL,'vegetables'),(9,6,'carrot','fresh',40.00,0,'Carrot.jpg','vegetables'),(10,8,'brinjal','fresh',50.00,0,NULL,'vegetables'),(11,9,'carrot','Fresh',50.00,6,'bae2bb71346d46ccbd051d237f6ee943_Carrot.jpg','vegetables'),(14,11,'alu','fresh',50.00,2,NULL,'vegetables'),(15,11,'tomato','fresh',50.00,5,NULL,'vegetables'),(16,9,'onion','fresh',50.00,49,NULL,'vegetables'),(17,9,'tomato','fresh',100.00,1,NULL,'vegetables');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `user_type` enum('farmer','consumer') DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'SURARAM SPANDANA','abc@gmail.com','scrypt:32768:8:1$Ko0hWg7ejnVwxhXo$2901983c1da4e1f25435186baa9ab63abed4b0ffcb08046926cdcd36e19dcce1b91ed74b6a8d6ee9807ff1d1801375d62c7bd1f63e30518a520046611b754bfc','farmer'),(3,'nisha','pqr@gmail.com','scrypt:32768:8:1$lvv9ma9Z6Dp5f8Bs$c9398bf395787937b3f2559ca42fb5a4e0a74bddc0a72580c4404a4f644726b3eff32811c9ce806fdf38ac56e35e8fde3978ab64b5486cd547b3b727a91cd709','farmer'),(4,'nisha','pqrs@gmail.com','scrypt:32768:8:1$KNKpg5I8ysyt8lIo$046917e96aeae6f29f610e6d94c51fb4e56dce1478f2224b849eb72b948fa56c82b08b39c4f975ee5742fa3b741cbd29283219f2a284a37f07f77a3797e1b2e2','farmer'),(5,'sri','xyz@gmail.com','scrypt:32768:8:1$q9rciuMZs7NgM2HG$f2706925122e0bfa529f57a1b346c0ef3ee76bc4c5d6e7ad94448856c06095d3f62bf346b649b9f8238485b6b5bc9f20683cd47d2e205cdcb68c7e8878794378','consumer'),(6,'sravanthi','sr@gmail.com','scrypt:32768:8:1$PI8tvEJlbgRD5STX$95c140a7816709360796d43f3c89589015c29c863549ec9da844f6069193ec2d36daa508caa3380476ba6f7c9f2253cc6d950f9fcbffc48c8b7c6af16b2976aa','farmer'),(7,'shushumna','bhai@gmail.com','scrypt:32768:8:1$KjMqJuIDXsDcPQyQ$a4940c9f5d66a7cd5c4c1cd221d762e2b0175561354e74ca449ad63aad65af2a5e2421b7a0807d5addd09c7c8e9ab45a5eb5acc6e3720118c94df3a1839c16db','consumer'),(8,'divya','abcd@gmail.com','scrypt:32768:8:1$AQ3jofAVE9g9RaYq$26a24a9fc5154741125fdb27c0e6114ea0cc533fd32400165df80427004bb15722e1fc21045bc5335bc84cdf3f41f8a4644f55b8bb0426e2f8a9ab5227b961bf','farmer'),(9,'Sriharsha','harsha@gmail.com','scrypt:32768:8:1$lt5iTc5OjUqQiZ4w$63423ca427676f7f1081de2a74ad01ee4b01114f554efcfa73ffc62a422c84d8e3f731bdcb2d8d47247d87a09eef57a4658d07d9ac8963619ff3135bd87037e0','farmer'),(10,'Shushumna','shushumna@gmail.com','scrypt:32768:8:1$1Boho1kCzctQj7zK$584b3af1a7bdb5ada9d6659ad8a595865ae737315a20d6caa7c181c40a668fddbf4701342b4de82ea3b688ab84d25cd57af9b943393ba99e9a3d7459fdd5705a','consumer'),(11,'spandana','spandana@gmail.com','scrypt:32768:8:1$Gl0g0Lgqe5mWKDQ8$580b1173a63de0ffe2ae55fcc3c3aa283d91728ea2ea58c3550a423ea676b4cabad9c289237a378d52fb2e1edb437298a9d4e145f10c76058d23789894ead138','farmer'),(12,'consumer','consumer@gmail.com','scrypt:32768:8:1$m9OcUi1gzVhHXVn9$cab8d0cc78e03f17c05d2d8010d6f97881f7e3112bc121ea0bfc8677b9ac9bbcac777b3cf17f1ddd32452d489cb06d4c724fab10d826a530d329e461cb9f5747','consumer'),(13,'farmer','farmer@gmail.com','scrypt:32768:8:1$IgL9DqMqkRUmDuFm$4e20086d67601d6bd5d2cd6dee6714ee8c52a4d08a1595108f872362bd115193fd8e8103e47e0368a77e75cac208adc35f9d95a83d36e4aacb0f6375fbb12e80','farmer');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-15 14:42:40
