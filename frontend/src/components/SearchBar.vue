<template>
  <div class="flex-1 max-w-xl">
    <div class="search-wrapper group" :class="{ focused: isFocused }">
      <div class="search-icon-wrapper">
        <MagnifyingGlassIcon class="w-5 h-5 transition-colors duration-200" :class="isFocused ? 'text-indigo-500' : 'text-gray-400'" />
      </div>
      <input
        v-model="query"
        @keyup.enter="handleSearch"
        @focus="isFocused = true"
        @blur="isFocused = false"
        type="text"
        placeholder="搜索您的知识库..."
        class="search-input"
      />
      <Transition name="fade-scale">
        <button
          v-if="query"
          @click="clearSearch"
          class="clear-button"
        >
          <XMarkIcon class="w-4 h-4" />
        </button>
      </Transition>
      <Transition name="fade-scale">
        <div v-if="query" class="search-shortcut">
          <kbd>Enter</kbd>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMainStore } from '../stores/main'
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const route = useRoute()
const store = useMainStore()

const query = ref('')
const isFocused = ref(false)

// Sync with route query
watch(() => route.query.q, (newQuery) => {
  if (route.name === 'search' && newQuery) {
    query.value = newQuery
  }
}, { immediate: true })

function handleSearch() {
  if (query.value.trim()) {
    store.searchQuery = query.value
    router.push({ name: 'search', query: { q: query.value } })
  }
}

function clearSearch() {
  query.value = ''
}
</script>

<style scoped>
.search-wrapper {
  @apply relative flex items-center bg-gray-50/80 border border-gray-200 rounded-xl overflow-hidden
         transition-all duration-300 ease-out;
}

.search-wrapper.focused {
  @apply bg-white border-indigo-300 shadow-lg shadow-indigo-100/50;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

.search-icon-wrapper {
  @apply absolute left-3.5 pointer-events-none;
}

.search-input {
  @apply w-full pl-11 pr-24 py-2.5 bg-transparent border-none text-sm text-gray-900
         placeholder:text-gray-400 focus:outline-none focus:ring-0;
}

.clear-button {
  @apply absolute right-16 p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md
         transition-all duration-200;
}

.search-shortcut {
  @apply absolute right-3 flex items-center;
}

.search-shortcut kbd {
  @apply px-2 py-1 text-xs font-medium text-gray-500 bg-gray-100 rounded-md border border-gray-200;
}

/* Fade Scale Animation */
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.2s ease-out;
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.8);
}
</style>
