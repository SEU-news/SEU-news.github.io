<!-- src/views/502.vue -->
<template>
  <div class="bad-gateway container mt-5 text-center">
    <h1 class="display-4">502</h1>
    <h2>Bad Gateway</h2>
    <p class="lead">
      The server received an invalid response from the upstream server.
      This issue is likely temporary, please try again later.
    </p>
    <router-link to="/" class="btn btn-primary">Return to Home</router-link>
  </div>
</template>

<script setup>
// 这里不需要额外逻辑
</script>

<style scoped>
.bad-gateway {
  min-height: 70vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.bad-gateway h1 {
  font-size: 6rem;
  margin-bottom: 0.5rem;
}

.bad-gateway h2 {
  margin-bottom: 1.5rem;
}

.bad-gateway .lead {
  max-width: 600px;
  margin: 0 auto 2rem;
}
</style>