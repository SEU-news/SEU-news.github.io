<!-- src/views/503.vue -->
<template>
  <div class="service-unavailable container mt-5 text-center">
    <h1 class="display-4">503</h1>
    <h2>Service Unavailable</h2>
    <p class="lead">
      The server is temporarily unable to service your request due to maintenance or overload.
      Please try again later.
    </p>
    <router-link to="/" class="btn btn-primary">Return to Home</router-link>
  </div>
</template>

<script setup>
// 这里不需要额外逻辑
</script>

<style scoped>
.service-unavailable {
  min-height: 70vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.service-unavailable h1 {
  font-size: 6rem;
  margin-bottom: 0.5rem;
}

.service-unavailable h2 {
  margin-bottom: 1.5rem;
}

.service-unavailable .lead {
  max-width: 600px;
  margin: 0 auto 2rem;
}
</style>