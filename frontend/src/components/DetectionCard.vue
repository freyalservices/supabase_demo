<template>
  <router-link
    :to="{ name: 'DetectionDetail', params: { id: detection.id } }"
    class="card group hover:border-infrared-800 transition block animate-fade-in"
  >
    <!-- Thumbnail -->
    <div class="rounded-lg overflow-hidden bg-black mb-4 h-40 flex items-center justify-center border border-gray-800">
      <img
        v-if="detection.processed_image_url || detection.original_image_url"
        :src="detection.processed_image_url || detection.original_image_url"
        :alt="`Detection ${detection.id}`"
        class="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
      />
      <svg v-else class="w-10 h-10 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3 3h18M3 21h18" />
      </svg>
    </div>

    <!-- Info -->
    <div class="flex items-start justify-between gap-2">
      <div class="min-w-0">
        <div class="flex items-center gap-2 mb-1">
          <span :class="['badge text-xs', detection.algorithm === 'DW-LCM' ? 'bg-infrared-900 text-infrared-300' : 'bg-blue-900 text-blue-300']">
            {{ detection.algorithm }}
          </span>
          <span :class="['badge text-xs', statusClass]">{{ detection.status }}</span>
        </div>
        <p class="text-xs text-gray-500">{{ formatDate(detection.created_at) }}</p>
      </div>
      <div class="shrink-0 text-right">
        <p class="text-lg font-bold text-white">{{ detection.target_count ?? 0 }}</p>
        <p class="text-xs text-gray-500">targets</p>
      </div>
    </div>

    <!-- Delete button (on hover) -->
    <button
      v-if="$emit && onDelete"
      @click.prevent="$emit('delete', detection.id)"
      class="mt-3 text-xs text-red-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition"
    >
      Delete
    </button>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  detection: { type: Object, required: true },
})

defineEmits(['delete'])

const onDelete = true

const statusClass = computed(() => {
  if (props.detection.status === 'completed') return 'bg-green-900/60 text-green-400'
  if (props.detection.status === 'failed') return 'bg-red-900/60 text-red-400'
  return 'bg-yellow-900/60 text-yellow-400'
})

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>
