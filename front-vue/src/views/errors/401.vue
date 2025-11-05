<!-- src/views/401.vue -->
<template>
  <div class="unauthorized container mt-5 text-center">
    <h1 class="display-4">401</h1>
    <h2>Unauthorized</h2>
    <p class="lead">
      The server could not verify that you are authorized to access the URL requested.
      You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required.
    </p>
    <router-link to="/" class="btn btn-primary">Return to Home</router-link>
  </div>
</template>

<script setup>
// 这里不需要额外逻辑
</script>

<style scoped>
.unauthorized {
  min-height: 70vh; /* 让页面垂直居中更好看 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.unauthorized h1 {
  font-size: 6rem;
  margin-bottom: 0.5rem;
}

.unauthorized h2 {
  margin-bottom: 1.5rem;
}

.unauthorized .lead {
  max-width: 600px;
  margin: 0 auto 2rem;
}
</style>
