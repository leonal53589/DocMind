import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Items
export const getItems = (params) => api.get('/items/', { params })
export const getItem = (id) => api.get(`/items/${id}`)
export const createItem = (data) => api.post('/items/', data)
export const updateItem = (id, data) => api.put(`/items/${id}`, data)
export const deleteItem = (id) => api.delete(`/items/${id}`)
export const getAISummary = (id) => api.post(`/items/${id}/ai-summary`, null, { timeout: 120000 })

// Favorites
export const toggleFavorite = (id) => api.post(`/items/${id}/favorite`)
export const getFavorites = (params) => api.get('/items/', { params: { ...params, favorites_only: true } })

// Associations
export const addAssociation = (id, associatedItemId) => api.post(`/items/${id}/associations`, { associated_item_id: associatedItemId })
export const removeAssociation = (id, associatedItemId) => api.delete(`/items/${id}/associations/${associatedItemId}`)
export const getAssociations = (id) => api.get(`/items/${id}/associations`)

// Categories
export const getCategories = () => api.get('/categories/')
export const getCategoryTree = () => api.get('/categories/tree')
export const createCategory = (data) => api.post('/categories/', data)
export const updateCategory = (id, data) => api.put(`/categories/${id}`, data)
export const deleteCategory = (id) => api.delete(`/categories/${id}`)

// Import
export const importFile = (formData) => api.post('/import/file', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const importUrl = (url, categoryId, autoClassify = true) => api.post('/import/url', null, {
  params: { url, category_id: categoryId, auto_classify: autoClassify }
})
export const importPath = (data) => api.post('/import/path', data)
export const reclassifyItem = (id) => api.post(`/import/${id}/reclassify`)

// Search
export const searchItems = (params) => api.get('/search/', { params })
export const getItemsByCategory = (limit = 5) => api.get('/search/by-category', { params: { limit_per_category: limit } })

// Stats
export const getStats = () => api.get('/stats')
export const healthCheck = () => api.get('/health')

export default api
