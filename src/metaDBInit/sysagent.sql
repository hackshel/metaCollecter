/*
 Navicat Premium Data Transfer

 Source Server         : system Agent
 Source Server Type    : MySQL
 Source Server Version : 50077

 Target Server Type    : MySQL
 Target Server Version : 50077
 File Encoding         : utf-8
 Author                : xiaochen2
 Date: 10/16/2013 19:40:10 PM
*/


SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

DROP DATABASE IF EXISTS `metaDB`;
CREATE DATABASE IF NOT EXISTS `metaDB` default charset utf8 COLLATE utf8_general_ci;
USE `metaDB`;

-- ----------------------------
--  Table structure for `sys_server_basic` add by cmdb API
-- ----------------------------



DROP TABLE IF EXISTS `sys_server_basic`;
CREATE TABLE `sys_server_basic` (

    `id` int(10) NOT NULL auto_increment ,
    `cmdb_id` int(10) NOT NULL default '' COMMENT '' ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `tunnel_ip` varchar(100) NOT NULL default '' COMMENT '设备通道IP',
    `state` varchar(10) NOT NULL default '' COMMENT '服务器设备状态',
    `rack` varchar(255) NOT NULL default '' COMMENT '机架信息',
    `service_type` varchar(255) NOT NULL default '' COMMENT '服务类型',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`),
    unique (an,sn)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;



-- ----------------------------
--  Table structure for `sys_servers` add by agent
-- ----------------------------

DROP TABLE IF EXISTS `sys_servers`;
CREATE TABLE `sys_servers` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `model` varchar(255) NOT NULL default '' COMMENT 'Product Name 设备的型号类型',
    `cpu_cores` varchar(4) NOT NULL default '' COMMENT 'Processor number',
    `cpu_numbers` varchar(4) NOT NULL default '' COMMENT 'Physical CPU number',
    `mem_total` varchar(12) NOT NULL default '' COMMENT '内存总量',
     -- `mem_max` varchar(12) NOT NULL default '' COMMENT '可支持最大内存量',
    `swap_total` varchar(12) NOT NULL default '' COMMENT 'swap 总量',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `sys_os` add by agent
-- ----------------------------

DROP TABLE IF EXISTS `sys_os`;
CREATE TABLE `sys_os` (
    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `os_type` varchar(20) NOT NULL default '' COMMENT '操作系统类型',
    `os_kernel` varchar(50) NOT NULL default '' COMMENT '内核版本',
    `os_platform` varchar(20) NOT NULL default '' COMMENT '平台32/64bit',
    `os_release` varchar(30) NOT NULL default '' COMMENT '发行系统',
    `os_version` varchar(5) NOT NULL default '' COMMENT '版本',
    `os_hostname` varchar(100) NOT NULL default '' COMMENT '主机hostname',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `sys_ipinfos` add by agent
-- ----------------------------

DROP TABLE IF EXISTS `sys_ipinfos`;
CREATE TABLE `sys_ipinfos` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `ipv4` varchar(20) NOT NULL default '' COMMENT 'ipv4',
    `ipv6` varchar(50) NOT NULL default '' COMMENT 'ipv6',
    `mac` varchar(20) NOT NULL default '' COMMENT 'mac address',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)

) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `sys_switch_list` add by cmdb api
-- ----------------------------

DROP TABLE IF EXISTS `sys_switch_list`;
CREATE TABLE `sys_switch_list` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `ipv4` varchar(20) NOT NULL default '' COMMENT 'ipv4',
    `ipv6` varchar(50) NOT NULL default '' COMMENT 'ipv6',
    `state` varchar(10) NOT NULL default '' COMMENT '交换机设备状态',
    `rack` varchar(255) NOT NULL default '' COMMENT '机架信息',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)

) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;



-- ----------------------------
--  Table structure for `sys_connect_relation` add  by agent
-- ----------------------------

DROP TABLE IF EXISTS `sys_connect_relation`;
CREATE TABLE `sys_connect_relation` (

    `id` int(10) NOT NULL auto_increment ,
    `switch_an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `switch_sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `server_an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `server_sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `switch_port` varchar(255) NOT NULL default '' COMMENT '交换机的端口号',
    `server_mac` varchar(20) NOT NULL default '' COMMENT 'server mac address',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',

    PRIMARY KEY  (`id`)

) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

GRANT ALL on collecter.* to 'systemagen'@'%'  IDENTIFIED BY "sina.com";
