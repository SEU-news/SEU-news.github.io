<!-- src/views/400.vue -->
<template>
  <div class="bad-request container mt-5 text-center">
    <h1 class="display-4">400</h1>
    <h2>Bad Request</h2>
    <p class="lead">
      The server could not understand the request due to invalid syntax or malformed request.
      Please check your request and try again.
    </p>
    <router-link to="/" class="btn btn-primary">Return to Home</router-link>
  </div>
</template>

<script setup>
// 这里不需要额外逻辑
</script>

<style scoped>
.bad-request {
  min-height: 70vh; /* 让页面垂直居中更好看 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.bad-request h1 {
  font-size: 6rem;
  margin-bottom: 0.5rem;
}

.bad-request h2 {
  margin-bottom: 1.5rem;
}

.bad-request .lead {
  max-width: 600px;
  margin: 0 auto 2rem;
}
</style>
