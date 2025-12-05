<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="$emit('close')">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <h2 class="text-lg font-semibold text-gray-900">导入内容</h2>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
          <XMarkIcon class="w-6 h-6" />
        </button>
      </div>

      <!-- Tabs -->
      <div class="flex border-b border-gray-200">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'flex-1 px-4 py-3 text-sm font-medium text-center border-b-2 transition-colors',
            activeTab === tab.id
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          ]"
        >
          <component :is="tab.icon" class="w-5 h-5 mx-auto mb-1" />
          {{ tab.label }}
        </button>
      </div>

      <!-- Content -->
      <div class="p-6">
        <!-- File Upload -->
        <div v-if="activeTab === 'file'" class="space-y-4">
          <div
            @dragover.prevent="isDragging = true"
            @dragleave="isDragging = false"
            @drop.prevent="handleDrop"
            :class="[
              'border-2 border-dashed rounded-lg p-8 text-center transition-colors',
              isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
            ]"
          >
            <CloudArrowUpIcon class="w-12 h-12 mx-auto text-gray-400" />
            <p class="mt-2 text-sm text-gray-600">
              将文件拖放到此处，或
              <label class="text-blue-600 hover:text-blue-700 cursor-pointer">
                浏览文件
                <input type="file" multiple class="hidden" @change="handleFileSelect" />
              </label>
            </p>
            <p class="mt-1 text-xs text-gray-500">
              支持文档、图片、视频和代码文件
            </p>
          </div>

          <div v-if="selectedFiles.length > 0" class="space-y-2">
            <div
              v-for="(file, index) in selectedFiles"
              :key="index"
              class="flex items-center justify-between px-3 py-2 bg-gray-50 rounded-lg"
            >
              <div class="flex items-center gap-2 min-w-0">
                <DocumentIcon class="w-5 h-5 text-gray-400 flex-shrink-0" />
                <span class="text-sm text-gray-700 truncate">{{ file.name }}</span>
                <span class="text-xs text-gray-500">({{ formatSize(file.size) }})</span>
              </div>
              <button @click="removeFile(index)" class="text-gray-400 hover:text-red-600">
                <XMarkIcon class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        <!-- URL Import -->
        <div v-if="activeTab === 'url'" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">网址</label>
            <input
              v-model="urlInput"
              type="url"
              placeholder="https://example.com/article"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <p class="text-sm text-gray-500">
            页面内容将被提取并保存到您的知识库中。
          </p>
        </div>

        <!-- Note -->
        <div v-if="activeTab === 'note'" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">标题</label>
            <input
              v-model="noteTitle"
              type="text"
              placeholder="笔记标题"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">内容</label>
            <textarea
              v-model="noteContent"
              rows="6"
              placeholder="在这里写下您的笔记..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            ></textarea>
          </div>
        </div>

        <!-- Category Selection -->
        <div class="mt-4 pt-4 border-t border-gray-200">
          <label class="block text-sm font-medium text-gray-700 mb-1">分类（可选）</label>
          <select
            v-model="selectedCategory"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">自动分类</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mt-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
          {{ error }}
        </div>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-xl">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg"
        >
          取消
        </button>
        <button
          @click="handleImport"
          :disabled="!canImport || importing"
          :class="[
            'px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors',
            canImport && !importing
              ? 'bg-blue-600 hover:bg-blue-700'
              : 'bg-gray-400 cursor-not-allowed'
          ]"
        >
          <span v-if="importing">导入中...</span>
          <span v-else>导入</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMainStore } from '../stores/main'
import * as api from '../api'
import {
  XMarkIcon,
  DocumentIcon,
  CloudArrowUpIcon,
  DocumentTextIcon,
  LinkIcon,
  PencilSquareIcon,
} from '@heroicons/vue/24/outline'

const emit = defineEmits(['close'])

const store = useMainStore()

const tabs = [
  { id: 'file', label: '文件', icon: DocumentTextIcon },
  { id: 'url', label: '网址', icon: LinkIcon },
  { id: 'note', label: '笔记', icon: PencilSquareIcon },
]

const activeTab = ref('file')
const isDragging = ref(false)
const selectedFiles = ref([])
const urlInput = ref('')
const noteTitle = ref('')
const noteContent = ref('')
const selectedCategory = ref('')
const importing = ref(false)
const error = ref('')

const categories = computed(() => store.categories)

const canImport = computed(() => {
  if (activeTab.value === 'file') return selectedFiles.value.length > 0
  if (activeTab.value === 'url') return urlInput.value.trim() !== ''
  if (activeTab.value === 'note') return noteTitle.value.trim() !== '' && noteContent.value.trim() !== ''
  return false
})

function formatSize(bytes) {
  if (bytes > 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  if (bytes > 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${bytes} B`
}

function handleFileSelect(event) {
  const files = Array.from(event.target.files)
  selectedFiles.value = [...selectedFiles.value, ...files]
}

function handleDrop(event) {
  isDragging.value = false
  const files = Array.from(event.dataTransfer.files)
  selectedFiles.value = [...selectedFiles.value, ...files]
}

function removeFile(index) {
  selectedFiles.value.splice(index, 1)
}

async function handleImport() {
  error.value = ''
  importing.value = true

  try {
    if (activeTab.value === 'file') {
      for (const file of selectedFiles.value) {
        const formData = new FormData()
        formData.append('file', file)
        if (selectedCategory.value) {
          formData.append('category_id', selectedCategory.value)
        }
        await api.importFile(formData)
      }
    } else if (activeTab.value === 'url') {
      await api.importUrl(urlInput.value, selectedCategory.value || null)
    } else if (activeTab.value === 'note') {
      await api.createItem({
        title: noteTitle.value,
        content: noteContent.value,
        content_type: 'note',
        category_id: selectedCategory.value || null,
      })
    }

    // Refresh data
    await store.fetchStats()
    await store.fetchItems()
    emit('close')
  } catch (err) {
    error.value = err.response?.data?.detail || '导入失败，请重试。'
  } finally {
    importing.value = false
  }
}

onMounted(async () => {
  await store.fetchCategories()
})
</script>
