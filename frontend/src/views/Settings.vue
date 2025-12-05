<template>
  <div class="max-w-4xl space-y-6">
    <h1 class="text-2xl font-bold text-gray-900">设置</h1>

    <!-- Server Status -->
    <div class="bg-white rounded-lg shadow">
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-lg font-medium text-gray-900">服务器状态</h2>
      </div>
      <div class="p-6">
        <div class="flex items-center gap-3">
          <div :class="[
            'w-3 h-3 rounded-full',
            serverStatus === 'healthy' ? 'bg-green-500' : 'bg-red-500'
          ]"></div>
          <span class="text-sm text-gray-700">
            {{ serverStatus === 'healthy' ? '服务器运行正常' : '服务器无响应' }}
          </span>
        </div>
        <p v-if="serverVersion" class="mt-2 text-sm text-gray-500">
          版本：{{ serverVersion }}
        </p>
      </div>
    </div>

    <!-- Categories Management -->
    <div class="bg-white rounded-lg shadow">
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h2 class="text-lg font-medium text-gray-900">分类管理</h2>
        <button
          @click="showNewCategory = true"
          class="text-sm text-blue-600 hover:text-blue-700"
        >
          + 添加分类
        </button>
      </div>
      <div class="divide-y divide-gray-200">
        <div v-for="cat in categories" :key="cat.id" class="px-6 py-4 flex items-center justify-between">
          <div>
            <h3 class="text-sm font-medium text-gray-900">{{ cat.name }}</h3>
            <p v-if="cat.description" class="text-sm text-gray-500">{{ cat.description }}</p>
          </div>
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-500">{{ cat.item_count }} 项</span>
            <button
              @click="deleteCategory(cat.id)"
              class="text-sm text-red-600 hover:text-red-700"
            >
              删除
            </button>
          </div>
        </div>
        <div v-if="categories.length === 0" class="px-6 py-8 text-center text-gray-500">
          暂无分类
        </div>
      </div>
    </div>

    <!-- New Category Modal -->
    <div v-if="showNewCategory" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">新建分类</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">名称</label>
            <input
              v-model="newCategory.name"
              type="text"
              class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="分类名称"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">描述</label>
            <textarea
              v-model="newCategory.description"
              rows="3"
              class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="可选描述"
            ></textarea>
          </div>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button
            @click="showNewCategory = false"
            class="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
          >
            取消
          </button>
          <button
            @click="createCategory"
            class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            创建
          </button>
        </div>
      </div>
    </div>

    <!-- Storage Info -->
    <div class="bg-white rounded-lg shadow">
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-lg font-medium text-gray-900">存储信息</h2>
      </div>
      <div class="p-6">
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-700">项目总数</span>
            <span class="text-sm font-medium text-gray-900">{{ stats?.total_items || 0 }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-700">已用存储</span>
            <span class="text-sm font-medium text-gray-900">{{ formatSize(stats?.total_storage_bytes) }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-700">文件数</span>
            <span class="text-sm font-medium text-gray-900">{{ stats?.items_by_type?.file || 0 }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-700">网页数</span>
            <span class="text-sm font-medium text-gray-900">{{ stats?.items_by_type?.url || 0 }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-700">笔记数</span>
            <span class="text-sm font-medium text-gray-900">{{ stats?.items_by_type?.note || 0 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- About -->
    <div class="bg-white rounded-lg shadow">
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-lg font-medium text-gray-900">关于</h2>
      </div>
      <div class="p-6">
        <p class="text-sm text-gray-700">
          <strong>知识库</strong>是一个本地知识存储系统，用于管理和组织文件、笔记和网页内容。
        </p>
        <p class="mt-2 text-sm text-gray-500">
          版本 0.1.0
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMainStore } from '../stores/main'
import * as api from '../api'

const store = useMainStore()

const serverStatus = ref('checking')
const serverVersion = ref('')
const showNewCategory = ref(false)
const newCategory = ref({ name: '', description: '' })

const categories = computed(() => store.categories)
const stats = computed(() => store.stats)

function formatSize(bytes) {
  if (!bytes) return '0 B'
  if (bytes > 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`
  if (bytes > 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  if (bytes > 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${bytes} B`
}

async function checkHealth() {
  try {
    const response = await api.healthCheck()
    serverStatus.value = response.data.status
    serverVersion.value = response.data.version || ''
  } catch {
    serverStatus.value = 'error'
  }
}

async function createCategory() {
  if (!newCategory.value.name.trim()) return

  try {
    await api.createCategory(newCategory.value)
    await store.fetchCategories()
    showNewCategory.value = false
    newCategory.value = { name: '', description: '' }
  } catch (error) {
    alert('创建分类失败')
  }
}

async function deleteCategory(id) {
  const cat = categories.value.find(c => c.id === id)
  if (cat?.item_count > 0) {
    alert('无法删除包含项目的分类。请先移动或删除项目。')
    return
  }

  if (confirm('确定要删除这个分类吗？')) {
    try {
      await api.deleteCategory(id)
      await store.fetchCategories()
    } catch (error) {
      alert('删除分类失败')
    }
  }
}

onMounted(async () => {
  await Promise.all([
    checkHealth(),
    store.fetchCategories(),
    store.fetchStats(),
  ])
})
</script>
