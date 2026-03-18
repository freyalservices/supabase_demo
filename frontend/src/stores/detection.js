import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useDetectionStore = defineStore('detection', () => {
  const detections = ref([])
  const current = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function fetchDetections() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get('/images/')
      detections.value = data.detections
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load detections'
    } finally {
      loading.value = false
    }
  }

  async function fetchDetection(id) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get(`/images/${id}`)
      current.value = data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load detection'
    } finally {
      loading.value = false
    }
  }

  async function uploadImage(file, algorithm) {
    loading.value = true
    error.value = null
    try {
      const form = new FormData()
      form.append('file', file)
      form.append('algorithm', algorithm)
      const { data } = await api.post('/images/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      detections.value.unshift(data)
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Upload failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteDetection(id) {
    await api.delete(`/images/${id}`)
    detections.value = detections.value.filter((d) => d.id !== id)
  }

  return { detections, current, loading, error, fetchDetections, fetchDetection, uploadImage, deleteDetection }
})
