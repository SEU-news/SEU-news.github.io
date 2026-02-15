-- ===================================================================
-- SEU News 数据库表创建脚本
-- ===================================================================
-- 说明:
--   - 手动创建表，不使用 Django migrate
--   - 表名与 Django models.db_table 对应
--   - 字段名与 Django models 定义保持一致
-- ===================================================================
-- 数据库: seu_news
-- 字符集: utf8mb4
-- 排序规则: utf8mb4_0900_ai_ci
-- 引擎: InnoDB
-- ===================================================================

USE seu_news;


-- ===================================================================
-- Table 1: user_info
-- ===================================================================
-- 说明: 用户信息表，存储用户账号、权限和基本信息
-- ===================================================================

CREATE TABLE IF NOT EXISTS `user_info` (
    -- 主键
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '唯一主键',

    -- 账号信息
    `username` VARCHAR(30) NOT NULL COMMENT '用户名（唯一）',
    `password_MD5` VARCHAR(100) NOT NULL COMMENT '密码 MD5 哈希值',

    -- 个人信息
    `avatar` VARCHAR(100) DEFAULT NULL COMMENT '用户头像图片名',
    `realname` VARCHAR(30) NOT NULL COMMENT '真实姓名',
    `student_id` VARCHAR(30) NOT NULL COMMENT '学号',

    -- 权限系统（位掩码）
    -- 0 (0b00): 普通用户
    -- 1 (0b01): 编辑（可创建/编辑/删除内容）
    -- 2 (0b10): 管理员（可管理用户、DDL）
    -- 3 (0b11): 超级管理员（兼具编辑和管理员权限）
    `role` INT UNSIGNED NOT NULL COMMENT '权限位（0:用户 1:编辑 2:管理员 3:超管）',

    -- 时间戳
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '账号创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    `last_login` DATETIME DEFAULT NULL COMMENT '最后登录时间',

    -- 索引
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_username` (`username`),
    KEY `idx_realname` (`realname`),
    KEY `idx_student_id` (`student_id`),
    KEY `idx_created_at` (`created_at`),
    KEY `idx_updated_at` (`updated_at`)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  COMMENT = '用户信息表：存储用户账号、权限和个人资料';


-- ===================================================================
-- Table 2: content_management
-- ===================================================================
-- 说明: 内容管理表，支持多状态内容生命周期管理
-- ===================================================================

CREATE TABLE IF NOT EXISTS `content_management` (
    -- 主键
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '唯一主键',

    -- 协作角色（三人协作机制）
    `creator_id` INT NOT NULL COMMENT '创建者用户ID',
    `describer_id` INT NOT NULL COMMENT '描述者用户ID',
    `reviewer_id` INT DEFAULT NULL COMMENT '审核者用户ID',

    -- 内容基本信息
    `title` VARCHAR(200) NOT NULL COMMENT '内容标题',
    `short_title` VARCHAR(100) DEFAULT NULL COMMENT '短标题（用于展示）',
    `link` TEXT NOT NULL COMMENT '内容链接地址',
    `content` TEXT NOT NULL COMMENT '详细内容',
    `type` VARCHAR(50) NOT NULL COMMENT '内容类型（教务/竞赛/活动等）',
    `tag` TEXT DEFAULT NULL COMMENT '内容标签（自由文本）',

    -- 时间相关
    `deadline` DATETIME DEFAULT NULL COMMENT '截止时间（DDL）',
    `publish_at` DATETIME DEFAULT NULL COMMENT '实际发布时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',

    -- 媒体资源
    `image_list` TEXT NOT NULL DEFAULT ('[]') COMMENT '图片列表（JSON数组格式）',

    -- 状态管理
    -- draft: 草稿（初始状态）
    -- pending: 待审核（提交审核）
    -- reviewed: 已审核（通过审核）
    -- rejected: 已拒绝（审核未通过）
    -- published: 已发布（正式发布）
    -- terminated: 已终止（取消/删除）
    `status` VARCHAR(50) NOT NULL DEFAULT 'draft' COMMENT '内容状态',

    -- 并发控制
    `locker_id` INT DEFAULT NULL COMMENT '当前锁定者用户ID（防止并发编辑）',
    `locked_at` DATETIME DEFAULT NULL COMMENT '锁定时间戳',

    -- 索引
    PRIMARY KEY (`id`),
    KEY `idx_creator_id` (`creator_id`),
    KEY `idx_describer_id` (`describer_id`),
    KEY `idx_reviewer_id` (`reviewer_id`),
    KEY `idx_status` (`status`),
    KEY `idx_type` (`type`),
    KEY `idx_deadline` (`deadline`),
    KEY `idx_publish_at` (`publish_at`),
    KEY `idx_created_at` (`created_at`),
    KEY `idx_updated_at` (`updated_at`)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  COMMENT = '内容管理表：管理多状态内容生命周期，支持三人协作（创建/描述/审核）和并发编辑控制';


-- ===================================================================
-- Table 3: comment_management
-- ===================================================================
-- 说明: 评论管理表，支持评论和回复功能
-- ===================================================================

CREATE TABLE IF NOT EXISTS `comment_management` (
    -- 主键
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '唯一主键',

    -- 评论内容
    `comment` TEXT NOT NULL COMMENT '评论内容',

    -- 关联信息
    `creator_id` INT NOT NULL COMMENT '评论创建者用户ID',
    `news_id` INT NOT NULL COMMENT '关联新闻ID',
    `parent_comment_id` INT DEFAULT NULL COMMENT '回复的上级评论ID（NULL表示顶层评论）',

    -- 时间戳
    `created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',

    -- 索引
    PRIMARY KEY (`id`),
    KEY `idx_creator_id` (`creator_id`),
    KEY `idx_news_id` (`news_id`),
    KEY `idx_parent_comment_id` (`parent_comment_id`),
    KEY `idx_created` (`created`),
    KEY `idx_updated` (`updated`)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  COMMENT = '评论管理表：管理用户对新闻的评论及层级回复关系';


-- ===================================================================
-- Table 4: django_session
-- ===================================================================
-- 说明: Django 会话表，用于管理用户登录状态和会话数据
-- ===================================================================

CREATE TABLE IF NOT EXISTS `django_session` (
    -- 主键
    `session_key` VARCHAR(40) NOT NULL COMMENT 'Session 密钥（唯一标识）',

    -- 会话数据
    `session_data` LONGTEXT NOT NULL COMMENT 'Session 数据（JSON 格式编码）',
    `expire_date` DATETIME(6) NOT NULL COMMENT 'Session 过期时间（精确到微秒）',

    -- 索引
    PRIMARY KEY (`session_key`),
    KEY `django_session_expire_date_idx` (`expire_date`)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  COMMENT = 'Django 会话表：存储用户登录状态和会话数据';


-- ===================================================================
-- 表结构验证
-- ===================================================================
-- 运行以下命令验证表是否创建成功：
--
--   SHOW TABLES;
--   DESCRIBE user_info;
--   DESCRIBE content_management;
--   DESCRIBE comment_management;
--   DESCRIBE django_session;
--
-- ===================================================================


-- ===================================================================
-- 索引说明
-- ===================================================================
-- user_info:
--   - idx_username: 登录查询优化
--   - idx_realname: 按姓名搜索优化
--   - idx_student_id: 按学号搜索优化
--   - idx_created_at/updated_at: 时间排序优化
--
-- content_management:
--   - idx_creator_id/describer_id/reviewer_id: 用户关联查询优化
--   - idx_status: 按状态筛选优化
--   - idx_type: 按类型筛选优化
--   - idx_deadline: DDL 查询优化
--   - idx_publish_at: 按发布时间排序优化
--   - idx_created_at/updated_at: 时间排序优化
--
-- comment_management:
--   - idx_creator_id: 按用户查询评论
--   - idx_news_id: 按新闻查询评论
--   - idx_parent_comment_id: 评论层级查询
--   - idx_created/updated: 时间排序优化
--
-- django_session:
--   - django_session_expire_date_idx: 过期会话清理优化
--
-- ===================================================================
