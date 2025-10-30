<template>
  <div class="home">
    <h1>至善新声门户</h1>
    <p>欢迎访问 News</p>
    <div class="features">
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
  </div>

  <div class="home">
    <div class="features">
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
</template>

<style scoped>
.home {
  text-align: center;
  padding: 2rem;
}

.features {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-top: 3rem;
}

.feature-card {
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  padding: 1.5rem;
  width: 200px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: 0.2s;
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
