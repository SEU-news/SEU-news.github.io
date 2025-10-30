<!-- src/views/500.vue -->
<template>
  <div class="server-error container mt-5 text-center">
    <h1 class="display-4">500</h1>
    <h2>Server Error</h2>
    <p class="lead">
      The server encountered an internal error and was unable to complete your request.
      Either the server is overloaded or there is an error in the application.
    </p>
    <router-link to="/" class="btn btn-primary">Return to Home</router-link>
  </div>
</template>

<script setup>
// 这里不需要额外逻辑
</script>

<style scoped>
.server-error {
  min-height: 70vh; /* 让页面垂直居中更好看 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.server-error h1 {
  font-size: 6rem;
  margin-bottom: 0.5rem;
}

.server-error h2 {
  margin-bottom: 1.5rem;
}

.server-error .lead {
  max-width: 600px;
  margin: 0 auto 2rem;
}
</style>
