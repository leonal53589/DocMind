<template>
  <div class="markdown-viewer" :class="{ 'dark-mode': isDarkMode }">
    <!-- Simple Toolbar -->
    <div class="toolbar">
      <div class="toolbar-left">
        <button
          @click="toggleDarkMode"
          class="toolbar-btn"
          :title="isDarkMode ? 'Light Mode' : 'Dark Mode'"
        >
          <SunIcon v-if="isDarkMode" class="w-5 h-5" />
          <MoonIcon v-else class="w-5 h-5" />
        </button>
        <button
          @click="toggleToc"
          class="toolbar-btn"
          :class="{ active: showToc }"
          title="Table of Contents"
        >
          <Bars3BottomLeftIcon class="w-5 h-5" />
        </button>
      </div>
      <div class="toolbar-right">
        <button
          @click="decreaseFontSize"
          class="toolbar-btn"
          title="Decrease Font Size"
        >
          <MinusIcon class="w-4 h-4" />
        </button>
        <span class="font-size-display">{{ fontSize }}px</span>
        <button
          @click="increaseFontSize"
          class="toolbar-btn"
          title="Increase Font Size"
        >
          <PlusIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <div class="content-wrapper">
      <!-- Table of Contents -->
      <aside v-if="showToc && tocItems.length > 0" class="toc-sidebar">
        <h3 class="toc-title">Table of Contents</h3>
        <nav class="toc-nav">
          <a
            v-for="(item, index) in tocItems"
            :key="index"
            :href="'#' + item.id"
            :class="['toc-link', `toc-level-${item.level}`, { active: activeHeading === item.id }]"
            @click.prevent="scrollToHeading(item.id)"
          >
            {{ item.text }}
          </a>
        </nav>
      </aside>

      <!-- Main Content -->
      <div
        ref="contentRef"
        class="markdown-content"
        :style="{ fontSize: fontSize + 'px' }"
        v-html="renderedContent"
        @scroll="handleScroll"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import {
  SunIcon,
  MoonIcon,
  Bars3BottomLeftIcon,
  MinusIcon,
  PlusIcon,
} from '@heroicons/vue/24/outline'

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  fileName: {
    type: String,
    default: 'Markdown Document'
  },
  fileUrl: {
    type: String,
    default: ''
  }
})

// State
const contentRef = ref(null)
const isDarkMode = ref(false)
const showToc = ref(false)
const fontSize = ref(16)
const activeHeading = ref('')
const tocItems = ref([])

// Configure marked with syntax highlighting
marked.setOptions({
  breaks: true,
  gfm: true
})

// Custom renderer for headings to add IDs
const renderer = new marked.Renderer()
renderer.heading = function(data) {
  // Handle both old and new marked API
  const text = typeof data === 'object' ? data.text : data
  const depth = typeof data === 'object' ? data.depth : arguments[1]
  const id = String(text).toLowerCase().replace(/[^\w]+/g, '-')
  return `<h${depth} id="${id}" class="heading-anchor">${text}</h${depth}>`
}

// Custom code renderer with syntax highlighting
renderer.code = function(data) {
  const code = typeof data === 'object' ? data.text : data
  const lang = typeof data === 'object' ? data.lang : arguments[1]

  if (lang && hljs.getLanguage(lang)) {
    try {
      const highlighted = hljs.highlight(code, { language: lang }).value
      return `<pre><code class="hljs language-${lang}">${highlighted}</code></pre>`
    } catch (err) {
      console.error('Highlight error:', err)
    }
  }
  const autoHighlighted = hljs.highlightAuto(code).value
  return `<pre><code class="hljs">${autoHighlighted}</code></pre>`
}

marked.use({ renderer })

// Computed
const renderedContent = computed(() => {
  if (!props.content) return ''
  return marked.parse(props.content)
})

// Extract TOC from content
const extractToc = () => {
  const headingRegex = /^(#{1,6})\s+(.+)$/gm
  const items = []
  let match

  while ((match = headingRegex.exec(props.content)) !== null) {
    const level = match[1].length
    const text = match[2].trim()
    const id = text.toLowerCase().replace(/[^\w]+/g, '-')
    items.push({ level, text, id })
  }

  tocItems.value = items
}

// Methods
const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
}

const toggleToc = () => {
  showToc.value = !showToc.value
}

const increaseFontSize = () => {
  if (fontSize.value < 24) fontSize.value += 2
}

const decreaseFontSize = () => {
  if (fontSize.value > 12) fontSize.value -= 2
}

const scrollToHeading = (id) => {
  const element = document.getElementById(id)
  if (element && contentRef.value) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    activeHeading.value = id
  }
}

const handleScroll = () => {
  if (!contentRef.value) return

  // Update active heading based on scroll position
  const headings = contentRef.value.querySelectorAll('[id]')
  for (let i = headings.length - 1; i >= 0; i--) {
    const heading = headings[i]
    if (heading.getBoundingClientRect().top <= 100) {
      activeHeading.value = heading.id
      break
    }
  }
}

// Lifecycle
onMounted(() => {
  extractToc()
})

watch(() => props.content, () => {
  extractToc()
})
</script>

<style scoped>
.markdown-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f8fafc;
  color: #1e293b;
}

.markdown-viewer.dark-mode {
  background: #1e293b;
  color: #e2e8f0;
}

/* Toolbar */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.dark-mode .toolbar {
  background: rgba(30, 41, 59, 0.9);
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.375rem;
  border-radius: 0.375rem;
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s ease;
}

.toolbar-btn:hover {
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
}

.toolbar-btn.active {
  background: rgba(99, 102, 241, 0.15);
  color: #6366f1;
}

.dark-mode .toolbar-btn {
  color: #94a3b8;
}

.dark-mode .toolbar-btn:hover {
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
}

.font-size-display {
  font-size: 0.75rem;
  color: #64748b;
  min-width: 2.5rem;
  text-align: center;
}

.dark-mode .font-size-display {
  color: #94a3b8;
}

/* Content Wrapper */
.content-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* TOC Sidebar */
.toc-sidebar {
  width: 220px;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.5);
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  flex-shrink: 0;
}

.dark-mode .toc-sidebar {
  background: rgba(30, 41, 59, 0.5);
  border-right-color: rgba(255, 255, 255, 0.1);
}

.toc-title {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  margin-bottom: 0.75rem;
}

.dark-mode .toc-title {
  color: #94a3b8;
}

.toc-nav {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.toc-link {
  display: block;
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
  color: #475569;
  text-decoration: none;
  border-radius: 0.25rem;
  border-left: 2px solid transparent;
  transition: all 0.15s ease;
}

.toc-link:hover {
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
  border-left-color: #6366f1;
}

.toc-link.active {
  background: rgba(99, 102, 241, 0.15);
  color: #6366f1;
  border-left-color: #6366f1;
}

.dark-mode .toc-link {
  color: #94a3b8;
}

.dark-mode .toc-link:hover,
.dark-mode .toc-link.active {
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
  border-left-color: #818cf8;
}

.toc-level-1 { padding-left: 0.5rem; }
.toc-level-2 { padding-left: 1rem; }
.toc-level-3 { padding-left: 1.5rem; }
.toc-level-4 { padding-left: 2rem; }
.toc-level-5 { padding-left: 2.5rem; }
.toc-level-6 { padding-left: 3rem; }

/* Main Content */
.markdown-content {
  flex: 1;
  padding: 1.5rem 2rem;
  overflow-y: auto;
  scroll-behavior: smooth;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  color: #1e293b;
  font-weight: 600;
  line-height: 1.3;
  margin-top: 1.25em;
  margin-bottom: 0.5em;
  scroll-margin-top: 1rem;
}

.dark-mode .markdown-content :deep(h1),
.dark-mode .markdown-content :deep(h2),
.dark-mode .markdown-content :deep(h3),
.dark-mode .markdown-content :deep(h4),
.dark-mode .markdown-content :deep(h5),
.dark-mode .markdown-content :deep(h6) {
  color: #f1f5f9;
}

.markdown-content :deep(h1) { font-size: 2em; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.3rem; }
.markdown-content :deep(h2) { font-size: 1.5em; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.25rem; }
.markdown-content :deep(h3) { font-size: 1.25em; }
.markdown-content :deep(h4) { font-size: 1.1em; }

.dark-mode .markdown-content :deep(h1),
.dark-mode .markdown-content :deep(h2) {
  border-bottom-color: #334155;
}

.markdown-content :deep(p) {
  margin-bottom: 0.75em;
  line-height: 1.7;
}

.markdown-content :deep(a) {
  color: #6366f1;
  text-decoration: none;
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}

.dark-mode .markdown-content :deep(a) {
  color: #818cf8;
}

.markdown-content :deep(code) {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.875em;
  background: rgba(99, 102, 241, 0.1);
  padding: 0.125em 0.25em;
  border-radius: 0.25rem;
  color: #6366f1;
}

.dark-mode .markdown-content :deep(code) {
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
}

.markdown-content :deep(pre) {
  background: #1e293b;
  border-radius: 0.5rem;
  padding: 1rem;
  overflow-x: auto;
  margin: 1rem 0;
}

.markdown-content :deep(pre code) {
  background: transparent;
  padding: 0;
  color: #e2e8f0;
  font-size: 0.85rem;
  line-height: 1.6;
}

.markdown-content :deep(blockquote) {
  border-left: 3px solid #6366f1;
  margin: 1rem 0;
  padding: 0.5rem 1rem;
  background: rgba(99, 102, 241, 0.05);
  color: #475569;
}

.dark-mode .markdown-content :deep(blockquote) {
  background: rgba(99, 102, 241, 0.1);
  color: #94a3b8;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 0.75rem 0;
  padding-left: 1.5rem;
}

.markdown-content :deep(li) {
  margin: 0.25rem 0;
  line-height: 1.6;
}

.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  padding: 0.5rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.markdown-content :deep(th) {
  background: rgba(99, 102, 241, 0.1);
  font-weight: 600;
}

.dark-mode .markdown-content :deep(th),
.dark-mode .markdown-content :deep(td) {
  border-bottom-color: #334155;
}

.dark-mode .markdown-content :deep(th) {
  background: rgba(99, 102, 241, 0.2);
}

.markdown-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 0.5rem;
  margin: 1rem 0;
}

.markdown-content :deep(hr) {
  border: none;
  height: 1px;
  background: #e2e8f0;
  margin: 1.5rem 0;
}

.dark-mode .markdown-content :deep(hr) {
  background: #334155;
}
</style>
