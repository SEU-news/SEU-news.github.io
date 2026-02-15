<!-- src/views/429.vue -->
<template>
  <div class="too-many-requests container mt-5 text-center">
    <h1 class="display-4">429</h1>
    <h2>Too Many Requests</h2>
    <p class="lead">
      You have sent too many requests in a given amount of time.
      Please wait a while before trying again.
    </p>
    <router-link to="/" class="btn btn-primary">Return to Home</router-link>
  </div>
</template>

<script setup>
// 这里不需要额外逻辑
</script>

<style scoped>
.too-many-requests {
  min-height: 70vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.too-many-requests h1 {
  font-size: 6rem;
  margin-bottom: 0.5rem;
}

.too-many-requests h2 {
  margin-bottom: 1.5rem;
}

.too-many-requests .lead {
  max-width: 600px;
  margin: 0 auto 2rem;
}
</style>