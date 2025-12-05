<template>
  <div class="px-6 py-4 hover:bg-gray-50 transition-colors">
    <div class="flex items-start gap-4">
      <!-- Thumbnail or Icon - Clickable -->
      <a
        :href="getItemLink()"
        :target="item.content_type === 'note' ? '_self' : '_blank'"
        class="flex-shrink-0 cursor-pointer"
        @click="handleItemClick($event)"
      >
        <img
          v-if="item.thumbnail_path"
          :src="`/thumbnails/${item.thumbnail_path}`"
          :alt="item.title"
          class="w-16 h-16 object-cover rounded-lg hover:opacity-80 transition-opacity"
        />
        <div
          v-else
          :class="[
            'w-16 h-16 rounded-lg flex items-center justify-center hover:opacity-80 transition-opacity',
            typeColors[item.content_type] || 'bg-gray-100'
          ]"
        >
          <component :is="typeIcons[item.content_type]" class="w-8 h-8 text-white" />
        </div>
      </a>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <div class="flex items-start justify-between gap-4">
          <div class="min-w-0 flex-1">
            <!-- Title - Clickable -->
            <a
              :href="getItemLink()"
              :target="item.content_type === 'note' ? '_self' : '_blank'"
              class="text-sm font-medium text-gray-900 hover:text-blue-600 truncate block cursor-pointer"
              @click="handleItemClick($event)"
            >
              {{ item.title }}
            </a>
            <p v-if="item.description" class="mt-1 text-sm text-gray-500 line-clamp-2">
              {{ item.description }}
            </p>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2">
            <!-- AI Summary Button -->
            <button
              @click.stop="handleAISummary"
              :disabled="aiLoading"
              class="p-1 text-purple-500 hover:text-purple-700 hover:bg-purple-50 rounded transition-colors"
              title="AI 摘要和分类推荐"
            >
              <SparklesIcon v-if="!aiLoading" class="w-5 h-5" />
              <svg v-else class="w-5 h-5 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </button>

            <!-- Dropdown Menu -->
            <div class="relative" v-click-outside="closeMenu">
              <button
                @click.stop="showMenu = !showMenu"
                class="p-1 text-gray-400 hover:text-gray-600 rounded"
              >
                <EllipsisVerticalIcon class="w-5 h-5" />
              </button>

              <div
                v-if="showMenu"
                class="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10"
              >
                <a
                  v-if="item.content_type === 'file' && item.file_path"
                  :href="`/files/${item.file_path}`"
                  target="_blank"
                  class="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <ArrowDownTrayIcon class="w-4 h-4" />
                  下载
                </a>
                <a
                  v-if="item.content_type === 'url' && item.url"
                  :href="item.url"
                  target="_blank"
                  class="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <ArrowTopRightOnSquareIcon class="w-4 h-4" />
                  打开链接
                </a>
                <button
                  @click="showCategoryEditor = true; showMenu = false"
                  class="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <FolderIcon class="w-4 h-4" />
                  修改分类
                </button>
                <button
                  @click="handleReclassify"
                  class="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <ArrowPathIcon class="w-4 h-4" />
                  自动重新分类
                </button>
                <button
                  @click="handleDelete"
                  class="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  <TrashIcon class="w-4 h-4" />
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Meta Info -->
        <div class="mt-2 flex items-center gap-4 text-xs text-gray-500">
          <span class="flex items-center gap-1">
            <component :is="typeIcons[item.content_type]" class="w-4 h-4" />
            {{ typeLabels[item.content_type] || item.content_type }}
          </span>
          <!-- Editable Category -->
          <button
            @click.stop="showCategoryEditor = true"
            class="flex items-center gap-1 hover:text-blue-600 transition-colors"
            :title="item.category_name ? '点击修改分类' : '点击设置分类'"
          >
            <FolderIcon class="w-4 h-4" />
            <span :class="item.category_name ? '' : 'italic text-gray-400'">
              {{ item.category_name || '未分类' }}
            </span>
            <PencilIcon class="w-3 h-3 opacity-50" />
          </button>
          <span v-if="item.file_size" class="flex items-center gap-1">
            {{ formatSize(item.file_size) }}
          </span>
          <span>
            {{ formatDate(item.created_at) }}
          </span>
        </div>

        <!-- AI Summary Display -->
        <div v-if="aiSummary" class="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
          <div class="flex items-start gap-2">
            <SparklesIcon class="w-4 h-4 text-purple-500 mt-0.5 flex-shrink-0" />
            <div class="flex-1 min-w-0">
              <p class="text-sm text-gray-900">{{ aiSummary.summary }}</p>
              <p v-if="aiSummary.recommended_category" class="mt-2 text-sm">
                <span class="text-gray-500">推荐分类：</span>
                <button
                  @click="applyRecommendedCategory"
                  class="text-red-600 font-medium hover:text-red-700 hover:underline"
                >
                  {{ aiSummary.recommended_category }}
                </button>
                <span class="text-gray-400 text-xs ml-1">(点击应用)</span>
              </p>
            </div>
            <button @click="aiSummary = null" class="text-gray-400 hover:text-gray-600">
              <XMarkIcon class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- AI Error Display -->
        <div v-if="aiError" class="mt-3 p-3 bg-red-50 rounded-lg border border-red-200">
          <div class="flex items-start gap-2">
            <ExclamationCircleIcon class="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
            <p class="text-sm text-red-700 flex-1">{{ aiError }}</p>
            <button @click="aiError = null" class="text-red-400 hover:text-red-600">
              <XMarkIcon class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Tags -->
        <div v-if="item.tags && item.tags.length > 0" class="mt-2 flex flex-wrap gap-1">
          <span
            v-for="tag in item.tags"
            :key="tag.id"
            class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700"
          >
            {{ tag.name }}
          </span>
        </div>
      </div>
    </div>

    <!-- Category Editor Modal -->
    <div v-if="showCategoryEditor" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showCategoryEditor = false">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">修改分类</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">选择分类</label>
            <select
              v-model="selectedCategoryId"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option :value="null">未分类</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button
            @click="showCategoryEditor = false"
            class="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
          >
            取消
          </button>
          <button
            @click="saveCategory"
            :disabled="savingCategory"
            class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {{ savingCategory ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMainStore } from '../stores/main'
import * as api from '../api'
import {
  DocumentTextIcon,
  LinkIcon,
  PencilSquareIcon,
  FolderIcon,
  EllipsisVerticalIcon,
  ArrowDownTrayIcon,
  ArrowTopRightOnSquareIcon,
  ArrowPathIcon,
  TrashIcon,
  SparklesIcon,
  XMarkIcon,
  PencilIcon,
  ExclamationCircleIcon,
} from '@heroicons/vue/24/outline'

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
  highlight: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['delete', 'reclassify', 'update'])

const store = useMainStore()

const showMenu = ref(false)
const showCategoryEditor = ref(false)
const selectedCategoryId = ref(props.item.category_id)
const savingCategory = ref(false)
const aiLoading = ref(false)
const aiSummary = ref(null)
const aiError = ref(null)

const categories = computed(() => store.categories)

const typeIcons = {
  file: DocumentTextIcon,
  url: LinkIcon,
  note: PencilSquareIcon,
}

const typeColors = {
  file: 'bg-blue-500',
  url: 'bg-green-500',
  note: 'bg-purple-500',
}

const typeLabels = {
  file: '文件',
  url: '网页',
  note: '笔记',
}

function getItemLink() {
  if (props.item.content_type === 'file' && props.item.file_path) {
    return `/files/${props.item.file_path}`
  }
  if (props.item.content_type === 'url' && props.item.url) {
    return props.item.url
  }
  return '#'
}

function handleItemClick(event) {
  if (props.item.content_type === 'note') {
    event.preventDefault()
    if (props.item.extracted_text) {
      alert(props.item.extracted_text.substring(0, 500) + (props.item.extracted_text.length > 500 ? '...' : ''))
    }
  }
}

async function handleAISummary() {
  aiLoading.value = true
  aiError.value = null
  aiSummary.value = null

  try {
    const response = await api.getAISummary(props.item.id)
    aiSummary.value = response.data
  } catch (error) {
    aiError.value = error.response?.data?.detail || 'AI分析失败，请确保Ollama正在运行'
  } finally {
    aiLoading.value = false
  }
}

async function applyRecommendedCategory() {
  if (!aiSummary.value?.recommended_category_id) return

  savingCategory.value = true
  try {
    await api.updateItem(props.item.id, {
      category_id: aiSummary.value.recommended_category_id
    })
    emit('update', props.item.id)
    aiSummary.value = null
  } catch (error) {
    alert('应用分类失败')
  } finally {
    savingCategory.value = false
  }
}

async function saveCategory() {
  savingCategory.value = true
  try {
    await api.updateItem(props.item.id, {
      category_id: selectedCategoryId.value
    })
    showCategoryEditor.value = false
    emit('update', props.item.id)
  } catch (error) {
    alert('保存分类失败')
  } finally {
    savingCategory.value = false
  }
}

function formatSize(bytes) {
  if (!bytes) return ''
  if (bytes > 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  if (bytes > 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${bytes} B`
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function closeMenu() {
  showMenu.value = false
}

function handleDelete() {
  showMenu.value = false
  emit('delete', props.item.id)
}

function handleReclassify() {
  showMenu.value = false
  emit('reclassify', props.item.id)
}

onMounted(async () => {
  if (store.categories.length === 0) {
    await store.fetchCategories()
  }
})

// Simple click outside directive
const vClickOutside = {
  mounted(el, binding) {
    el._clickOutside = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value()
      }
    }
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el) {
    document.removeEventListener('click', el._clickOutside)
  },
}
</script>
