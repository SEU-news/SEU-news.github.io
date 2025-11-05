# 样式库使用说明

## 概述

本目录包含项目的共享样式库，旨在提供统一的UI组件样式，减少重复代码，提高开发效率和维护性。

## 文件说明

- [layout.css](./layout.css) - 包含基础布局样式，如容器、网格系统、标题等
- [utilities.css](./utilities.css) - 包含通用工具类，如间距、flexbox、文本对齐等
- [buttons.css](./buttons.css) - 包含按钮样式
- [forms.css](./forms.css) - 包含表单控件样式
- [tables.css](./tables.css) - 包含表格样式
- [alerts.css](./alerts.css) - 包含提示信息样式
- [navigation.css](./navigation.css) - 包含导航和分页样式

## 使用方法

在Vue组件的样式部分通过[@import](file:///d:/pythonProj/seu-news/front-vue/frontend/src/api/user.js#L14-L28)指令引入需要的样式文件：

```vue
<style scoped>
@import './layout.css';
@import './buttons.css';

/* 组件特有样式 */
.component-specific-style {
  /* ... */
}
</style>
```

或者，如果需要所有样式，可以全部引入：

```vue
<style scoped>
@import './layout.css';
@import './utilities.css';
@import './buttons.css';
@import './forms.css';
@import './tables.css';
@import './alerts.css';
@import './navigation.css';

/* 组件特有样式 */
.component-specific-style {
  /* ... */
}
</style>
```

## 样式类说明

### 布局类 (layout.css)
- `.container` - 页面容器
- `.row` - 行布局
- `.col-md-6` - 列布局

### 工具类 (utilities.css)
- `.mt-5` - 上边距
- `.mb-2`, `.mb-3`, `.mb-4` - 下边距
- `.me-2`, `.ms-2` - 左右边距
- `.ms-auto` - 自动左边距
- `.d-flex` - Flex布局
- `.justify-content-between` - 两端对齐
- `.justify-content-center` - 居中对齐
- `.align-items-center` - 垂直居中

### 按钮类 (buttons.css)
- `.btn` - 基础按钮
- `.btn-primary` - 主要按钮
- `.btn-secondary` - 次要按钮
- `.btn-success` - 成功按钮
- `.btn-danger` - 危险按钮
- `.btn-info` - 信息按钮
- `.btn-warning` - 警告按钮
- `.btn-outline-primary` - 轮廓主要按钮
- `.btn-outline-secondary` - 轮廓次要按钮
- `.btn-sm` - 小按钮

### 表单类 (forms.css)
- `.form-control` - 表单控件
- `.form-select` - 选择框
- `.input-group` - 输入组

### 表格类 (tables.css)
- `.table` - 基础表格
- `.table-hover` - 悬停效果表格
- `.table-secondary` - 次要状态
- `.table-info` - 信息状态
- `.table-success` - 成功状态
- `.table-danger` - 危险状态
- `.table-primary` - 主要状态

### 提示信息类 (alerts.css)
- `.alert` - 基础提示
- `.alert-info` - 信息提示

### 导航类 (navigation.css)
- `.pagination` - 分页容器
- `.page-item` - 分页项
- `.page-link` - 分页链接

## 维护说明

1. 添加新的样式类时，应根据功能放入对应的文件中
2. 避免在基础样式中添加过于具体的样式规则
3. 组件特有样式应写在组件内部，不要添加到基础样式中
4. 更新基础样式时要考虑对现有组件的影响