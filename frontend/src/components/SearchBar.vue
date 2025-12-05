<template>
  <div class="flex-1 max-w-xl">
    <div class="relative">
      <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
      <input
        v-model="query"
        @keyup.enter="handleSearch"
        type="text"
        placeholder="搜索您的知识库..."
        class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMainStore } from '../stores/main'
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const route = useRoute()
const store = useMainStore()

const query = ref('')

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
</script>
