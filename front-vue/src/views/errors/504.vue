<!-- src/views/504.vue -->
<template>
  <div class="gateway-timeout container mt-5 text-center">
    <h1 class="display-4">504</h1>
    <h2>Gateway Timeout</h2>
    <p class="lead">
      The server, acting as a gateway, did not receive a timely response from the upstream server.
      This issue is likely temporary, please try again later.
    </p>
    <router-link to="/" class="btn btn-primary">Return to Home</router-link>
  </div>
</template>

<script setup>
// 这里不需要额外逻辑
</script>

<style scoped>
.gateway-timeout {
  min-height: 70vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.gateway-timeout h1 {
  font-size: 6rem;
  margin-bottom: 0.5rem;
}

.gateway-timeout h2 {
  margin-bottom: 1.5rem;
}

.gateway-timeout .lead {
  max-width: 600px;
  margin: 0 auto 2rem;
}
</style>