<template>
  <div class="space-y-8">
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
      <div
        v-for="(stat, index) in statsCards"
        :key="stat.key"
        class="stat-card group"
        :style="{ animationDelay: `${index * 100}ms` }"
      >
        <div class="flex items-center justify-between">
          <div :class="['stat-icon', stat.colorClass]">
            <component :is="stat.icon" class="w-6 h-6" />
          </div>
          <div class="stat-trend">
            <ArrowTrendingUpIcon class="w-4 h-4" />
          </div>
        </div>
        <div class="mt-4">
          <p class="text-sm font-medium text-gray-500">{{ stat.label }}</p>
          <p class="stat-value">
            <span class="counter" :data-target="stat.value">{{ animatedStats[stat.key] || 0 }}</span>
            <span v-if="stat.suffix" class="text-lg text-gray-400">{{ stat.suffix }}</span>
          </p>
        </div>
        <div class="stat-decoration" :class="stat.decorationClass"></div>
      </div>
    </div>

    <!-- Content Type Breakdown -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <div
        v-for="(type, index) in contentTypes"
        :key="type.key"
        class="type-card group"
        :style="{ animationDelay: `${(index + 4) * 100}ms` }"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div :class="['type-icon', type.iconClass]">
              <component :is="type.icon" class="w-5 h-5" />
            </div>
            <h3 class="text-lg font-semibold text-gray-900">{{ type.label }}</h3>
          </div>
        </div>
        <p :class="['type-value', type.textClass]">{{ stats?.items_by_type?.[type.key] || 0 }}</p>
        <p class="text-sm text-gray-500 mt-1">{{ type.description }}</p>
        <div class="type-bar mt-4">
          <div
            :class="['type-bar-fill', type.barClass]"
            :style="{ width: getTypePercentage(type.key) + '%' }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Recent Items -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-indigo-500 rounded-xl flex items-center justify-center">
            <ClockIcon class="w-5 h-5 text-white" />
          </div>
          <h2 class="text-lg font-bold text-gray-900">最近项目</h2>
        </div>
        <router-link to="/browse" class="text-sm text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1">
          查看全部
          <ArrowRightIcon class="w-4 h-4" />
        </router-link>
      </div>
      <div class="divide-y divide-gray-100">
        <div v-if="loading" class="p-12 text-center">
          <div class="text-indigo-500">
            <svg class="w-8 h-8 mx-auto animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <p class="mt-4 text-gray-500">加载中...</p>
        </div>
        <div v-else-if="recentItems.length === 0" class="p-12 text-center">
          <div class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <InboxIcon class="w-10 h-10 text-gray-400" />
          </div>
          <p class="text-gray-500">暂无项目。导入一些内容开始使用吧。</p>
        </div>
        <div v-else>
          <ItemCard
            v-for="item in recentItems"
            :key="item.id"
            :item="item"
            :all-items="allItems"
            @delete="handleDelete"
            @update="handleUpdate"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
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
  ClockIcon,
  ArrowRightIcon,
  InboxIcon,
  ArrowTrendingUpIcon,
} from '@heroicons/vue/24/outline'
import ItemCard from '../components/ItemCard.vue'

const store = useMainStore()

const loading = ref(true)
const recentItems = ref([])
const allItems = ref([])
const animatedStats = ref({})

const stats = computed(() => store.stats)

const statsCards = computed(() => [
  {
    key: 'total_items',
    label: '项目总数',
    value: stats.value?.total_items || 0,
    icon: DocumentIcon,
    colorClass: 'stat-icon-blue',
    decorationClass: 'decoration-blue'
  },
  {
    key: 'total_categories',
    label: '分类数量',
    value: stats.value?.total_categories || 0,
    icon: FolderIcon,
    colorClass: 'stat-icon-emerald',
    decorationClass: 'decoration-emerald'
  },
  {
    key: 'total_tags',
    label: '标签数量',
    value: stats.value?.total_tags || 0,
    icon: TagIcon,
    colorClass: 'stat-icon-purple',
    decorationClass: 'decoration-purple'
  },
  {
    key: 'storage',
    label: '存储空间',
    value: formatStorageValue(stats.value?.total_storage_bytes),
    suffix: formatStorageUnit(stats.value?.total_storage_bytes),
    icon: CircleStackIcon,
    colorClass: 'stat-icon-amber',
    decorationClass: 'decoration-amber'
  }
])

const contentTypes = [
  {
    key: 'file',
    label: '文件',
    description: '已导入的文件',
    icon: DocumentTextIcon,
    iconClass: 'bg-blue-100 text-blue-600',
    textClass: 'text-blue-600',
    barClass: 'bg-gradient-to-r from-blue-500 to-blue-400'
  },
  {
    key: 'url',
    label: '网页',
    description: '已保存的网页',
    icon: LinkIcon,
    iconClass: 'bg-emerald-100 text-emerald-600',
    textClass: 'text-emerald-600',
    barClass: 'bg-gradient-to-r from-emerald-500 to-emerald-400'
  },
  {
    key: 'note',
    label: '笔记',
    description: '已创建的笔记',
    icon: PencilSquareIcon,
    iconClass: 'bg-purple-100 text-purple-600',
    textClass: 'text-purple-600',
    barClass: 'bg-gradient-to-r from-purple-500 to-purple-400'
  }
]

function formatStorageValue(bytes) {
  if (!bytes) return 0
  if (bytes > 1024 * 1024 * 1024) return (bytes / (1024 * 1024 * 1024)).toFixed(1)
  if (bytes > 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1)
  if (bytes > 1024) return (bytes / 1024).toFixed(1)
  return bytes
}

function formatStorageUnit(bytes) {
  if (!bytes) return 'B'
  if (bytes > 1024 * 1024 * 1024) return 'GB'
  if (bytes > 1024 * 1024) return 'MB'
  if (bytes > 1024) return 'KB'
  return 'B'
}

function formatSize(bytes) {
  if (!bytes) return '0 B'
  if (bytes > 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`
  if (bytes > 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  if (bytes > 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${bytes} B`
}

function getTypePercentage(type) {
  const total = stats.value?.total_items || 0
  if (total === 0) return 0
  const count = stats.value?.items_by_type?.[type] || 0
  return Math.min((count / total) * 100, 100)
}

// Animate counter
function animateValue(key, end, duration = 1000) {
  const start = 0
  const startTime = performance.now()

  function update(currentTime) {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    const easeOutQuart = 1 - Math.pow(1 - progress, 4)
    animatedStats.value[key] = Math.round(start + (end - start) * easeOutQuart)

    if (progress < 1) {
      requestAnimationFrame(update)
    }
  }

  requestAnimationFrame(update)
}

watch(stats, (newStats) => {
  if (newStats) {
    animateValue('total_items', newStats.total_items || 0)
    animateValue('total_categories', newStats.total_categories || 0)
    animateValue('total_tags', newStats.total_tags || 0)
    animateValue('storage', formatStorageValue(newStats.total_storage_bytes))
  }
}, { immediate: true })

async function handleDelete(id) {
  if (confirm('确定要删除这个项目吗？')) {
    await store.deleteItem(id)
    recentItems.value = recentItems.value.filter(item => item.id !== id)
  }
}

async function handleUpdate(id) {
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
    const allData = await api.getItems({ page: 1, page_size: 1000 })
    allItems.value = allData.data?.items || []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* Stat Card */
.stat-card {
  @apply relative bg-white rounded-xl shadow-sm border border-gray-100 p-6 overflow-hidden;
}

.stat-icon {
  @apply w-12 h-12 rounded-xl flex items-center justify-center;
}

.stat-icon-blue {
  @apply bg-blue-100 text-blue-600;
}

.stat-icon-emerald {
  @apply bg-emerald-100 text-emerald-600;
}

.stat-icon-purple {
  @apply bg-purple-100 text-purple-600;
}

.stat-icon-amber {
  @apply bg-amber-100 text-amber-600;
}

.stat-trend {
  @apply w-8 h-8 rounded-lg bg-emerald-50 text-emerald-500 flex items-center justify-center;
}

.stat-value {
  @apply text-3xl font-bold text-gray-900 mt-1;
}

.stat-decoration {
  @apply absolute -right-8 -bottom-8 w-32 h-32 rounded-full opacity-10;
}

.decoration-blue { @apply bg-blue-500; }
.decoration-emerald { @apply bg-emerald-500; }
.decoration-purple { @apply bg-purple-500; }
.decoration-amber { @apply bg-amber-500; }

/* Type Card */
.type-card {
  @apply bg-white rounded-xl shadow-sm border border-gray-100 p-6;
}

.type-icon {
  @apply w-10 h-10 rounded-xl flex items-center justify-center;
}

.type-value {
  @apply text-4xl font-bold;
}

.type-bar {
  @apply h-2 bg-gray-100 rounded-full overflow-hidden;
}

.type-bar-fill {
  @apply h-full rounded-full;
}
</style>
