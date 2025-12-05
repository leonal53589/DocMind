<template>
  <div class="space-y-6">
    <!-- Category Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">
          {{ currentCategory ? currentCategory.name : '所有项目' }}
        </h1>
        <p v-if="currentCategory?.description" class="text-sm text-gray-500 mt-1">
          {{ currentCategory.description }}
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

        <!-- Sort -->
        <select
          v-model="sortBy"
          class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="created_at">最新优先</option>
          <option value="title">标题 A-Z</option>
        </select>
      </div>
    </div>

    <!-- Items Grid -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p class="mt-2 text-gray-500">加载项目中...</p>
    </div>

    <div v-else-if="items.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
      <FolderOpenIcon class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-lg font-medium text-gray-900">未找到项目</h3>
      <p class="mt-1 text-sm text-gray-500">
        {{ currentCategory ? '该分类为空。' : '导入一些内容开始使用吧。' }}
      </p>
    </div>

    <div v-else class="bg-white rounded-lg shadow divide-y divide-gray-200">
      <ItemCard
        v-for="item in items"
        :key="item.id"
        :item="item"
        @delete="handleDelete"
        @reclassify="handleReclassify"
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
              ? 'bg-blue-600 text-white border-blue-600'
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
import { useRoute } from 'vue-router'
import { useMainStore } from '../stores/main'
import * as api from '../api'
import { FolderOpenIcon } from '@heroicons/vue/24/outline'
import ItemCard from '../components/ItemCard.vue'

const route = useRoute()
const store = useMainStore()

const loading = ref(true)
const items = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const filterType = ref('')
const sortBy = ref('created_at')

const categoryId = computed(() => route.params.categoryId)

const currentCategory = computed(() => {
  if (!categoryId.value) return null
  return store.categories.find(c => c.id === parseInt(categoryId.value))
})

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

async function fetchItems() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (categoryId.value) params.category_id = categoryId.value
    if (filterType.value) params.content_type = filterType.value

    const data = await store.fetchItems(params)
    items.value = data?.items || []
    total.value = data?.total || 0
  } finally {
    loading.value = false
  }
}

async function handleDelete(id) {
  if (confirm('确定要删除这个项目吗？')) {
    await store.deleteItem(id)
    await fetchItems()
  }
}

async function handleReclassify(id) {
  try {
    await store.reclassifyItem(id)
    await fetchItems()
  } catch (error) {
    alert('重新分类失败')
  }
}

async function handleUpdate(id) {
  // Refresh the updated item
  try {
    const response = await api.getItem(id)
    const index = items.value.findIndex(item => item.id === id)
    if (index !== -1) {
      items.value[index] = response.data
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

watch([categoryId, filterType, sortBy], () => {
  currentPage.value = 1
  fetchItems()
})

watch(currentPage, fetchItems)

onMounted(async () => {
  await store.fetchCategories()
  await fetchItems()
})
</script>
