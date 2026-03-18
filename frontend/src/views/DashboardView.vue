<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10 animate-fade-in">
    <!-- Hero -->
    <div class="rounded-2xl bg-gradient-to-br from-infrared-950 via-gray-900 to-gray-950 border border-infrared-900 p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
      <div>
        <h1 class="text-3xl font-bold text-white">Welcome back<span v-if="user?.email">, <span class="text-infrared-400">{{ user.email }}</span></span></h1>
        <p class="mt-2 text-gray-400">Detect small targets in infrared imagery using DW-LCM &amp; MW-IPI.</p>
      </div>
      <router-link to="/upload" class="btn-primary shrink-0">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
        Upload Image
      </router-link>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-5">
      <div class="card flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-infrared-900 flex items-center justify-center shrink-0">
          <svg class="w-6 h-6 text-infrared-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V9l-6-6z" />
          </svg>
        </div>
        <div>
          <p class="text-2xl font-bold text-white">{{ totalDetections }}</p>
          <p class="text-sm text-gray-400">Total Detections</p>
        </div>
      </div>
      <div class="card flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-green-900 flex items-center justify-center shrink-0">
          <svg class="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="text-2xl font-bold text-white">{{ completedDetections }}</p>
          <p class="text-sm text-gray-400">Completed</p>
        </div>
      </div>
      <div class="card flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-yellow-900 flex items-center justify-center shrink-0">
          <svg class="w-6 h-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
        </div>
        <div>
          <p class="text-2xl font-bold text-white">{{ totalTargets }}</p>
          <p class="text-sm text-gray-400">Targets Found</p>
        </div>
      </div>
    </div>

    <!-- Recent detections -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-white">Recent Detections</h2>
        <router-link to="/history" class="text-sm text-infrared-400 hover:text-infrared-300">View all →</router-link>
      </div>

      <div v-if="store.loading" class="flex justify-center py-12">
        <LoadingSpinner class="w-8 h-8 text-infrared-400" />
      </div>

      <div v-else-if="!recentDetections.length" class="card text-center py-12">
        <svg class="w-12 h-12 text-gray-600 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3 3h18M3 21h18" />
        </svg>
        <p class="text-gray-400">No detections yet. Upload your first image to get started!</p>
        <router-link to="/upload" class="btn-primary mt-4 inline-flex">Upload Now</router-link>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <DetectionCard
          v-for="d in recentDetections"
          :key="d.id"
          :detection="d"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useDetectionStore } from '../stores/detection'
import DetectionCard from '../components/DetectionCard.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const auth = useAuthStore()
const store = useDetectionStore()
const user = computed(() => auth.user)

const totalDetections = computed(() => store.detections.length)
const completedDetections = computed(() => store.detections.filter((d) => d.status === 'completed').length)
const totalTargets = computed(() => store.detections.reduce((sum, d) => sum + (d.target_count || 0), 0))
const recentDetections = computed(() => store.detections.slice(0, 6))

onMounted(() => store.fetchDetections())
</script>
