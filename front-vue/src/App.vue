<template>
  <div id="app">
    <nav v-if="$route.path !== '/'" class="navbar">
      <router-link to="/">首页</router-link>
      <router-link to="/news">新闻</router-link>
      <router-link to="/about">关于</router-link>
    </nav>
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const $route = useRoute()
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

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
