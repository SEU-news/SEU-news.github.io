<template>
  <div id="app">
    <Navbar v-if="showNavbar" />
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import { errorRouteNames } from './router/errorRoutes'
import Navbar from './components/Navbar.vue'

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
</style>