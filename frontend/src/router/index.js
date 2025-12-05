import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Browse from '../views/Browse.vue'
import Search from '../views/Search.vue'
import Settings from '../views/Settings.vue'

const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: Dashboard
  },
  {
    path: '/browse',
    name: 'browse',
    component: Browse
  },
  {
    path: '/browse/:categoryId',
    name: 'browse-category',
    component: Browse
  },
  {
    path: '/search',
    name: 'search',
    component: Search
  },
  {
    path: '/settings',
    name: 'settings',
    component: Settings
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
