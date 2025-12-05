<template>
  <div class="space-y-6">
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-blue-100 text-blue-600">
            <DocumentIcon class="w-6 h-6" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">项目总数</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stats?.total_items || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-green-100 text-green-600">
            <FolderIcon class="w-6 h-6" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">分类数量</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stats?.total_categories || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-purple-100 text-purple-600">
            <TagIcon class="w-6 h-6" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">标签数量</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stats?.total_tags || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-3 rounded-full bg-orange-100 text-orange-600">
            <CircleStackIcon class="w-6 h-6" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">存储空间</p>
            <p class="text-2xl font-semibold text-gray-900">{{ formatSize(stats?.total_storage_bytes) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Content Type Breakdown -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">文件</h3>
          <DocumentTextIcon class="w-5 h-5 text-gray-400" />
        </div>
        <p class="mt-2 text-3xl font-bold text-blue-600">{{ stats?.items_by_type?.file || 0 }}</p>
        <p class="text-sm text-gray-500">已导入的文件</p>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">网页</h3>
          <LinkIcon class="w-5 h-5 text-gray-400" />
        </div>
        <p class="mt-2 text-3xl font-bold text-green-600">{{ stats?.items_by_type?.url || 0 }}</p>
        <p class="text-sm text-gray-500">已保存的网页</p>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">笔记</h3>
          <PencilSquareIcon class="w-5 h-5 text-gray-400" />
        </div>
        <p class="mt-2 text-3xl font-bold text-purple-600">{{ stats?.items_by_type?.note || 0 }}</p>
        <p class="text-sm text-gray-500">已创建的笔记</p>
      </div>
    </div>

    <!-- Recent Items -->
    <div class="bg-white rounded-lg shadow">
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-lg font-medium text-gray-900">最近项目</h2>
      </div>
      <div class="divide-y divide-gray-200">
        <div v-if="loading" class="p-6 text-center text-gray-500">
          加载中...
        </div>
        <div v-else-if="recentItems.length === 0" class="p-6 text-center text-gray-500">
          暂无项目。导入一些内容开始使用吧。
        </div>
        <ItemCard
          v-else
          v-for="item in recentItems"
          :key="item.id"
          :item="item"
          @delete="handleDelete"
          @update="handleUpdate"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useMainStore } from '../stores/main'
import * as api from '../api'
import {
  DocumentIcon,
  FolderIcon,
  TagIcon,
  CircleStackIcon,
  DocumentTextIcon,
  LinkIcon,
  PencilSquareIcon,
} from '@heroicons/vue/24/outline'
import ItemCard from '../components/ItemCard.vue'

const store = useMainStore()

const loading = ref(true)
const recentItems = ref([])

const stats = computed(() => store.stats)

function formatSize(bytes) {
  if (!bytes) return '0 B'
  if (bytes > 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`
  if (bytes > 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  if (bytes > 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${bytes} B`
}

async function handleDelete(id) {
  if (confirm('确定要删除这个项目吗？')) {
    await store.deleteItem(id)
    recentItems.value = recentItems.value.filter(item => item.id !== id)
  }
}

async function handleUpdate(id) {
  // Refresh the updated item
  try {
    const response = await api.getItem(id)
    const index = recentItems.value.findIndex(item => item.id === id)
    if (index !== -1) {
      recentItems.value[index] = response.data
    }
  } catch (error) {
    console.error('Failed to refresh item:', error)
  }
}

onMounted(async () => {
  try {
    await store.fetchStats()
    const data = await store.fetchItems({ page_size: 10 })
    recentItems.value = data?.items || []
  } finally {
    loading.value = false
  }
})
</script>
