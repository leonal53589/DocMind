<template>
  <div class="min-h-screen bg-gray-50">
    <div class="flex">
      <!-- Sidebar -->
      <Sidebar />

      <!-- Main content -->
      <main class="flex-1 ml-64">
        <header class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-10">
          <div class="flex items-center justify-between px-6 py-4">
            <SearchBar />
            <div class="flex items-center gap-4">
              <button
                @click="showImportModal = true"
                class="btn-primary"
              >
                <PlusIcon class="w-5 h-5" />
                导入
              </button>
            </div>
          </div>
        </header>

        <div class="p-6">
          <router-view v-slot="{ Component }">
            <component :is="Component" />
          </router-view>
        </div>
      </main>
    </div>

    <!-- Import Modal -->
    <ImportModal v-if="showImportModal" @close="showImportModal = false" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { PlusIcon } from '@heroicons/vue/24/outline'
import Sidebar from './components/Sidebar.vue'
import SearchBar from './components/SearchBar.vue'
import ImportModal from './components/ImportModal.vue'

const showImportModal = ref(false)
</script>

<style>
/* ===== Button Styles ===== */
.btn-primary {
  @apply bg-indigo-600 text-white px-4 py-2 rounded-lg
         hover:bg-indigo-700
         flex items-center gap-2 font-medium
         transition-colors duration-150;
}

.btn-secondary {
  @apply bg-white text-gray-700 px-4 py-2 rounded-lg
         border border-gray-300
         hover:bg-gray-50
         flex items-center gap-2 font-medium
         transition-colors duration-150;
}

.btn-ghost {
  @apply text-gray-600 px-3 py-2 rounded-lg
         hover:bg-gray-100 hover:text-gray-900
         flex items-center gap-2
         transition-colors duration-150;
}

.btn-danger {
  @apply bg-red-600 text-white px-4 py-2 rounded-lg
         hover:bg-red-700
         flex items-center gap-2 font-medium
         transition-colors duration-150;
}

/* ===== Input Styles ===== */
.input-field {
  @apply w-full px-4 py-2 rounded-lg border border-gray-300
         focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200
         transition-colors duration-150
         placeholder:text-gray-400;
}

/* ===== Smooth Scrollbar ===== */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
