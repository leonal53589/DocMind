<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">收藏夹</h1>
        <p class="text-sm text-gray-500 mt-1">
          您标记为收藏的项目，按收藏时间排序
        </p>
      </div>

      <div class="flex items-center gap-4">
        <!-- Filter by Type -->
        <select
          v-model="filterType"
          class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">所有类型</option>
          <option value="file">文件</option>
          <option value="url">网页</option>
          <option value="note">笔记</option>
        </select>
      </div>
    </div>

    <!-- Items Grid -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-500"></div>
      <p class="mt-2 text-gray-500">加载收藏中...</p>
    </div>

    <div v-else-if="items.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
      <StarIcon class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-lg font-medium text-gray-900">暂无收藏</h3>
      <p class="mt-1 text-sm text-gray-500">
        点击项目旁边的星号图标将其添加到收藏夹。
      </p>
    </div>

    <div v-else class="bg-white rounded-lg shadow divide-y divide-gray-200">
      <ItemCard
        v-for="item in items"
        :key="item.id"
        :item="item"
        :all-items="allItems"
        @delete="handleDelete"
        @update="handleUpdate"
      />
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-between">
      <p class="text-sm text-gray-700">
        显示第 {{ (currentPage - 1) * pageSize + 1 }} 到 {{ Math.min(currentPage * pageSize, total) }} 项，共 {{ total }} 项
      </p>
      <div class="flex gap-2">
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
        >
          上一页
        </button>
        <button
          v-for="page in displayPages"
          :key="page"
          @click="goToPage(page)"
          :class="[
            'px-3 py-1 border rounded text-sm',
            page === currentPage
              ? 'bg-yellow-500 text-white border-yellow-500'
              : 'border-gray-300 hover:bg-gray-50'
          ]"
        >
          {{ page }}
        </button>
        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useMainStore } from '../stores/main'
import * as api from '../api'
import { StarIcon } from '@heroicons/vue/24/outline'
import ItemCard from '../components/ItemCard.vue'

const store = useMainStore()

const loading = ref(true)
const items = ref([])
const allItems = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const filterType = ref('')

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const displayPages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

async function fetchFavorites() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      favorites_only: true,
    }
    if (filterType.value) params.content_type = filterType.value

    const response = await api.getFavorites(params)
    items.value = response.data?.items || []
    total.value = response.data?.total || 0
  } finally {
    loading.value = false
  }
}

async function fetchAllItems() {
  try {
    const response = await api.getItems({ page: 1, page_size: 1000 })
    allItems.value = response.data?.items || []
  } catch (error) {
    console.error('Failed to fetch all items:', error)
  }
}

async function handleDelete(id) {
  if (confirm('确定要删除这个项目吗？')) {
    await store.deleteItem(id)
    await fetchFavorites()
  }
}

async function handleUpdate(id) {
  try {
    const response = await api.getItem(id)
    const updatedItem = response.data

    // If item is no longer a favorite, remove it from the list
    if (!updatedItem.is_favorite) {
      items.value = items.value.filter(item => item.id !== id)
      total.value = Math.max(0, total.value - 1)
    } else {
      // Update the item in place
      const index = items.value.findIndex(item => item.id === id)
      if (index !== -1) {
        items.value[index] = updatedItem
      }
    }

    // Also update in allItems
    const allIndex = allItems.value.findIndex(item => item.id === id)
    if (allIndex !== -1) {
      allItems.value[allIndex] = updatedItem
    }
  } catch (error) {
    console.error('Failed to refresh item:', error)
  }
}

function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

watch([filterType], () => {
  currentPage.value = 1
  fetchFavorites()
})

watch(currentPage, fetchFavorites)

onMounted(async () => {
  await Promise.all([fetchFavorites(), fetchAllItems()])
})
</script>
