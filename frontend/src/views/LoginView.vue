<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-950 px-4">
    <div class="w-full max-w-md space-y-8 animate-fade-in">
      <!-- Logo -->
      <div class="text-center">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-infrared-900 border border-infrared-700 mb-4">
          <svg class="w-8 h-8 text-infrared-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-white">InfraSight</h1>
        <p class="mt-1 text-gray-400 text-sm">Sign in to your account</p>
      </div>

      <!-- Card -->
      <div class="card">
        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1.5">Email</label>
            <input
              v-model="form.email"
              type="email"
              autocomplete="email"
              required
              placeholder="you@example.com"
              class="input-field"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1.5">Password</label>
            <input
              v-model="form.password"
              type="password"
              autocomplete="current-password"
              required
              placeholder="••••••••"
              class="input-field"
            />
          </div>

          <div v-if="error" class="rounded-lg bg-red-900/40 border border-red-700 px-4 py-3 text-sm text-red-300">
            {{ error }}
          </div>

          <button type="submit" :disabled="loading" class="btn-primary w-full">
            <LoadingSpinner v-if="loading" class="w-4 h-4" />
            <span>{{ loading ? 'Signing in…' : 'Sign in' }}</span>
          </button>
        </form>
      </div>

      <p class="text-center text-sm text-gray-500">
        Don't have an account?
        <router-link to="/signup" class="text-infrared-400 hover:text-infrared-300 font-medium ml-1">
          Create one
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const auth = useAuthStore()
const router = useRouter()
const form = reactive({ email: '', password: '' })
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.email, form.password)
    router.push({ name: 'Dashboard' })
  } catch (err) {
    error.value = err.response?.data?.detail || 'Login failed. Please check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>
