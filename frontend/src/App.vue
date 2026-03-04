<script setup lang="ts">
import { ref, onMounted } from 'vue'

const healthStatus = ref<string>('Loading...')

onMounted(async () => {
  try {
    const response = await fetch('/api/health')
    const data = await response.json()
    healthStatus.value = data.status
  } catch (error) {
    healthStatus.value = 'Error fetching health status'
    console.error(error)
  }
})
</script>

<template>
  <div>
    <h1>World Cup Project</h1>
    <p>Backend Status: {{ healthStatus }}</p>
  </div>
</template>

<style scoped>
</style>
