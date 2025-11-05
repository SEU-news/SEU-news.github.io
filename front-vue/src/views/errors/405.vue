<!-- src/views/405.vue -->
<template>
  <div class="method-not-allowed container mt-5 text-center">
    <h1 class="display-4">405</h1>
    <h2>Method Not Allowed</h2>
    <p class="lead">
      The request method is not supported for the requested resource.
      Please check your request method and try again.
    </p>
    <router-link to="/" class="btn btn-primary">Return to Home</router-link>
  </div>
</template>

<script setup>
// 这里不需要额外逻辑
</script>

<style scoped>
.method-not-allowed {
  min-height: 70vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.method-not-allowed h1 {
  font-size: 6rem;
  margin-bottom: 0.5rem;
}

.method-not-allowed h2 {
  margin-bottom: 1.5rem;
}

.method-not-allowed .lead {
  max-width: 600px;
  margin: 0 auto 2rem;
}
</style>