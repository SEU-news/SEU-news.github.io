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
</template>

<script setup lang="ts">
// 首页逻辑
</script>

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
}
</style>
