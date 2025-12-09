<template>
  <div class="item-card px-6 py-4 hover:bg-gray-50 transition-colors">
    <div class="flex items-start gap-4">
      <!-- Thumbnail or Icon - Clickable -->
      <button
        class="flex-shrink-0 cursor-pointer"
        @click="handleItemClick($event)"
      >
        <img
          v-if="item.thumbnail_path"
          :src="`/thumbnails/${item.thumbnail_path}`"
          :alt="item.title"
          class="w-16 h-16 object-cover rounded-lg"
        />
        <div
          v-else
          :class="[
            'w-16 h-16 rounded-lg flex items-center justify-center',
            typeColors[item.content_type] || 'bg-gray-100'
          ]"
        >
          <component :is="typeIcons[item.content_type]" class="w-8 h-8 text-white" />
        </div>
      </button>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <div class="flex items-start justify-between gap-4">
          <div class="min-w-0 flex-1">
            <!-- Title - Clickable or Editable -->
            <div class="flex items-center gap-2">
              <button
                v-if="!isEditingTitle"
                class="text-sm font-medium text-gray-900 hover:text-blue-600 truncate block cursor-pointer text-left"
                @click="handleItemClick($event)"
              >
                {{ item.title }}
              </button>
              <input
                v-else
                v-model="editTitle"
                @blur="saveTitle"
                @keyup.enter="saveTitle"
                @keyup.escape="cancelEditTitle"
                class="text-sm font-medium text-gray-900 border border-blue-500 rounded px-2 py-1 w-full"
                ref="titleInput"
              />
              <!-- Favorite Star -->
              <button
                @click.stop="handleToggleFavorite"
                :disabled="favoriteLoading"
                class="flex-shrink-0"
                :title="item.is_favorite ? '取消收藏' : '添加到收藏'"
              >
                <StarIconSolid v-if="item.is_favorite" class="w-5 h-5 text-yellow-500" />
                <StarIconOutline v-else class="w-5 h-5 text-gray-300 hover:text-yellow-500" />
              </button>
            </div>
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
                <button
                  v-if="canPreview()"
                  @click="showPreviewModal = true; showMenu = false"
                  class="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <EyeIcon class="w-4 h-4" />
                  预览
                </button>
                <button
                  @click="startEditTitle"
                  class="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <PencilIcon class="w-4 h-4" />
                  重命名
                </button>
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
                  @click="openAssociationEditor"
                  class="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <LinkIcon class="w-4 h-4" />
                  管理关联
                </button>
                <button
                  @click="handleReclassify"
                  :disabled="reclassifyLoading"
                  class="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 disabled:opacity-50"
                >
                  <svg v-if="reclassifyLoading" class="w-4 h-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <ArrowPathIcon v-else class="w-4 h-4" />
                  {{ reclassifyLoading ? '分类中...' : '自动重新分类' }}
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
            v-for="(tag, index) in item.tags"
            :key="index"
            class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700"
          >
            {{ tag }}
          </span>
        </div>

        <!-- Associated Items -->
        <div v-if="item.associated_items && item.associated_items.length > 0" class="mt-3">
          <div class="flex items-center gap-2 text-xs text-gray-500 mb-2">
            <LinkIcon class="w-3 h-3" />
            <span>关联项目：</span>
          </div>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="assoc in item.associated_items"
              :key="assoc.id"
              class="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-blue-50 text-blue-700 text-xs"
            >
              <component :is="typeIcons[assoc.content_type]" class="w-3 h-3" />
              <span class="max-w-32 truncate">{{ assoc.title }}</span>
              <button
                @click.stop="removeAssociation(assoc.id)"
                class="text-blue-400 hover:text-blue-600"
                title="移除关联"
              >
                <XMarkIcon class="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- File Preview Modal -->
    <FilePreviewModal
      :isOpen="showPreviewModal"
      :item="item"
      @close="showPreviewModal = false"
    />

    <!-- Associated Item Preview Modal -->
    <FilePreviewModal
      :isOpen="showAssociatedPreviewModal"
      :item="selectedAssociatedItem"
      @close="showAssociatedPreviewModal = false; selectedAssociatedItem = null"
    />

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

    <!-- Association Editor Modal -->
    <div v-if="showAssociationEditor" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showAssociationEditor = false">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <div class="p-6 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">管理关联项目</h3>
        </div>

        <div class="flex-1 overflow-auto p-6">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Left: Current Associations & Add New -->
            <div class="space-y-4">
              <!-- Current Associations -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">当前关联</label>
                <div v-if="item.associated_items && item.associated_items.length > 0" class="space-y-2 max-h-48 overflow-y-auto">
                  <div
                    v-for="assoc in item.associated_items"
                    :key="assoc.id"
                    class="flex items-center justify-between p-2 bg-gray-50 rounded"
                  >
                    <div class="flex items-center gap-2 min-w-0">
                      <component :is="typeIcons[assoc.content_type]" class="w-4 h-4 text-gray-500 flex-shrink-0" />
                      <span class="text-sm truncate">{{ assoc.title }}</span>
                    </div>
                    <button
                      @click="removeAssociation(assoc.id)"
                      class="text-red-500 hover:text-red-700 flex-shrink-0"
                    >
                      <XMarkIcon class="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <p v-else class="text-sm text-gray-500">暂无关联项目</p>
              </div>

              <!-- Add New Association -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">添加关联</label>
                <div v-if="loadingItems" class="text-sm text-gray-500 py-2">
                  <span class="inline-flex items-center gap-2">
                    <svg class="w-4 h-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    加载项目列表...
                  </span>
                </div>
                <div v-else class="flex gap-2">
                  <select
                    v-model="selectedAssociationId"
                    class="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  >
                    <option :value="null">选择项目...</option>
                    <option
                      v-for="availableItem in availableItemsForAssociation"
                      :key="availableItem.id"
                      :value="availableItem.id"
                    >
                      {{ availableItem.title }}
                    </option>
                  </select>
                  <button
                    @click="addAssociation"
                    :disabled="!selectedAssociationId || addingAssociation"
                    class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {{ addingAssociation ? '添加中...' : '添加' }}
                  </button>
                </div>
                <p v-if="!loadingItems && availableItemsForAssociation.length === 0" class="text-xs text-gray-400 mt-1">
                  没有更多可关联的项目
                </p>
              </div>
            </div>

            <!-- Right: Association Network Graph -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">关联网络图</label>
              <div class="border border-gray-200 rounded-lg bg-gray-50 h-64 relative overflow-hidden">
                <svg ref="networkSvg" class="w-full h-full" viewBox="0 0 400 256" preserveAspectRatio="xMidYMid meet">
                  <!-- Center node (current item) -->
                  <circle
                    :cx="networkCenter.x"
                    :cy="networkCenter.y"
                    r="30"
                    :fill="getNodeFillColor(item.content_type)"
                  />
                  <text
                    :x="networkCenter.x"
                    :y="networkCenter.y"
                    text-anchor="middle"
                    dominant-baseline="middle"
                    fill="white"
                    font-size="10"
                    font-weight="500"
                  >
                    {{ item.title.substring(0, 6) }}{{ item.title.length > 6 ? '...' : '' }}
                  </text>

                  <!-- Associated items as connected nodes -->
                  <g v-for="(assoc, index) in item.associated_items || []" :key="assoc.id">
                    <!-- Connection line -->
                    <line
                      :x1="networkCenter.x"
                      :y1="networkCenter.y"
                      :x2="getNodePosition(index, item.associated_items?.length || 0).x"
                      :y2="getNodePosition(index, item.associated_items?.length || 0).y"
                      stroke="#CBD5E1"
                      stroke-width="2"
                    />
                    <!-- Node -->
                    <circle
                      :cx="getNodePosition(index, item.associated_items?.length || 0).x"
                      :cy="getNodePosition(index, item.associated_items?.length || 0).y"
                      r="24"
                      :fill="getNodeFillColor(assoc.content_type)"
                      class="cursor-pointer hover:opacity-80 transition-opacity"
                      @click="navigateToItem(assoc)"
                    />
                    <!-- Node label -->
                    <text
                      :x="getNodePosition(index, item.associated_items?.length || 0).x"
                      :y="getNodePosition(index, item.associated_items?.length || 0).y"
                      text-anchor="middle"
                      dominant-baseline="middle"
                      fill="white"
                      font-size="9"
                      class="pointer-events-none"
                    >
                      {{ assoc.title.substring(0, 4) }}{{ assoc.title.length > 4 ? '..' : '' }}
                    </text>
                  </g>
                </svg>

                <!-- Empty state -->
                <div
                  v-if="!item.associated_items || item.associated_items.length === 0"
                  class="absolute inset-0 flex items-center justify-center text-gray-400 text-sm"
                >
                  暂无关联，添加关联后将显示网络图
                </div>
              </div>
              <p class="text-xs text-gray-400 mt-2">点击节点可查看关联项目详情</p>
            </div>
          </div>
        </div>

        <div class="p-6 border-t border-gray-200 flex justify-end">
          <button
            @click="showAssociationEditor = false"
            class="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useMainStore } from '../stores/main'
import * as api from '../api'
import FilePreviewModal from './FilePreviewModal.vue'
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
  StarIcon as StarIconOutline,
  EyeIcon,
} from '@heroicons/vue/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/vue/24/solid'

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
  highlight: {
    type: String,
    default: '',
  },
  allItems: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['delete', 'reclassify', 'update'])

const store = useMainStore()

const showMenu = ref(false)
const showCategoryEditor = ref(false)
const showAssociationEditor = ref(false)
const showPreviewModal = ref(false)
const showAssociatedPreviewModal = ref(false)
const selectedAssociatedItem = ref(null)
const selectedCategoryId = ref(props.item.category_id)
const savingCategory = ref(false)
const aiLoading = ref(false)
const aiSummary = ref(null)
const aiError = ref(null)
const reclassifyLoading = ref(false)
const favoriteLoading = ref(false)

// Rename state
const isEditingTitle = ref(false)
const editTitle = ref('')
const titleInput = ref(null)

// Association state
const selectedAssociationId = ref(null)
const addingAssociation = ref(false)
const availableItems = ref([])
const loadingItems = ref(false)

const categories = computed(() => store.categories)

// Items available for association (excluding current item and already associated items)
const availableItemsForAssociation = computed(() => {
  const associatedIds = new Set(props.item.associated_items?.map(a => a.id) || [])
  associatedIds.add(props.item.id)
  // Use availableItems if loaded, otherwise fall back to store items
  const itemList = availableItems.value.length > 0 ? availableItems.value : store.items
  return itemList.filter(i => !associatedIds.has(i.id))
})

// Fetch all items when association editor opens
async function openAssociationEditor() {
  showMenu.value = false
  showAssociationEditor.value = true

  // If we already have items from the store, use those immediately
  if (store.items.length > 0 && availableItems.value.length === 0) {
    availableItems.value = [...store.items]
  }

  // Always fetch fresh items
  loadingItems.value = true
  try {
    const data = await store.fetchItems({ page: 1, page_size: 1000 })
    if (data?.items) {
      availableItems.value = data.items
    }
  } catch (error) {
    console.error('Failed to fetch items for association:', error)
  } finally {
    loadingItems.value = false
  }
}

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

// Network graph helpers
const networkSvg = ref(null)
const networkCenter = { x: 200, y: 128 } // Center of 400x256 viewBox

function getNodePosition(index, total) {
  if (total === 0) return { x: 0, y: 0 }
  const angle = (2 * Math.PI * index / total) - Math.PI / 2 // Start from top
  const radius = 90
  return {
    x: networkCenter.x + radius * Math.cos(angle),
    y: networkCenter.y + radius * Math.sin(angle)
  }
}

function getNodeColorClass(contentType) {
  const colors = {
    file: 'text-blue-500',
    url: 'text-green-500',
    note: 'text-purple-500',
  }
  return colors[contentType] || 'text-gray-500'
}

function getNodeFillColor(contentType) {
  const colors = {
    file: '#3B82F6',    // blue-500
    url: '#22C55E',     // green-500
    note: '#A855F7',    // purple-500
  }
  return colors[contentType] || '#6B7280' // gray-500
}

async function navigateToItem(assoc) {
  // Close association editor
  showAssociationEditor.value = false

  // Fetch full item data before showing preview
  try {
    const response = await api.getItem(assoc.id)
    selectedAssociatedItem.value = response.data
    showAssociatedPreviewModal.value = true
  } catch (error) {
    console.error('Failed to fetch item details:', error)
    alert('无法加载项目详情')
  }
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

// Check if file can be previewed in modal
function canPreview() {
  if (props.item.content_type !== 'file' || !props.item.file_path) return false
  const path = props.item.file_path.toLowerCase()
  const previewableExtensions = [
    '.md', '.markdown', '.txt', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini',
    '.js', '.ts', '.jsx', '.tsx', '.vue', '.py', '.java', '.c', '.cpp', '.h', '.hpp',
    '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.sh', '.bash',
    '.zsh', '.ps1', '.sql', '.css', '.scss', '.less', '.html', '.htm',
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp',
    '.pdf', '.mp4', '.webm', '.ogg', '.mp3', '.wav', '.flac'
  ]
  return previewableExtensions.some(ext => path.endsWith(ext))
}

function handleItemClick(event) {
  event.preventDefault()

  // For files that can be previewed, show the preview modal
  if (canPreview()) {
    showPreviewModal.value = true
    return
  }

  // For other files, open in new tab
  if (props.item.content_type === 'file' && props.item.file_path) {
    window.open(`/files/${props.item.file_path}`, '_blank')
    return
  }

  // For URLs, open in new tab
  if (props.item.content_type === 'url' && props.item.url) {
    window.open(props.item.url, '_blank')
    return
  }

  // For notes, show the content
  if (props.item.content_type === 'note') {
    if (props.item.extracted_text) {
      alert(props.item.extracted_text.substring(0, 500) + (props.item.extracted_text.length > 500 ? '...' : ''))
    }
  }
}

// Rename functions
function startEditTitle() {
  showMenu.value = false
  editTitle.value = props.item.title
  isEditingTitle.value = true
  nextTick(() => {
    titleInput.value?.focus()
    titleInput.value?.select()
  })
}

async function saveTitle() {
  if (!editTitle.value.trim() || editTitle.value === props.item.title) {
    cancelEditTitle()
    return
  }

  try {
    await api.updateItem(props.item.id, { title: editTitle.value.trim() })
    emit('update', props.item.id)
  } catch (error) {
    alert('重命名失败')
  }
  isEditingTitle.value = false
}

function cancelEditTitle() {
  isEditingTitle.value = false
  editTitle.value = ''
}

// Favorite functions
async function handleToggleFavorite() {
  favoriteLoading.value = true
  try {
    await api.toggleFavorite(props.item.id)
    emit('update', props.item.id)
  } catch (error) {
    alert('操作失败')
  } finally {
    favoriteLoading.value = false
  }
}

// Association functions
async function addAssociation() {
  if (!selectedAssociationId.value) return

  addingAssociation.value = true
  try {
    await api.addAssociation(props.item.id, selectedAssociationId.value)
    selectedAssociationId.value = null
    emit('update', props.item.id)
  } catch (error) {
    alert(error.response?.data?.detail || '添加关联失败')
  } finally {
    addingAssociation.value = false
  }
}

async function removeAssociation(associatedItemId) {
  try {
    await api.removeAssociation(props.item.id, associatedItemId)
    emit('update', props.item.id)
  } catch (error) {
    alert('移除关联失败')
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

async function handleReclassify() {
  showMenu.value = false
  reclassifyLoading.value = true
  aiError.value = null

  try {
    await api.reclassifyItem(props.item.id)
    emit('update', props.item.id)
  } catch (error) {
    aiError.value = error.response?.data?.detail || 'AI分类失败，请稍后重试'
  } finally {
    reclassifyLoading.value = false
  }
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
