<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 animate-fade-in">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-white">Detection History</h1>
        <p class="mt-1 text-gray-400 text-sm">All your previous infrared image detections.</p>
      </div>
      <router-link to="/upload" class="btn-primary">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        New Detection
      </router-link>
    </div>

    <!-- Filter bar -->
    <div class="flex flex-wrap gap-3 mb-6">
      <button
        v-for="f in filters"
        :key="f.value"
        @click="activeFilter = f.value"
        :class="[
          'rounded-full px-4 py-1.5 text-sm font-medium transition',
          activeFilter === f.value
            ? 'bg-infrared-600 text-white'
            : 'bg-gray-800 text-gray-400 hover:bg-gray-700',
        ]"
      >
        {{ f.label }}
      </button>
    </div>

    <div v-if="store.loading" class="flex justify-center py-16">
      <LoadingSpinner class="w-8 h-8 text-infrared-400" />
    </div>

    <div v-else-if="!filtered.length" class="card text-center py-16">
      <svg class="w-12 h-12 text-gray-600 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3 3h18M3 21h18" />
      </svg>
      <p class="text-gray-400">No detections found for this filter.</p>
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
      <DetectionCard
        v-for="d in filtered"
        :key="d.id"
        :detection="d"
        @delete="confirmDelete(d.id)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useDetectionStore } from '../stores/detection'
import DetectionCard from '../components/DetectionCard.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const store = useDetectionStore()
const activeFilter = ref('all')

const filters = [
  { label: 'All', value: 'all' },
  { label: 'Completed', value: 'completed' },
  { label: 'DW-LCM', value: 'DW-LCM' },
  { label: 'MW-IPI', value: 'MW-IPI' },
]

const filtered = computed(() => {
  if (activeFilter.value === 'all') return store.detections
  if (activeFilter.value === 'completed') return store.detections.filter((d) => d.status === 'completed')
  return store.detections.filter((d) => d.algorithm === activeFilter.value)
})

async function confirmDelete(id) {
  if (confirm('Delete this detection?')) {
    await store.deleteDetection(id)
  }
}

onMounted(() => store.fetchDetections())
</script>
