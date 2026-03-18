<template>
  <div class="min-h-screen bg-gray-950 flex flex-col">
    <Navbar />
    <main class="flex-1">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import Navbar from '../components/Navbar.vue'

const auth = useAuthStore()
onMounted(() => auth.fetchUser())
</script>
