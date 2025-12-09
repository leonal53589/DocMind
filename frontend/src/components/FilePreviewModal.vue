<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="preview-modal-overlay"
      @click.self="close"
      @keydown.esc="close"
    >
      <div class="preview-modal" :class="{ 'fullscreen': isFullscreen }">
        <!-- Modal Header -->
        <header class="modal-header">
          <div class="header-left">
            <div class="file-icon" :class="fileTypeClass">
              <component :is="fileIcon" class="w-5 h-5" />
            </div>
            <div class="file-info">
              <h2 class="file-title">{{ item?.title || 'Preview' }}</h2>
              <span class="file-meta">{{ fileMeta }}</span>
            </div>
          </div>
          <div class="header-actions">
            <button
              @click="toggleFullscreen"
              class="action-btn"
              :title="isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'"
              type="button"
            >
              <ArrowsPointingOutIcon v-if="!isFullscreen" class="w-5 h-5" />
              <ArrowsPointingInIcon v-else class="w-5 h-5" />
            </button>
            <a
              v-if="item?.file_path"
              :href="fileUrl"
              target="_blank"
              class="action-btn"
              title="Open in New Tab"
            >
              <ArrowTopRightOnSquareIcon class="w-5 h-5" />
            </a>
            <button
              @click.stop="close"
              class="action-btn close-btn"
              title="Close (Esc)"
              type="button"
            >
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
        </header>

          <!-- Modal Content -->
          <div class="modal-content" ref="contentRef">
            <!-- Loading State -->
            <div v-if="isLoading" class="loading-container">
              <div class="loading-spinner">
                <div class="spinner-ring"></div>
                <div class="spinner-ring"></div>
                <div class="spinner-ring"></div>
              </div>
              <p class="loading-text">Loading preview...</p>
            </div>

            <!-- Error State -->
            <div v-else-if="error" class="error-container">
              <ExclamationTriangleIcon class="w-16 h-16 text-amber-500" />
              <h3 class="error-title">Preview Unavailable</h3>
              <p class="error-message">{{ error }}</p>
              <a
                v-if="item?.file_path"
                :href="fileUrl"
                target="_blank"
                class="download-btn"
              >
                <ArrowDownTrayIcon class="w-5 h-5" />
                Download File
              </a>
            </div>

            <!-- Markdown Preview -->
            <MarkdownViewer
              v-else-if="isMarkdown && content"
              :content="content"
              :fileName="item?.title || 'document.md'"
              :fileUrl="fileUrl"
            />

            <!-- Image Preview -->
            <div v-else-if="isImage" class="image-preview">
              <img
                :src="fileUrl"
                :alt="item?.title"
                class="preview-image"
                @load="onImageLoad"
                @error="onImageError"
              />
            </div>

            <!-- PDF Preview -->
            <div v-else-if="isPdf" class="pdf-preview">
              <iframe
                :src="fileUrl"
                class="pdf-iframe"
                frameborder="0"
              ></iframe>
            </div>

            <!-- Video Preview -->
            <div v-else-if="isVideo" class="video-preview">
              <video
                :src="fileUrl"
                controls
                class="preview-video"
              >
                Your browser does not support video playback.
              </video>
            </div>

            <!-- Audio Preview -->
            <div v-else-if="isAudio" class="audio-preview">
              <div class="audio-visualization">
                <div class="audio-icon-bg">
                  <MusicalNoteIcon class="w-16 h-16 text-indigo-500" />
                </div>
                <h3 class="audio-title">{{ item?.title }}</h3>
              </div>
              <audio
                :src="fileUrl"
                controls
                class="preview-audio"
              >
                Your browser does not support audio playback.
              </audio>
            </div>

            <!-- Code Preview -->
            <div v-else-if="isCode && content" class="code-preview">
              <pre class="code-block"><code v-html="highlightedCode"></code></pre>
            </div>

            <!-- Plain Text Preview -->
            <div v-else-if="isText && content" class="text-preview">
              <pre class="text-content">{{ content }}</pre>
            </div>

            <!-- Unsupported File Type -->
            <div v-else class="unsupported-preview">
              <DocumentIcon class="w-24 h-24 text-gray-400" />
              <h3 class="unsupported-title">Preview Not Available</h3>
              <p class="unsupported-message">
                This file type cannot be previewed in the browser.
              </p>
              <a
                v-if="item?.file_path"
                :href="fileUrl"
                target="_blank"
                class="download-btn"
              >
                <ArrowDownTrayIcon class="w-5 h-5" />
                Download File
              </a>
            </div>
          </div>

          <!-- Modal Footer -->
          <footer v-if="item" class="modal-footer">
            <div class="footer-info">
              <span v-if="item.category" class="category-badge">
                {{ item.category.name }}
              </span>
              <span v-if="item.file_size" class="file-size">
                {{ formatFileSize(item.file_size) }}
              </span>
              <span v-if="item.created_at" class="created-date">
                {{ formatDate(item.created_at) }}
              </span>
            </div>
            <div class="footer-tags" v-if="item.tags?.length">
              <span
                v-for="tag in item.tags"
                :key="tag.id"
                class="tag-badge"
              >
                #{{ tag.name }}
              </span>
            </div>
          </footer>
        </div>
      </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import MarkdownViewer from './MarkdownViewer.vue'
import {
  XMarkIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon,
  ArrowTopRightOnSquareIcon,
  ArrowDownTrayIcon,
  ExclamationTriangleIcon,
  DocumentIcon,
  DocumentTextIcon,
  PhotoIcon,
  FilmIcon,
  MusicalNoteIcon,
  CodeBracketIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  item: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

// State
const isLoading = ref(false)
const error = ref(null)
const content = ref('')
const isFullscreen = ref(false)
const contentRef = ref(null)

// API base URL
const API_BASE = 'http://localhost:8000'

// Computed
const fileUrl = computed(() => {
  if (!props.item?.file_path) return ''
  return `${API_BASE}/files/${props.item.file_path}`
})

const mimeType = computed(() => props.item?.mime_type || '')

const isMarkdown = computed(() => {
  const path = props.item?.file_path?.toLowerCase() || ''
  return path.endsWith('.md') || path.endsWith('.markdown')
})

const isImage = computed(() => mimeType.value.startsWith('image/'))

const isPdf = computed(() => mimeType.value === 'application/pdf')

const isVideo = computed(() => mimeType.value.startsWith('video/'))

const isAudio = computed(() => mimeType.value.startsWith('audio/'))

const isCode = computed(() => {
  const path = props.item?.file_path?.toLowerCase() || ''
  const codeExtensions = [
    '.js', '.ts', '.jsx', '.tsx', '.vue', '.py', '.java', '.c', '.cpp',
    '.h', '.hpp', '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt',
    '.scala', '.sh', '.bash', '.zsh', '.ps1', '.sql', '.json', '.xml',
    '.yaml', '.yml', '.toml', '.ini', '.css', '.scss', '.less', '.html'
  ]
  return codeExtensions.some(ext => path.endsWith(ext))
})

const isText = computed(() => {
  return mimeType.value.startsWith('text/') ||
         props.item?.file_path?.toLowerCase().endsWith('.txt')
})

const fileTypeClass = computed(() => {
  if (isMarkdown.value) return 'markdown'
  if (isImage.value) return 'image'
  if (isPdf.value) return 'pdf'
  if (isVideo.value) return 'video'
  if (isAudio.value) return 'audio'
  if (isCode.value) return 'code'
  if (isText.value) return 'text'
  return 'default'
})

const fileIcon = computed(() => {
  if (isImage.value) return PhotoIcon
  if (isVideo.value) return FilmIcon
  if (isAudio.value) return MusicalNoteIcon
  if (isCode.value) return CodeBracketIcon
  return DocumentTextIcon
})

const fileMeta = computed(() => {
  const parts = []
  if (props.item?.mime_type) parts.push(props.item.mime_type)
  if (props.item?.file_size) parts.push(formatFileSize(props.item.file_size))
  return parts.join(' • ')
})

const highlightedCode = computed(() => {
  if (!content.value) return ''
  const path = props.item?.file_path?.toLowerCase() || ''
  const ext = path.split('.').pop()
  const langMap = {
    js: 'javascript', ts: 'typescript', jsx: 'javascript', tsx: 'typescript',
    py: 'python', rb: 'ruby', sh: 'bash', yml: 'yaml', md: 'markdown'
  }
  const lang = langMap[ext] || ext

  try {
    if (hljs.getLanguage(lang)) {
      return hljs.highlight(content.value, { language: lang }).value
    }
    return hljs.highlightAuto(content.value).value
  } catch {
    return content.value
  }
})

// Methods
const close = () => {
  isFullscreen.value = false
  document.body.style.overflow = ''
  emit('close')
}

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

const formatFileSize = (bytes) => {
  if (!bytes) return ''
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const loadContent = async () => {
  if (!props.item?.file_path) return

  // Only load content for text-based files
  if (!isMarkdown.value && !isCode.value && !isText.value) return

  isLoading.value = true
  error.value = null
  content.value = ''

  try {
    const response = await fetch(fileUrl.value)
    if (!response.ok) {
      throw new Error(`Failed to load file: ${response.statusText}`)
    }
    content.value = await response.text()
  } catch (err) {
    console.error('Error loading file:', err)
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}

const onImageLoad = () => {
  isLoading.value = false
}

const onImageError = () => {
  error.value = 'Failed to load image'
  isLoading.value = false
}

// Keyboard shortcuts
const handleKeydown = (e) => {
  if (!props.isOpen) return

  if (e.key === 'Escape') {
    close()
  } else if (e.key === 'f' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    toggleFullscreen()
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

// Watch for item changes
watch(() => props.item, (newItem) => {
  if (newItem && props.isOpen) {
    loadContent()
  }
}, { immediate: true })

watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    document.body.style.overflow = 'hidden'
    loadContent()
  } else {
    document.body.style.overflow = ''
    content.value = ''
    error.value = null
  }
})
</script>

<style scoped>
/* Modal Overlay */
.preview-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.8);
  padding: 2rem;
}

/* Modal Container */
.preview-modal {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1200px;
  max-height: 90vh;
  background: #ffffff;
  border-radius: 1rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.preview-modal.fullscreen {
  max-width: 100%;
  max-height: 100%;
  border-radius: 0;
}

/* Modal Header */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 0;
}

.file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  flex-shrink: 0;
}

.file-icon.markdown { background: #6366f1; color: white; }
.file-icon.image { background: #ec4899; color: white; }
.file-icon.pdf { background: #ef4444; color: white; }
.file-icon.video { background: #8b5cf6; color: white; }
.file-icon.audio { background: #10b981; color: white; }
.file-icon.code { background: #3b82f6; color: white; }
.file-icon.text { background: #64748b; color: white; }
.file-icon.default { background: #6b7280; color: white; }

.file-info {
  min-width: 0;
}

.file-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  font-size: 0.75rem;
  color: #64748b;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.5rem;
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  text-decoration: none;
}

.action-btn:hover {
  background: #f1f5f9;
  color: #6366f1;
}

.action-btn.close-btn:hover {
  background: #fef2f2;
  color: #ef4444;
}

/* Modal Content */
.modal-content {
  flex: 1;
  overflow: auto;
  min-height: 0;
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
  padding: 3rem;
}

.loading-spinner {
  position: relative;
  width: 60px;
  height: 60px;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
}

.spinner-ring:nth-child(1) { animation-delay: -0.45s; }
.spinner-ring:nth-child(2) { animation-delay: -0.3s; border-top-color: #8b5cf6; }
.spinner-ring:nth-child(3) { animation-delay: -0.15s; border-top-color: #a855f7; }

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 1.5rem;
  color: #64748b;
  font-weight: 500;
}

/* Error State */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
  padding: 3rem;
  text-align: center;
}

.error-title {
  margin-top: 1.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
}

.error-message {
  margin-top: 0.5rem;
  color: #64748b;
}

/* Download Button */
.download-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding: 0.75rem 1.5rem;
  background: #6366f1;
  color: white;
  border-radius: 0.5rem;
  font-weight: 500;
  text-decoration: none;
}

.download-btn:hover {
  background: #4f46e5;
}

/* Image Preview */
.image-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 2rem;
  background: #0f172a;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 0.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
}

/* PDF Preview */
.pdf-preview {
  height: 100%;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

/* Video Preview */
.video-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 2rem;
  background: #0f172a;
}

.preview-video {
  max-width: 100%;
  max-height: 100%;
  border-radius: 0.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
}

/* Audio Preview */
.audio-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 3rem;
  background: #1e293b;
}

.audio-visualization {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
}

.audio-icon-bg {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 120px;
  background: rgba(99, 102, 241, 0.2);
  border-radius: 50%;
  margin-bottom: 1.5rem;
}

.audio-title {
  color: #e2e8f0;
  font-size: 1.25rem;
  font-weight: 600;
}

.preview-audio {
  width: 100%;
  max-width: 500px;
}

/* Code Preview */
.code-preview {
  height: 100%;
  overflow: auto;
}

.code-block {
  margin: 0;
  padding: 1.5rem;
  background: #1e293b;
  min-height: 100%;
  overflow: auto;
}

.code-block code {
  font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
  font-size: 0.875rem;
  line-height: 1.7;
  color: #e2e8f0;
}

/* Text Preview */
.text-preview {
  height: 100%;
  overflow: auto;
  padding: 2rem;
  background: #f8fafc;
}

.text-content {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 0.9375rem;
  line-height: 1.75;
  color: #334155;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* Unsupported Preview */
.unsupported-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
  padding: 3rem;
  text-align: center;
}

.unsupported-title {
  margin-top: 1.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
}

.unsupported-message {
  margin-top: 0.5rem;
  color: #64748b;
}

/* Modal Footer */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  background: #ffffff;
  border-top: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.footer-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.category-badge {
  display: inline-flex;
  padding: 0.25rem 0.75rem;
  background: #6366f1;
  color: white;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 9999px;
}

.file-size,
.created-date {
  font-size: 0.75rem;
  color: #64748b;
}

.footer-tags {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tag-badge {
  display: inline-flex;
  padding: 0.125rem 0.5rem;
  background: #eef2ff;
  color: #6366f1;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 0.25rem;
}
</style>
