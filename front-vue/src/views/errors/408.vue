<!-- src/views/408.vue -->
<template>
  <div class="request-timeout container mt-5 text-center">
    <h1 class="display-4">408</h1>
    <h2>Request Timeout</h2>
    <p class="lead">
      The server timed out waiting for the request.
      Please check your network connection and try again.
    </p>
    <router-link to="/" class="btn btn-primary">Return to Home</router-link>
  </div>
</template>

<script setup>
// 这里不需要额外逻辑
</script>

<style scoped>
.request-timeout {
  min-height: 70vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.request-timeout h1 {
  font-size: 6rem;
  margin-bottom: 0.5rem;
}

.request-timeout h2 {
  margin-bottom: 1.5rem;
}

.request-timeout .lead {
  max-width: 600px;
  margin: 0 auto 2rem;
}
</style>