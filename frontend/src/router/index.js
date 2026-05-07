import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/plugins'
  },
  {
    path: '/plugins',
    name: 'PluginsList',
    component: () => import('../views/PluginsList.vue'),
    meta: { title: '插件浏览' }
  },
  {
    path: '/plugins/:name',
    name: 'PluginDetail',
    component: () => import('../views/PluginDetail.vue'),
    meta: { title: '插件详情' }
  },
  {
    path: '/admin/sync',
    name: 'AdminSync',
    component: () => import('../views/AdminSync.vue'),
    meta: { title: '同步面板', admin: true }
  },
  {
    path: '/admin/stats',
    name: 'AdminStats',
    component: () => import('../views/AdminStats.vue'),
    meta: { title: '统计分析', admin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Update document title on route change
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 插件市场` : '插件市场'
  next()
})

export default router
