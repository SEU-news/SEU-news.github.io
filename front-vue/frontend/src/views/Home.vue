<template>
  <div class="home">
    <h1>至善新声门户</h1>
    <p>欢迎访问 News</p>
    <a href="http://49.235.51.123:42610"> 旧的系统 </a>

    <div class="home-container">

      <!-- 左侧 PDF -->
      <div class="pdf-card">
        <h3>最新公告 PDF</h3>
        <iframe src="http://49.235.51.123:42610/static/latest.pdf" width="100%" height="600px" style="border:none;"></iframe>
      </div>

      <!-- 右侧功能卡片 -->
      <div class="features_column">
        <div class="features_row">
          <div class="feature-card">
            <h3>最新动态</h3>
            <p>了解校园最新消息</p>
          </div>
          <div class="feature-card">
            <h3>学术资讯</h3>
            <p>掌握学术前沿信息</p>
          </div>
          <div class="feature-card">
            <h3>校园生活</h3>
            <p>关注校园文化活动</p>
          </div>
        </div>
        <div class="features_row">
          <router-link to="/login" class="feature-card link-card">
            <h3>访客登录</h3>
            <p>进入访客系统</p>
          </router-link>

          <router-link to="/admin-login" class="feature-card link-card">
            <h3>管理登录</h3>
            <p>后台管理入口</p>
          </router-link>

          <router-link to="/contact" class="feature-card link-card">
            <h3>联系我们</h3>
            <p>欢迎留言</p>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  text-align: center;
  padding: 0.5rem;
}

.home-container {
  display: flex;
  gap: 2rem;
  justify-content: center;
  align-items: flex-start;
  flex-wrap: wrap; /* 小屏幕自动换行 */
  padding: 2rem;
}

/* PDF 卡片 */
.pdf-card {
  flex: 2 1 300px; /* 左侧宽度可伸缩，最小300px */
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  padding: 1rem;
  background: #fff;
}

/* 功能卡片 */
.features_row {
  flex: 1 1 250px; /* 右侧宽度可伸缩，最小250px */
  display: flex;
  flex-direction: row;
  gap: 1rem;
}

.features_column {
  flex: 1 1 250px; /* 右侧宽度可伸缩，最小250px */
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.feature-card {
  display: flex;            /* flex 布局，统一行为 */
  flex-direction: column;   /* 纵向排列标题和文字 */
  justify-content: center;  /* 内容垂直居中 */
  align-items: center;      /* 水平居中 */
  min-width: 150px;         /* 最小宽度，保证一致 */
  flex: 1;                  /* 平分父容器 */
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: 0.2s;
  text-align: center;       /* 文字居中 */
}


/* 鼠标悬停时美化 */
.feature-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transform: translateY(-3px);
}

/* 让 router-link 看起来像卡片 */
.link-card {
  text-decoration: none;
  color: inherit;
}

</style>
<script setup lang="ts">
</script>
