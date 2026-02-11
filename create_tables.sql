-- 表创建脚本
-- 手动创建表，不使用 migrate

USE seu_news;

-- Django Session 表（用于管理用户会话）
CREATE TABLE IF NOT EXISTS `django_session` (
    `session_key` varchar(40) NOT NULL COMMENT 'Session密钥',
    `session_data` longtext NOT NULL COMMENT 'Session数据（JSON格式）',
    `expire_date` datetime(6) NOT NULL COMMENT 'Session过期时间',
    PRIMARY KEY (`session_key`),
    KEY `django_session_expire_date_idx` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Django用户会话表：存储用户登录状态和会话数据';


CREATE TABLE
  `user_info` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '唯一主键',
    `username` VARCHAR(30) NOT NULL COMMENT '用户名',
    `password_MD5` VARCHAR(100) NOT NULL COMMENT '密码MD5值',
    
    `avatar` VARCHAR(100) DEFAULT NULL COMMENT '用户头像图片名',

    `realname` VARCHAR(30) NOT NULL COMMENT '真名',
    `student_id` VARCHAR(30) NOT NULL COMMENT '学号',    
    
    `role` INT UNSIGNED NOT NULL COMMENT '权限位',
    
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_username` (`username`),
    KEY `idx_realname` (`realname`),
    KEY `idx_student_id` (`student_id`),
    key `idx_created_at` (`created_at`),
    key `idx_updated_at` (`updated_at`)
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户信息';
ALTER TABLE `user_info`
  ADD COLUMN `last_login` DATETIME NULL COMMENT '最后登录时间' AFTER `updated_at`;



CREATE TABLE `content_management` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '唯一主键',
    `creator_id` INT NOT NULL COMMENT '创建者用户ID',
    `describer_id` INT NOT NULL COMMENT '描述者用户ID',
    `reviewer_id` INT DEFAULT NULL COMMENT '审核者用户ID',
    
    `title` VARCHAR(200) NOT NULL COMMENT '内容标题',
    `short_title` VARCHAR(100) DEFAULT NULL COMMENT '短标题（用于展示）',
    `link` TEXT NOT NULL COMMENT '内容链接地址',
    `content` TEXT NOT NULL COMMENT '详细内容',
    `deadline` DATETIME DEFAULT NULL COMMENT '截止时间',
    `image_list` TEXT NOT NULL DEFAULT ('[]') COMMENT '图片list，json格式的[]',
    `publish_at` DATETIME DEFAULT NULL COMMENT '发布时间',
    
    `type` VARCHAR(50) NOT NULL COMMENT '内容类型：新闻、竞赛等',
    `tag` TEXT DEFAULT NULL COMMENT '内容标签，JSON格式的list，比较自由',
    `status` VARCHAR(50) NOT NULL DEFAULT 'draft' COMMENT '状态：draft/pending/reviewed/published/rejected',
    `locker_id` INT DEFAULT NULL COMMENT '当前锁定者用户ID',
    `locked_at` DATETIME DEFAULT NULL COMMENT '锁定时间',
    
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    
    PRIMARY KEY (`id`),
    KEY `idx_creator_id` (`creator_id`),
    KEY `idx_describer_id` (`describer_id`),
    KEY `idx_reviewer_id` (`reviewer_id`),

    KEY `idx_status` (`status`),
    KEY `idx_type` (`type`),
 
    KEY `idx_deadline` (`deadline`),
    KEY `idx_publish_at` (`publish_at`),
    key `idx_created_at` (`created_at`),
    key `idx_updated_at` (`updated_at`)
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '内容管理系统：用于管理多状态内容生命周期，支持协作编辑和审核流程';

CREATE TABLE
  `comment_management` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '唯一主键',
    `comment` TEXT NOT NULL COMMENT '评论内容',
    `creator_id` INT NOT NULL COMMENT '评论创建者ID',
    `news_id` INT NOT NULL COMMENT '关联新闻ID',
    `parent_comment_id` INT DEFAULT NULL COMMENT '回复的上级评论ID（NULL表示顶层评论）',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_creator_id` (`creator_id`),
    KEY `idx_news_id` (`news_id`),
    KEY `idx_parent_comment_id` (`parent_comment_id`),
    KEY `idx_created_at` (`created_at`),
    KEY `idx_updated_at` (`updated_at`)
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '评论管理系统：管理用户对新闻的评论及回复关系';
