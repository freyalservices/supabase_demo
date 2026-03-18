<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-950 px-4">
    <div class="w-full max-w-md space-y-8 animate-fade-in">
      <div class="text-center">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-infrared-900 border border-infrared-700 mb-4">
          <svg class="w-8 h-8 text-infrared-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-white">InfraSight</h1>
        <p class="mt-1 text-gray-400 text-sm">Create your account</p>
      </div>

      <div class="card">
        <form @submit.prevent="handleSignup" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1.5">Email</label>
            <input v-model="form.email" type="email" required placeholder="you@example.com" class="input-field" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1.5">Password</label>
            <input v-model="form.password" type="password" required placeholder="Min. 8 characters" minlength="8" class="input-field" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1.5">Confirm Password</label>
            <input v-model="form.confirm" type="password" required placeholder="Repeat password" class="input-field" />
          </div>

          <div v-if="error" class="rounded-lg bg-red-900/40 border border-red-700 px-4 py-3 text-sm text-red-300">
            {{ error }}
          </div>
          <div v-if="success" class="rounded-lg bg-green-900/40 border border-green-700 px-4 py-3 text-sm text-green-300">
            {{ success }}
          </div>

          <button type="submit" :disabled="loading" class="btn-primary w-full">
            <LoadingSpinner v-if="loading" class="w-4 h-4" />
            <span>{{ loading ? 'Creating account…' : 'Create account' }}</span>
          </button>
        </form>
      </div>

      <p class="text-center text-sm text-gray-500">
        Already have an account?
        <router-link to="/login" class="text-infrared-400 hover:text-infrared-300 font-medium ml-1">
          Sign in
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const auth = useAuthStore()
const form = reactive({ email: '', password: '', confirm: '' })
const loading = ref(false)
const error = ref('')
const success = ref('')

async function handleSignup() {
  error.value = ''
  success.value = ''
  if (form.password !== form.confirm) {
    error.value = 'Passwords do not match.'
    return
  }
  loading.value = true
  try {
    await auth.signup(form.email, form.password)
    success.value = 'Account created! Please check your email to confirm, then sign in.'
    Object.assign(form, { email: '', password: '', confirm: '' })
  } catch (err) {
    error.value = err.response?.data?.detail || 'Signup failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
