import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '../api'

export const useMainStore = defineStore('main', () => {
  // State
  const categories = ref([])
  const items = ref([])
  const stats = ref(null)
  const loading = ref(false)
  const searchQuery = ref('')
  const selectedCategory = ref(null)

  // Getters
  const categoriesWithItems = computed(() => {
    return categories.value.map(cat => ({
      ...cat,
      items: items.value.filter(item => item.category_id === cat.id)
    }))
  })

  // Actions
  async function fetchCategories() {
    try {
      const response = await api.getCategories()
      categories.value = response.data
    } catch (error) {
      console.error('Failed to fetch categories:', error)
    }
  }

  async function fetchItems(params = {}) {
    loading.value = true
    try {
      const response = await api.getItems(params)
      items.value = response.data.items
      return response.data
    } catch (error) {
      console.error('Failed to fetch items:', error)
    } finally {
      loading.value = false
    }
  }

  async function fetchStats() {
    try {
      const response = await api.getStats()
      stats.value = response.data
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  async function searchItems(query, params = {}) {
    loading.value = true
    try {
      const response = await api.searchItems({ q: query, ...params })
      return response.data
    } catch (error) {
      console.error('Failed to search items:', error)
    } finally {
      loading.value = false
    }
  }

  async function deleteItem(id) {
    try {
      await api.deleteItem(id)
      items.value = items.value.filter(item => item.id !== id)
      await fetchStats()
    } catch (error) {
      console.error('Failed to delete item:', error)
      throw error
    }
  }

  async function reclassifyItem(id) {
    try {
      const response = await api.reclassifyItem(id)
      const index = items.value.findIndex(item => item.id === id)
      if (index !== -1) {
        items.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('Failed to reclassify item:', error)
      throw error
    }
  }

  return {
    categories,
    items,
    stats,
    loading,
    searchQuery,
    selectedCategory,
    categoriesWithItems,
    fetchCategories,
    fetchItems,
    fetchStats,
    searchItems,
    deleteItem,
    reclassifyItem,
  }
})
