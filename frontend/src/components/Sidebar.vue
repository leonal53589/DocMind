<template>
  <aside class="fixed left-0 top-0 h-screen w-64 bg-white border-r border-gray-200 flex flex-col">
    <!-- Logo -->
    <div class="p-4 border-b border-gray-200">
      <router-link to="/" class="flex items-center gap-2">
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <ArchiveBoxIcon class="w-5 h-5 text-white" />
        </div>
        <span class="text-lg font-semibold text-gray-900">知识库</span>
      </router-link>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 p-4 space-y-1 overflow-y-auto">
      <router-link
        to="/"
        :class="[
          'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
          isActive('/') ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-100'
        ]"
      >
        <HomeIcon class="w-5 h-5" />
        仪表盘
      </router-link>

      <router-link
        to="/browse"
        :class="[
          'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
          isActive('/browse') && !$route.params.categoryId ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-100'
        ]"
      >
        <FolderIcon class="w-5 h-5" />
        所有项目
      </router-link>

      <router-link
        to="/search"
        :class="[
          'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
          isActive('/search') ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-100'
        ]"
      >
        <MagnifyingGlassIcon class="w-5 h-5" />
        搜索
      </router-link>

      <!-- Categories Section -->
      <div class="pt-4">
        <div class="flex items-center justify-between px-3 mb-2">
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">分类</span>
          <button
            @click="toggleCategories"
            class="text-gray-400 hover:text-gray-600"
          >
            <ChevronDownIcon :class="['w-4 h-4 transition-transform', showCategories ? '' : '-rotate-90']" />
          </button>
        </div>

        <div v-if="showCategories && loading" class="px-3 py-2 text-sm text-gray-500">
          加载中...
        </div>

        <div v-else-if="showCategories" class="space-y-0.5">
          <router-link
            v-for="category in categories"
            :key="category.id"
            :to="`/browse/${category.id}`"
            :class="[
              'flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors',
              isActiveCategory(category.id) ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-100'
            ]"
          >
            <div class="flex items-center gap-2 min-w-0">
              <component :is="getCategoryIcon(category.name)" class="w-4 h-4 flex-shrink-0" />
              <span class="truncate">{{ category.name }}</span>
            </div>
            <span class="text-xs text-gray-400">{{ category.item_count }}</span>
          </router-link>

          <div v-if="categories.length === 0" class="px-3 py-2 text-sm text-gray-500">
            暂无分类
          </div>
        </div>
      </div>
    </nav>

    <!-- Settings Link -->
    <div class="p-4 border-t border-gray-200">
      <router-link
        to="/settings"
        :class="[
          'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
          isActive('/settings') ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-100'
        ]"
      >
        <Cog6ToothIcon class="w-5 h-5" />
        设置
      </router-link>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMainStore } from '../stores/main'
import {
  ArchiveBoxIcon,
  HomeIcon,
  FolderIcon,
  MagnifyingGlassIcon,
  Cog6ToothIcon,
  ChevronDownIcon,
  BookOpenIcon,
  LightBulbIcon,
  CodeBracketIcon,
  DocumentTextIcon,
  GlobeAltIcon,
  AcademicCapIcon,
  BeakerIcon,
  WrenchScrewdriverIcon,
} from '@heroicons/vue/24/outline'

const route = useRoute()
const store = useMainStore()

const showCategories = ref(true)
const loading = ref(false)

const categories = computed(() => store.categories)

function isActive(path) {
  return route.path === path
}

function isActiveCategory(categoryId) {
  return route.params.categoryId === String(categoryId)
}

function toggleCategories() {
  showCategories.value = !showCategories.value
}

function getCategoryIcon(name) {
  const lower = name.toLowerCase()
  if (lower.includes('math') || lower.includes('principle')) return AcademicCapIcon
  if (lower.includes('idea') || lower.includes('concept')) return LightBulbIcon
  if (lower.includes('program') || lower.includes('code') || lower.includes('implementation')) return CodeBracketIcon
  if (lower.includes('research') || lower.includes('paper')) return BeakerIcon
  if (lower.includes('reference') || lower.includes('doc')) return BookOpenIcon
  if (lower.includes('web') || lower.includes('link')) return GlobeAltIcon
  if (lower.includes('tool') || lower.includes('utility')) return WrenchScrewdriverIcon
  return DocumentTextIcon
}

onMounted(async () => {
  loading.value = true
  try {
    await store.fetchCategories()
  } finally {
    loading.value = false
  }
})
</script>
