<!-- src/views/403.vue -->
<template>
  <div class="forbidden container mt-5 text-center">
    <h1 class="display-4">403</h1>
    <h2>Forbidden</h2>
    <p class="lead">
      You don't have permission to access the requested resource.
      This might be due to insufficient privileges or access restrictions.
    </p>
    <router-link to="/" class="btn btn-primary">Return to Home</router-link>
  </div>
</template>

<script setup>
// 目前不需要额外逻辑
</script>

<style scoped>
.forbidden {
  min-height: 70vh; /* 让页面垂直居中更好看 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.forbidden h1 {
  font-size: 6rem;
  margin-bottom: 0.5rem;
}

.forbidden h2 {
  margin-bottom: 1.5rem;
}

.forbidden .lead {
  max-width: 600px;
  margin: 0 auto 2rem;
}
</style>
