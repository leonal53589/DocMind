<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="$emit('close')">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gray-50">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-indigo-500 rounded-xl flex items-center justify-center">
            <PlusIcon class="w-5 h-5 text-white" />
          </div>
          <h2 class="text-lg font-bold text-gray-900">导入内容</h2>
        </div>
        <button @click="$emit('close')" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>

      <!-- Tabs -->
      <div class="flex border-b border-gray-100 bg-gray-50/50">
        <button
          v-for="(tab, index) in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="tab-button group"
          :class="{ 'tab-active': activeTab === tab.id }"
          :style="{ transitionDelay: `${index * 50}ms` }"
        >
          <div class="tab-icon" :class="activeTab === tab.id ? 'tab-icon-active' : 'tab-icon-inactive'">
            <component :is="tab.icon" class="w-5 h-5" />
          </div>
          <span class="tab-label">{{ tab.label }}</span>
          <div v-if="activeTab === tab.id" class="tab-indicator"></div>
        </button>
      </div>

      <!-- Content -->
      <div class="p-6">
        <Transition name="tab-slide" mode="out-in">
          <!-- File Upload -->
          <div v-if="activeTab === 'file'" key="file" class="space-y-4">
            <div
              @dragover.prevent="isDragging = true"
              @dragleave="isDragging = false"
              @drop.prevent="handleDrop"
              class="upload-zone"
              :class="{ 'upload-zone-active': isDragging }"
            >
              <div class="upload-icon" :class="{ 'animate-bounce': isDragging }">
                <CloudArrowUpIcon class="w-8 h-8" />
              </div>
              <p class="mt-3 text-sm text-gray-600">
                将文件拖放到此处，或
                <label class="text-indigo-600 hover:text-indigo-700 cursor-pointer font-medium underline-offset-2 hover:underline">
                  浏览文件
                  <input type="file" multiple class="hidden" @change="handleFileSelect" />
                </label>
              </p>
              <p class="mt-1 text-xs text-gray-400">
                支持文档、图片、视频和代码文件
              </p>
            </div>

            <TransitionGroup name="file-list" tag="div" class="space-y-2">
              <div
                v-for="(file, index) in selectedFiles"
                :key="file.name + index"
                class="file-item"
              >
                <div class="flex items-center gap-3 min-w-0">
                  <div class="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <DocumentIcon class="w-5 h-5 text-indigo-600" />
                  </div>
                  <div class="min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">{{ file.name }}</p>
                    <p class="text-xs text-gray-500">{{ formatSize(file.size) }}</p>
                  </div>
                </div>
                <button @click="removeFile(index)" class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all duration-200">
                  <XMarkIcon class="w-4 h-4" />
                </button>
              </div>
            </TransitionGroup>
          </div>

          <!-- URL Import -->
          <div v-else-if="activeTab === 'url'" key="url" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">网址</label>
              <div class="relative">
                <div class="absolute left-3 top-1/2 -translate-y-1/2">
                  <GlobeAltIcon class="w-5 h-5 text-gray-400" />
                </div>
                <input
                  v-model="urlInput"
                  type="url"
                  placeholder="https://example.com/article"
                  class="input-field pl-10"
                />
              </div>
            </div>
            <div class="flex items-start gap-3 p-3 bg-blue-50 rounded-xl">
              <InformationCircleIcon class="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
              <p class="text-sm text-blue-700">
                页面内容将被提取并保存到您的知识库中。
              </p>
            </div>
          </div>

          <!-- Note -->
          <div v-else-if="activeTab === 'note'" key="note" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">标题</label>
              <input
                v-model="noteTitle"
                type="text"
                placeholder="笔记标题"
                class="input-field"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">内容</label>
              <textarea
                v-model="noteContent"
                rows="5"
                placeholder="在这里写下您的笔记..."
                class="input-field resize-none"
              ></textarea>
            </div>
          </div>
        </Transition>

        <!-- Category Selection -->
        <div class="mt-6 pt-4 border-t border-gray-100">
          <label class="block text-sm font-medium text-gray-700 mb-2">分类（可选）</label>
          <select
            v-model="selectedCategory"
            class="input-field"
          >
            <option value="">自动分类</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>

        <!-- Error Message -->
        <Transition name="slide-up">
          <div v-if="error" class="mt-4 p-4 bg-red-50 border border-red-100 text-red-700 rounded-xl text-sm flex items-start gap-3">
            <ExclamationCircleIcon class="w-5 h-5 flex-shrink-0" />
            <span>{{ error }}</span>
          </div>
        </Transition>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/80">
        <button
          @click="$emit('close')"
          class="btn-secondary"
        >
          取消
        </button>
        <button
          @click="handleImport"
          :disabled="!canImport || importing"
          class="btn-primary"
          :class="{ 'opacity-50 cursor-not-allowed': !canImport || importing }"
        >
          <span v-if="importing" class="flex items-center gap-2">
            <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            导入中...
          </span>
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
  PlusIcon,
  GlobeAltIcon,
  InformationCircleIcon,
  ExclamationCircleIcon,
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

<style scoped>
/* Tab Styles */
.tab-button {
  @apply relative flex-1 flex flex-col items-center gap-1.5 px-4 py-3 text-sm font-medium transition-colors;
}

.tab-button:hover .tab-icon-inactive {
  @apply bg-indigo-100 text-indigo-600;
}

.tab-icon {
  @apply w-9 h-9 rounded-xl flex items-center justify-center;
}

.tab-icon-active {
  @apply bg-indigo-500 text-white;
}

.tab-icon-inactive {
  @apply bg-gray-100 text-gray-500;
}

.tab-label {
  @apply text-gray-600;
}

.tab-active .tab-label {
  @apply text-indigo-600 font-semibold;
}

.tab-indicator {
  @apply absolute bottom-0 left-1/2 -translate-x-1/2 w-12 h-0.5 bg-indigo-500 rounded-full;
}

/* Upload Zone */
.upload-zone {
  @apply border-2 border-dashed rounded-xl p-8 text-center border-gray-200 bg-gray-50;
}

.upload-zone-active {
  @apply border-indigo-500 bg-indigo-50;
}

.upload-icon {
  @apply w-16 h-16 mx-auto bg-indigo-100 text-indigo-500 rounded-2xl flex items-center justify-center;
}

.upload-zone-active .upload-icon {
  @apply bg-indigo-500 text-white;
}

/* File Item */
.file-item {
  @apply flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-xl;
}

/* Input Field */
.input-field {
  @apply w-full px-4 py-2.5 border border-gray-200 rounded-xl bg-white
         focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 text-sm;
}

/* Button Styles */
.btn-primary {
  @apply bg-indigo-600 text-white px-5 py-2.5 rounded-xl hover:bg-indigo-700
         flex items-center justify-center gap-2 font-medium;
}

.btn-secondary {
  @apply bg-white text-gray-700 px-5 py-2.5 rounded-xl
         border border-gray-200 hover:bg-gray-50 font-medium;
}

/* Simple Transitions */
.tab-slide-enter-active,
.tab-slide-leave-active {
  transition: opacity 0.15s ease;
}

.tab-slide-enter-from,
.tab-slide-leave-to {
  opacity: 0;
}

.file-list-enter-active,
.file-list-leave-active {
  transition: opacity 0.15s ease;
}

.file-list-enter-from,
.file-list-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: opacity 0.15s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
}
</style>
