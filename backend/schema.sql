CREATE DATABASE IF NOT EXISTS dance_king DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE dance_king;

-- 1. 用户表 (Users)
CREATE TABLE IF NOT EXISTS `users` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `openid` VARCHAR(100) UNIQUE NOT NULL COMMENT '微信OpenID',
  `nickname` VARCHAR(100),
  `avatar_url` VARCHAR(255),
  `phone` VARCHAR(20),
  `role` TINYINT DEFAULT 0 COMMENT '0:普通用户, 1:认证商家, 9:超级管理员',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 舞厅主表 (Dance Halls)
CREATE TABLE IF NOT EXISTS `dance_halls` (
  `id` BIGINT PRIMARY KEY COMMENT '主键，直接复用舞图图的ID以便同步',
  `name` VARCHAR(100) NOT NULL,
  `province` VARCHAR(50),
  `city` VARCHAR(50),
  `address` VARCHAR(255),
  `longitude` DECIMAL(10, 6),
  `latitude` DECIMAL(10, 6),
  `location` POINT SRID 4326 NOT NULL COMMENT '空间索引字段，用于快速计算距离',
  `open_status` TINYINT DEFAULT 1 COMMENT '0:停业, 1:营业中',
  `hot` TINYINT DEFAULT 0 COMMENT '1:热门(需高频抓取), 0:普通',
  
  -- 营业时间与票价 (通过 detail 接口获取)
  `morning_hours` VARCHAR(50),
  `afternoon_hours` VARCHAR(50),
  `evening_hours` VARCHAR(50),
  `ticket_price` VARCHAR(255),
  
  -- 商家动态/公告
  `moment_text` VARCHAR(500) COMMENT '紧急公告内容',
  `moment_updated_at` DATETIME NULL COMMENT '公告发布时间',
  
  `owner_user_id` BIGINT NULL COMMENT '商家认领后的关联的用户ID',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  SPATIAL INDEX(`location`)
);

-- 3. 认领申请表 (Claim Applications)
CREATE TABLE IF NOT EXISTS `claim_applications` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id` BIGINT NOT NULL COMMENT '申请人ID',
  `dance_hall_id` BIGINT NULL COMMENT '关联的舞厅ID(可选，也可能提交新舞厅)',
  `venue_name` VARCHAR(100) NOT NULL,
  `city` VARCHAR(50),
  `address` VARCHAR(255),
  `applicant_name` VARCHAR(50),
  `contact_phone` VARCHAR(20),
  `contact_wechat` VARCHAR(50),
  `relationship` VARCHAR(20) COMMENT '老板/经理/工作人员',
  `license_images` JSON COMMENT '图片URL数组',
  `extra_notes` TEXT,
  `status` TINYINT DEFAULT 0 COMMENT '0:待审核, 1:已通过, 2:已驳回',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 4. 广告配置表 (Advertisements)
CREATE TABLE IF NOT EXISTS `advertisements` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `position` VARCHAR(20) COMMENT 'top_banner(顶部大图) 或 list_card(列表卡片)',
  `title` VARCHAR(100) COMMENT '如: 某高端KTV',
  `image_url` VARCHAR(255) NOT NULL,
  `target_link` VARCHAR(255) COMMENT '跳转路径或外部小程序APPID',
  `is_active` TINYINT DEFAULT 1 COMMENT '1:上架, 0:下架',
  `sort_weight` INT DEFAULT 0 COMMENT '用于控制在列表中的插入位置',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 系统配置表 (System Config)
CREATE TABLE IF NOT EXISTS `system_config` (
  `config_key` VARCHAR(50) PRIMARY KEY,
  `config_value` TEXT,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
