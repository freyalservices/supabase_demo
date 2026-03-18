<template>
  <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 animate-fade-in">
    <div class="flex items-center gap-3 mb-8">
      <router-link to="/history" class="text-gray-400 hover:text-white transition">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
        </svg>
      </router-link>
      <h1 class="text-2xl font-bold text-white">Detection Result</h1>
    </div>

    <div v-if="store.loading" class="flex justify-center py-16">
      <LoadingSpinner class="w-8 h-8 text-infrared-400" />
    </div>

    <div v-else-if="!detection" class="card text-center py-12">
      <p class="text-gray-400">Detection not found.</p>
    </div>

    <template v-else>
      <!-- Meta info -->
      <div class="card mb-6 flex flex-wrap gap-6">
        <div>
          <p class="text-xs text-gray-500 uppercase tracking-wide">Algorithm</p>
          <span :class="['badge mt-1', detection.algorithm === 'DW-LCM' ? 'bg-infrared-900 text-infrared-300' : 'bg-blue-900 text-blue-300']">
            {{ detection.algorithm }}
          </span>
        </div>
        <div>
          <p class="text-xs text-gray-500 uppercase tracking-wide">Status</p>
          <span :class="['badge mt-1', statusClass]">{{ detection.status }}</span>
        </div>
        <div>
          <p class="text-xs text-gray-500 uppercase tracking-wide">Targets Found</p>
          <p class="text-xl font-bold text-white">{{ targets.length }}</p>
        </div>
        <div>
          <p class="text-xs text-gray-500 uppercase tracking-wide">Date</p>
          <p class="text-sm text-gray-300 mt-1">{{ formatDate(detection.created_at) }}</p>
        </div>
      </div>

      <!-- Image comparison -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div class="card space-y-3">
          <p class="text-sm font-medium text-gray-400">Original Image</p>
          <img
            :src="detection.original_image_url"
            alt="Original infrared image"
            class="w-full rounded-lg border border-gray-700 object-contain bg-black"
            style="max-height: 400px"
          />
        </div>
        <div class="card space-y-3">
          <p class="text-sm font-medium text-gray-400">Processed Image <span class="text-infrared-400">(targets highlighted)</span></p>
          <img
            :src="detection.processed_image_url"
            alt="Processed image with targets"
            class="w-full rounded-lg border border-gray-700 object-contain bg-black"
            style="max-height: 400px"
          />
        </div>
      </div>

      <!-- Target list -->
      <div class="card">
        <h2 class="font-semibold text-white mb-4">Detected Targets ({{ targets.length }})</h2>
        <div v-if="!targets.length" class="text-gray-500 text-sm">
          No targets were detected in this image with the selected algorithm.
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-800 text-left">
                <th class="pb-2 pr-4 text-gray-500 font-medium">#</th>
                <th class="pb-2 pr-4 text-gray-500 font-medium">Position (x, y)</th>
                <th class="pb-2 pr-4 text-gray-500 font-medium">Size</th>
                <th class="pb-2 pr-4 text-gray-500 font-medium">Area (px²)</th>
                <th class="pb-2 text-gray-500 font-medium">Confidence</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(t, i) in targets" :key="i" class="border-b border-gray-800/50">
                <td class="py-2 pr-4 text-gray-400">{{ i + 1 }}</td>
                <td class="py-2 pr-4 text-white font-mono">({{ t.x }}, {{ t.y }})</td>
                <td class="py-2 pr-4 text-gray-300">{{ t.width }}×{{ t.height }}</td>
                <td class="py-2 pr-4 text-gray-300">{{ t.area }}</td>
                <td class="py-2">
                  <div class="flex items-center gap-2">
                    <div class="w-20 h-1.5 rounded-full bg-gray-700">
                      <div class="h-full rounded-full bg-infrared-500" :style="{ width: Math.min(t.confidence * 100, 100) + '%' }" />
                    </div>
                    <span class="text-gray-300 text-xs">{{ (t.confidence * 100).toFixed(1) }}%</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useDetectionStore } from '../stores/detection'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const route = useRoute()
const store = useDetectionStore()

const detection = computed(() => store.current)
const targets = computed(() => detection.value?.targets || [])

const statusClass = computed(() => {
  const s = detection.value?.status
  if (s === 'completed') return 'bg-green-900 text-green-300'
  if (s === 'failed') return 'bg-red-900 text-red-300'
  return 'bg-yellow-900 text-yellow-300'
})

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString()
}

onMounted(() => store.fetchDetection(route.params.id))
</script>
