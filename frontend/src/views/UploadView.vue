<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10 animate-fade-in">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-white">Upload Infrared Image</h1>
      <p class="mt-1 text-gray-400 text-sm">Select an algorithm and upload your infrared image for target detection.</p>
    </div>

    <div class="card space-y-6">
      <!-- Algorithm selector -->
      <div>
        <label class="block text-sm font-medium text-gray-300 mb-3">Detection Algorithm</label>
        <div class="grid grid-cols-2 gap-3">
          <button
            v-for="algo in algorithms"
            :key="algo.value"
            type="button"
            @click="selectedAlgorithm = algo.value"
            :class="[
              'rounded-lg border p-4 text-left transition',
              selectedAlgorithm === algo.value
                ? 'border-infrared-500 bg-infrared-950'
                : 'border-gray-700 bg-gray-800 hover:border-gray-600'
            ]"
          >
            <p class="font-semibold text-white">{{ algo.value }}</p>
            <p class="text-xs text-gray-400 mt-0.5">{{ algo.description }}</p>
          </button>
        </div>
      </div>

      <!-- Drop zone -->
      <ImageUpload @file-selected="onFileSelected" />

      <!-- Selected file preview -->
      <div v-if="selectedFile" class="rounded-lg border border-gray-700 bg-gray-800 p-4 flex items-center gap-3">
        <svg class="w-8 h-8 text-infrared-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3 3h18M3 21h18" />
        </svg>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-white truncate">{{ selectedFile.name }}</p>
          <p class="text-xs text-gray-400">{{ formatBytes(selectedFile.size) }}</p>
        </div>
        <button @click="selectedFile = null" class="text-gray-500 hover:text-gray-300">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Error / success -->
      <div v-if="error" class="rounded-lg bg-red-900/40 border border-red-700 px-4 py-3 text-sm text-red-300">
        {{ error }}
      </div>

      <!-- Submit -->
      <button
        @click="handleUpload"
        :disabled="!selectedFile || processing"
        class="btn-primary w-full"
      >
        <LoadingSpinner v-if="processing" class="w-4 h-4" />
        <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
        {{ processing ? 'Processing…' : 'Run Detection' }}
      </button>
    </div>

    <!-- Processing progress -->
    <div v-if="processing" class="mt-6 card text-center space-y-3">
      <LoadingSpinner class="w-10 h-10 text-infrared-400 mx-auto" />
      <p class="text-white font-medium">Running {{ selectedAlgorithm }}…</p>
      <p class="text-sm text-gray-400">This may take a few seconds depending on image size.</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDetectionStore } from '../stores/detection'
import ImageUpload from '../components/ImageUpload.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const store = useDetectionStore()
const router = useRouter()

const algorithms = [
  { value: 'DW-LCM', description: 'Fast local contrast, ideal for single-scale targets' },
  { value: 'MW-IPI', description: 'Robust multi-scale patch decomposition' },
]

const selectedAlgorithm = ref('DW-LCM')
const selectedFile = ref(null)
const processing = ref(false)
const error = ref('')

function onFileSelected(file) {
  selectedFile.value = file
  error.value = ''
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

async function handleUpload() {
  if (!selectedFile.value) return
  error.value = ''
  processing.value = true
  try {
    const result = await store.uploadImage(selectedFile.value, selectedAlgorithm.value)
    router.push({ name: 'DetectionDetail', params: { id: result.id } })
  } catch (err) {
    error.value = err.response?.data?.detail || store.error || 'Upload failed.'
  } finally {
    processing.value = false
  }
}
</script>
