<script setup lang="ts">
interface Props {
  showLogo?: boolean
}

withDefaults(defineProps<Props>(), {
  showLogo: false
})
</script>

<template>
  <div class="gradient-background">
    <slot></slot>
  </div>
</template>

<style scoped>
.gradient-background {
  background: linear-gradient(to right, #00a99d, #ffffff 50%, #00a99d);
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  box-sizing: border-box;
}
</style>