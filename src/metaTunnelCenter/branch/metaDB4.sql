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


DROP TABLE IF EXISTS `cmdb_server_basic`;
CREATE TABLE `cmdb_server_basic` (

    `id` int(10) NOT NULL auto_increment ,
    `cmdb_id` int(10) NOT NULL default 0 COMMENT '' ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `state` varchar(10) NOT NULL default '' COMMENT '服务器设备状态',
    `rack` varchar(255) NOT NULL default '' COMMENT '机架信息',
    `service_type` varchar(255) NOT NULL default '' COMMENT '服务类型',
    `is_collect` varchar(10) NOT NULL default '' COMMENT '是否收集',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`),
    unique (an,sn)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `cmdb_ipinfo` add by agent
-- ----------------------------

DROP TABLE IF EXISTS `cmdb_ipinfo`;
CREATE TABLE `cmdb_ipinfo` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `ipv4` varchar(20) NOT NULL default '' COMMENT 'ipv4',
    `ipv6` varchar(50) NOT NULL default '' COMMENT 'ipv6',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)

) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `cmdb_server_tunnelIP` add by tunnel test script
-- ----------------------------

DROP TABLE IF EXISTS `cmdb_server_tunnelIP`;
CREATE TABLE `cmdb_server_tunnelIP` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `tunnel_ip` varchar(100) NOT NULL default '' COMMENT '设备通道IP',
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
    `cpuHT` varchar(12) NOT NULL default '' COMMENT '是否开启超线程',
    `pack` varchar(255) NOT NULL default '' COMMENT 'sina-agent package',
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
    `speed` varchar(20)  default '' COMMENT 'netcard speed',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)

) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `sys_raid` add by agent diffent data
-- ----------------------------

DROP TABLE IF EXISTS `sys_raid`;
CREATE TABLE `sys_raid` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `raid_id` varchar(10) NOT NULL default '' COMMENT 'raid id number',
    `level` varchar(255) NOT NULL default '' COMMENT 'raid level',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;



-- ----------------------------
--  Table structure for `sys_disksize` add by agent diffent data
-- ----------------------------

DROP TABLE IF EXISTS `sys_disksize`;
CREATE TABLE `sys_disksize` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `point` varchar(10) NOT NULL default '' COMMENT 'disk point number',
    `size` varchar(10) NOT NULL default '' COMMENT 'disk size ',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;




-- ----------------------------
--  Table structure for `sys_serverAN` add by agent diffent data
-- ----------------------------

DROP TABLE IF EXISTS `sys_serverAN`;
CREATE TABLE `sys_serverAN` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `server_an` varchar(50) NOT NULL default '' COMMENT 'server 盘点号',
    `server_sn` varchar(100) NOT NULL default '' COMMENT 'server 设备序列号',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;



-- ----------------------------
--  Table structure for `sys_physical_disk` add by agent diffent data
-- ----------------------------

DROP TABLE IF EXISTS `sys_physical_disk`;
CREATE TABLE `sys_physical_disk` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `slot` varchar(10) NOT NULL default '' COMMENT '磁盘位置slot插槽',
    `interface` varchar(20) NOT NULL default '' COMMENT '磁盘接口，SATA，SAS...',
    `size` varchar(10) NOT NULL default '' COMMENT 'disk size ',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `sys_route` add by agent diffent data
-- ----------------------------

DROP TABLE IF EXISTS `sys_route`;
CREATE TABLE `sys_route` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `route` varchar(15) NOT NULL default '' COMMENT 'route ',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;



-- ----------------------------
--  Table structure for `sys_dns` add by agent diffent data
-- ----------------------------

DROP TABLE IF EXISTS `sys_dns`;
CREATE TABLE `sys_dns` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `dns` varchar(15) NOT NULL default '' COMMENT 'route ',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;




-- ----------------------------
--  Table structure for `sys_sudoers` add by agent diffent data
-- ----------------------------

DROP TABLE IF EXISTS `sys_sudoers`;
CREATE TABLE `sys_sudoers` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `user` varchar(255) NOT NULL default '' COMMENT 'root users ',
    `passwd` varchar(50) NOT NULL default '' COMMENT 'root passwd ',
    `rights` varchar(50) NOT NULL default '' COMMENT 'root rights ',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- change will be backup to this tables.

-- ----------------------------
--  Table structure for `chg_os` add by agent
-- ----------------------------

DROP TABLE IF EXISTS `chg_os`;
CREATE TABLE `chg_os` (
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
--  Table structure for `chg_servers` add by agent
-- ----------------------------

DROP TABLE IF EXISTS `chg_servers`;
CREATE TABLE `chg_servers` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `model` varchar(255) NOT NULL default '' COMMENT 'Product Name 设备的型号类型',
    `cpu_cores` varchar(4) NOT NULL default '' COMMENT 'Processor number',
    `cpu_numbers` varchar(4) NOT NULL default '' COMMENT 'Physical CPU number',
    `mem_total` varchar(12) NOT NULL default '' COMMENT '内存总量',
     -- `mem_max` varchar(12) NOT NULL default '' COMMENT '可支持最大内存量',
    `swap_total` varchar(12) NOT NULL default '' COMMENT 'swap 总量',
    `cpuHT` varchar(12) NOT NULL default '' COMMENT '是否开启超线程',
    `pack` varchar(255) NOT NULL default '' COMMENT 'sina-agent package',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `chg_ipinfos` add by agent
-- ----------------------------

DROP TABLE IF EXISTS `chg_ipinfos`;
CREATE TABLE `chg_ipinfos` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `ipv4` varchar(20) NOT NULL default '' COMMENT 'ipv4',
    `ipv6` varchar(50) NOT NULL default '' COMMENT 'ipv6',
    `mac` varchar(20) NOT NULL default '' COMMENT 'mac address',
    `speed` varchar(20)  default '' COMMENT 'netcard speed',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)

) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `chg_raid` add by agent diffent data
-- ----------------------------

DROP TABLE IF EXISTS `chg_raid`;
CREATE TABLE `chg_raid` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `raid_id` varchar(10) NOT NULL default '' COMMENT 'raid id number',
    `level` varchar(255) NOT NULL default '' COMMENT 'raid level',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;



-- ----------------------------
--  Table structure for `chg_disksize` add by agent diffent data
-- ----------------------------

DROP TABLE IF EXISTS `chg_disksize`;
CREATE TABLE `chg_disksize` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `point` varchar(10) NOT NULL default '' COMMENT 'disk point number',
    `size` varchar(10) NOT NULL default '' COMMENT 'disk size ',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;




-- ----------------------------
--  Table structure for `chg_serverAN` add by agent diffent data
-- ----------------------------

DROP TABLE IF EXISTS `chg_serverAN`;
CREATE TABLE `chg_serverAN` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `server_an` varchar(50) NOT NULL default '' COMMENT 'server 盘点号',
    `server_sn` varchar(100) NOT NULL default '' COMMENT 'server 设备序列号',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;



-- ----------------------------
--  Table structure for `chg_physical_disk` add by agent diffent data
-- ----------------------------

DROP TABLE IF EXISTS `chg_physical_disk`;
CREATE TABLE `chg_physical_disk` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `slot` varchar(10) NOT NULL default '' COMMENT '磁盘位置slot插槽',
    `interface` varchar(20) NOT NULL default '' COMMENT '磁盘接口，SATA，SAS...',
    `size` varchar(10) NOT NULL default '' COMMENT 'disk size ',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
--  Table structure for `chg_route` add by agent diffent data
-- ----------------------------

DROP TABLE IF EXISTS `chg_route`;
CREATE TABLE `chg_route` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `route` varchar(15) NOT NULL default '' COMMENT 'route ',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;



-- ----------------------------
--  Table structure for `chg_dns` add by agent diffent data
-- ----------------------------

DROP TABLE IF EXISTS `chg_dns`;
CREATE TABLE `chg_dns` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `dns` varchar(15) NOT NULL default '' COMMENT 'route ',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;




-- ----------------------------
--  Table structure for `chg_sudoers` add by agent diffent data
-- ----------------------------

DROP TABLE IF EXISTS `chg_sudoers`;
CREATE TABLE `chg_sudoers` (

    `id` int(10) NOT NULL auto_increment ,
    `an` varchar(50) NOT NULL default '' COMMENT '盘点号',
    `sn` varchar(100) NOT NULL default '' COMMENT '设备序列号',
    `user` varchar(255) NOT NULL default '' COMMENT 'root users ',
    `passwd` varchar(50) NOT NULL default '' COMMENT 'root passwd ',
    `rights` varchar(50) NOT NULL default '' COMMENT 'root rights ',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;




-- ----------------------------
--  Table structure for `lnk_servers` add by agent diffent data
-- ----------------------------

DROP TABLE IF EXISTS `lnk_servers`;
CREATE TABLE `lnk_servers` (

    `id` int(10) NOT NULL auto_increment ,
    `server_ip` varchar(20) NOT NULL default '' COMMENT 'server_ip',
    `switch_ip` varchar(20) NOT NULL default '' COMMENT 'switch_ip',
    `switch_port` varchar(500) NOT NULL default '' COMMENT 'switch port',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;



-- ----------------------------
--  Table structure for `lnk_switchs` add by agent diffent data
-- ----------------------------

DROP TABLE IF EXISTS `lnk_switchs`;
CREATE TABLE `lnk_switchs` (

    `id` int(10) NOT NULL auto_increment ,
    `switch_from` varchar(20) NOT NULL default '' COMMENT 'switch from ',
    `switch_from_port` varchar(500) NOT NULL default '' COMMENT 'switch from port',
    `switch_to` varchar(20) NOT NULL default '' COMMENT 'switch to',
    `switch_to_port` varchar(500) NOT NULL default '' COMMENT 'switch_to port',
    `ctime` datetime NOT NULL default '0000-00-00 00:00:00' COMMENT ' 创建时间 ',
    PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


CREATE TABLE `new_server_checks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `job_id` int(11) NOT NULL,
  `i_id` varchar(255) NOT NULL,
  `asset_number` varchar(255) NOT NULL,
  `ip` varchar(255) NOT NULL,
  `state` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;





