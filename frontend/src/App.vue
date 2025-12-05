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
                class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
              >
                <PlusIcon class="w-5 h-5" />
                导入
              </button>
            </div>
          </div>
        </header>

        <div class="p-6">
          <router-view />
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
