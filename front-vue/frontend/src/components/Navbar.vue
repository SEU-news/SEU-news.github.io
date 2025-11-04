<template>
  <nav class="navbar">
    <router-link to="/">首页</router-link>
    <router-link to="/news">至善新生</router-link>
    <router-link to="/about">关于</router-link>
  </nav>
</template>

<script setup lang="ts">
// Navbar component
</script>

<style scoped>
.navbar {
  padding: 1rem;
  background: #f5f5f5;
  margin-bottom: 2rem;
}

.navbar a {
  margin: 0 1rem;
  text-decoration: none;
  color: #2c3e50;
}

.navbar a.router-link-active {
  color: #42b983;
  font-weight: bold;
}
</style>