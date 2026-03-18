<template>
  <div
    class="relative rounded-xl border-2 border-dashed transition-colors cursor-pointer"
    :class="isDragging ? 'border-infrared-500 bg-infrared-950/30' : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'"
    @dragenter.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @dragover.prevent
    @drop.prevent="onDrop"
    @click="triggerInput"
  >
    <input
      ref="fileInput"
      type="file"
      accept="image/jpeg,image/png,image/bmp,image/tiff,image/webp"
      class="sr-only"
      @change="onFileChange"
    />
    <div class="flex flex-col items-center justify-center gap-3 py-14 px-6 text-center pointer-events-none">
      <div class="w-14 h-14 rounded-full bg-gray-700 flex items-center justify-center">
        <svg class="w-7 h-7 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
            d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
        </svg>
      </div>
      <div>
        <p class="text-sm font-medium text-white">
          <span class="text-infrared-400">Click to upload</span> or drag &amp; drop
        </p>
        <p class="text-xs text-gray-500 mt-1">JPEG, PNG, BMP, TIFF, WebP</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['file-selected'])
const fileInput = ref(null)
const isDragging = ref(false)

function triggerInput() {
  fileInput.value?.click()
}

function onFileChange(e) {
  const file = e.target.files?.[0]
  if (file) emit('file-selected', file)
}

function onDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) emit('file-selected', file)
}
</script>
