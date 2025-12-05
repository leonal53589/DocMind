<template>
  <div class="space-y-6">
    <!-- Search Header -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex items-center gap-4">
        <div class="flex-1 relative">
          <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            v-model="searchQuery"
            @keyup.enter="performSearch"
            type="text"
            placeholder="搜索您的知识库..."
            class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <button
          @click="performSearch"
          class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          搜索
        </button>
      </div>

      <!-- Filters -->
      <div class="mt-4 flex items-center gap-4">
        <select
          v-model="filterCategory"
          class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">所有分类</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>

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

    <!-- Search Results -->
    <div v-if="hasSearched">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-medium text-gray-900">
          <span v-if="loading">搜索中...</span>
          <span v-else>找到 {{ total }} 个关于 "{{ lastQuery }}" 的结果</span>
        </h2>
      </div>

      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>

      <div v-else-if="items.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
        <MagnifyingGlassIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-lg font-medium text-gray-900">未找到结果</h3>
        <p class="mt-1 text-sm text-gray-500">
          请尝试其他关键词或调整筛选条件。
        </p>
      </div>

      <div v-else class="bg-white rounded-lg shadow divide-y divide-gray-200">
        <ItemCard
          v-for="item in items"
          :key="item.id"
          :item="item"
          :highlight="lastQuery"
          :all-items="allItems"
          @delete="handleDelete"
          @update="handleUpdate"
        />
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="mt-6 flex items-center justify-between">
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
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- Initial State -->
    <div v-else class="text-center py-12 bg-white rounded-lg shadow">
      <MagnifyingGlassIcon class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-lg font-medium text-gray-900">搜索您的知识库</h3>
      <p class="mt-1 text-sm text-gray-500">
        输入关键词搜索您的文件、网页和笔记。
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMainStore } from '../stores/main'
import * as api from '../api'
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline'
import ItemCard from '../components/ItemCard.vue'

const route = useRoute()
const store = useMainStore()

const searchQuery = ref('')
const lastQuery = ref('')
const loading = ref(false)
const hasSearched = ref(false)
const items = ref([])
const allItems = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const filterCategory = ref('')
const filterType = ref('')

const categories = computed(() => store.categories)
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

async function performSearch() {
  if (!searchQuery.value.trim()) return

  loading.value = true
  hasSearched.value = true
  lastQuery.value = searchQuery.value
  currentPage.value = 1

  try {
    const params = {
      q: searchQuery.value,
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (filterCategory.value) params.category_id = filterCategory.value
    if (filterType.value) params.content_type = filterType.value

    const data = await store.searchItems(searchQuery.value, params)
    items.value = data?.items || []
    total.value = data?.total || 0
  } finally {
    loading.value = false
  }
}

async function handleDelete(id) {
  if (confirm('确定要删除这个项目吗？')) {
    await store.deleteItem(id)
    items.value = items.value.filter(item => item.id !== id)
    total.value--
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
    performSearch()
  }
}

onMounted(async () => {
  await store.fetchCategories()

  // Fetch all items for association feature
  try {
    const allData = await api.getItems({ page: 1, page_size: 1000 })
    allItems.value = allData.data?.items || []
  } catch (error) {
    console.error('Failed to fetch all items:', error)
  }

  // Check for query param
  if (route.query.q) {
    searchQuery.value = route.query.q
    await performSearch()
  }
})
</script>
