<template>
  <nav class="sticky top-0 z-40 border-b border-gray-800 bg-gray-950/90 backdrop-blur">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-6">
      <!-- Logo -->
      <router-link to="/" class="flex items-center gap-2.5 shrink-0">
        <div class="w-8 h-8 rounded-lg bg-infrared-900 border border-infrared-700 flex items-center justify-center">
          <svg class="w-4 h-4 text-infrared-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
          </svg>
        </div>
        <span class="text-white font-bold text-lg tracking-tight">InfraSight</span>
      </router-link>

      <!-- Nav links -->
      <div class="hidden sm:flex items-center gap-1">
        <router-link
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="px-3 py-1.5 rounded-lg text-sm font-medium transition"
          :class="$route.path === link.to || $route.path.startsWith(link.to + '/') && link.to !== '/'
            ? 'bg-infrared-900 text-infrared-300'
            : 'text-gray-400 hover:text-white hover:bg-gray-800'"
        >
          {{ link.label }}
        </router-link>
      </div>

      <!-- User menu -->
      <div class="flex items-center gap-3">
        <span class="hidden sm:block text-xs text-gray-500 truncate max-w-[140px]">{{ auth.user?.email }}</span>
        <button @click="handleLogout" class="btn-secondary text-xs px-3 py-1.5">
          Sign out
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const navLinks = [
  { to: '/', label: 'Dashboard' },
  { to: '/upload', label: 'Upload' },
  { to: '/history', label: 'History' },
]

async function handleLogout() {
  await auth.logout()
  router.push({ name: 'Login' })
}
</script>
