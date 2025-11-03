<template>
  <div id="app">
    <nav v-if="showNavbar" class="navbar">
      <router-link to="/">首页</router-link>
      <router-link to="/news">至善新生</router-link>
      <router-link to="/about">关于</router-link>
    </nav>
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import { errorRouteNames } from './router/errorRoutes'

const $route = useRoute()

// 只在非错误页面显示导航栏
const showNavbar = computed(() => {
  return !errorRouteNames.includes($route.name as string)
})
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