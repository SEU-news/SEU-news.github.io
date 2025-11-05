<!-- src/views/404.vue -->
<template>
  <div class="not-found container mt-5 text-center">
    <h1 class="display-4">404</h1>
    <h2>Not Found</h2>
    <p class="lead">
      The requested URL was not found on the server.
      If you entered the URL manually please check your spelling and try again.
    </p>
    <router-link to="/" class="btn btn-primary">Return to Home</router-link>
  </div>
</template>

<script setup>
// 这里不需要额外逻辑
</script>

<style scoped>
.not-found {
  min-height: 70vh; /* 让页面垂直居中更好看 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.not-found h1 {
  font-size: 6rem;
  margin-bottom: 0.5rem;
}

.not-found h2 {
  margin-bottom: 1.5rem;
}

.not-found .lead {
  max-width: 600px;
  margin: 0 auto 2rem;
}
</style>
