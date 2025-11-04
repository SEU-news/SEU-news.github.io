<!-- src/views/413.vue -->
<template>
  <div class="payload-too-large container mt-5 text-center">
    <h1 class="display-4">413</h1>
    <h2>Payload Too Large</h2>
    <p class="lead">
      The request is larger than the server is willing or able to process.
      Please reduce the size of your request and try again.
    </p>
    <router-link to="/" class="btn btn-primary">Return to Home</router-link>
  </div>
</template>

<script setup>
// 这里不需要额外逻辑
</script>

<style scoped>
.payload-too-large {
  min-height: 70vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.payload-too-large h1 {
  font-size: 6rem;
  margin-bottom: 0.5rem;
}

.payload-too-large h2 {
  margin-bottom: 1.5rem;
}

.payload-too-large .lead {
  max-width: 600px;
  margin: 0 auto 2rem;
}
</style>