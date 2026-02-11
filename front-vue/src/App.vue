<template>
  <div id="app">
    <ToastContainer />
    <Navbar v-if="showNavbar" />
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import { errorRouteNames } from './router'
import Navbar from './components/Navbar.vue'

const $route = useRoute()

// 只在非错误页面且非管理后台页面显示导航栏
const showNavbar = computed(() => {
  const isErrorPage = errorRouteNames.includes($route.name as string)
  const isAdminPage = $route.path.startsWith('/manage/admin')
  return !isErrorPage && !isAdminPage
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