<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from './stores'

const store = useAppStore()
const route = useRoute()
const router = useRouter()

// Mock user for development (in production, this would come from SSO)
const mockUserEmail = ref('developer@company.com')
const mockUserName = ref('开发者')

// Navigation items
const navItems = [
  {
    path: '/plugins',
    label: '插件浏览',
    icon: ['polygon', { points: '13 2 3 14 12 14 11 22 21 10 12 10 13 2' }]
  },
  {
    path: '/submit',
    label: '提交插件',
    icon: ['path', { d: 'M12 20h9' }, ['path', { d: 'M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z' }]]
  },
  {
    path: '/my-submissions',
    label: '我的提交',
    icon: ['path', { d: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z' }, ['polyline', { points: '14 2 14 8 20 8' }], ['line', { x1: 16, y1: 13, x2: 8, y2: 13 }], ['line', { x1: 16, y1: 17, x2: 8, y2: 17 }]]
  },
]

const adminNavItems = [
  {
    path: '/admin/reviews',
    label: '审核管理',
    icon: ['circle', { cx: 12, cy: 12, r: 10 }, ['polyline', { points: '12 6 12 12 16 14' }]],
    badge: true
  },
  {
    path: '/admin/stats',
    label: '统计分析',
    icon: ['line', { x1: 12, y1: 20, x2: 12, y2: 10 }, ['line', { x1: 18, y1: 20, x2: 18, y2: 4 }], ['line', { x1: 6, y1: 20, x2: 6, y2: 16 }]]
  },
]

const sidebarCollapsed = ref(false)
const currentPath = computed(() => route.path)

// Toggle admin mode for testing
const toggleAdmin = () => {
  store.setUser(mockUserEmail.value, mockUserName.value, !store.isAdmin)
  if (store.isAdmin) {
    store.fetchPendingCount()
  }
}

onMounted(() => {
  store.setUser(mockUserEmail.value, mockUserName.value, true)
  store.fetchStats()
  store.fetchPendingCount()
})

const navigate = (path) => {
  router.push(path)
}

// Render SVG elements from our icon definitions
const renderIcon = (def) => {
  // This is handled in the template with v-for
  return def
}
</script>

<template>
  <div class="app-container">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <!-- Logo -->
      <div class="sidebar-header">
        <div class="logo">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
          </div>
          <span class="logo-text" v-if="!sidebarCollapsed">插件市场</span>
        </div>
        <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed" :aria-label="sidebarCollapsed ? '展开侧栏' : '收起侧栏'">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <polyline v-if="!sidebarCollapsed" points="15 18 9 12 15 6" />
            <polyline v-else points="9 18 15 12 9 6" />
          </svg>
        </button>
      </div>

      <!-- Quick stats -->
      <div class="sidebar-stats" v-if="!sidebarCollapsed && store.stats">
        <div class="stat-item">
          <span class="stat-value">{{ store.stats.plugins_count }}</span>
          <span class="stat-label">插件</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ store.stats.pending_reviews }}</span>
          <span class="stat-label">待审核</span>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="sidebar-nav">
        <div class="nav-section">
          <span class="nav-section-title" v-if="!sidebarCollapsed">导航</span>
          <ul class="nav-list">
            <li
              v-for="item in navItems"
              :key="item.path"
              :class="['nav-item', { active: currentPath === item.path }]"
              @click="navigate(item.path)"
            >
              <span class="nav-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polygon v-if="item.icon[0] === 'polygon'" :points="item.icon[1].points" />
                  <template v-if="item.icon[0] === 'path'">
                    <path :d="item.icon[1].d" />
                    <path :d="item.icon[2][1].d" />
                  </template>
                  <template v-if="item.icon[0] === 'path' && item.icon[0] === 'path'">
                    <path :d="item.icon[1].d" />
                  </template>
                  <path v-if="item.icon[0] === 'path'" :d="item.icon[1].d" />
                  <template v-if="item.path === '/submit'">
                    <path d="M12 20h9" />
                    <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                  </template>
                  <template v-if="item.path === '/my-submissions'">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                    <line x1="16" y1="13" x2="8" y2="13" />
                    <line x1="16" y1="17" x2="8" y2="17" />
                  </template>
                  <template v-if="item.path === '/plugins'">
                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                  </template>
                </svg>
              </span>
              <span class="nav-label" v-if="!sidebarCollapsed">{{ item.label }}</span>
            </li>
          </ul>
        </div>

        <!-- Admin section -->
        <div class="nav-section admin-section" v-if="store.isAdmin">
          <span class="nav-section-title" v-if="!sidebarCollapsed">管理员</span>
          <ul class="nav-list">
            <li
              v-for="item in adminNavItems"
              :key="item.path"
              :class="['nav-item', { active: currentPath === item.path }]"
              @click="navigate(item.path)"
            >
              <span class="nav-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <template v-if="item.path === '/admin/reviews'">
                    <circle cx="12" cy="12" r="10" />
                    <polyline points="12 6 12 12 16 14" />
                  </template>
                  <template v-if="item.path === '/admin/stats'">
                    <line x1="12" y1="20" x2="12" y2="10" />
                    <line x1="18" y1="20" x2="18" y2="4" />
                    <line x1="6" y1="20" x2="6" y2="16" />
                  </template>
                </svg>
              </span>
              <span class="nav-label" v-if="!sidebarCollapsed">{{ item.label }}</span>
              <span class="nav-badge" v-if="item.badge && store.pendingCount > 0">
                {{ store.pendingCount }}
              </span>
            </li>
          </ul>
        </div>
      </nav>

      <!-- User section -->
      <div class="sidebar-footer">
        <div class="user-info" v-if="!sidebarCollapsed">
          <span class="user-name">{{ store.userName }}</span>
          <span class="user-role" :class="{ admin: store.isAdmin }">
            {{ store.isAdmin ? '管理员' : '用户' }}
          </span>
        </div>
        <button class="admin-toggle" @click="toggleAdmin" :title="store.isAdmin ? '切换为用户' : '切换为管理员'">
          <svg v-if="store.isAdmin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <main class="main-content" :class="{ expanded: sidebarCollapsed }">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 240px;
  background: var(--color-bg-subtle);
  border-right: 1px solid var(--color-border-subtle);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  padding: var(--space-4) var(--space-5);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--color-border-subtle);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.logo-icon {
  width: 28px;
  height: 28px;
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon svg {
  width: 24px;
  height: 24px;
}

.logo-text {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 500;
  color: var(--color-primary);
}

.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--color-text-dim);
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.collapse-btn:hover {
  color: var(--color-primary);
  background: var(--color-primary-muted);
}

.sidebar-stats {
  padding: var(--space-4);
  display: flex;
  justify-content: space-around;
  border-bottom: 1px solid var(--color-border-subtle);
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 500;
  color: var(--color-primary);
  display: block;
}

.stat-label {
  font-size: 11px;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-3);
}

.nav-section {
  margin-bottom: var(--space-4);
}

.nav-section-title {
  display: block;
  font-family: var(--font-display);
  font-size: 10px;
  color: var(--color-text-dim);
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: var(--space-2) var(--space-2) var(--space-1);
}

.nav-list {
  list-style: none;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--color-text-secondary);
  margin-bottom: 2px;
}

.nav-item:hover {
  background: var(--color-card);
  color: var(--color-text);
}

.nav-item.active {
  background: var(--color-primary-muted);
  color: var(--color-primary);
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nav-icon svg {
  width: 18px;
  height: 18px;
}

.nav-label {
  font-size: 14px;
}

.nav-badge {
  background: var(--color-warning);
  color: #1A1A1F;
  font-family: var(--font-display);
  font-size: 10px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: var(--radius-full);
  margin-left: auto;
  line-height: 1.2;
  min-width: 18px;
  text-align: center;
}

.sidebar-footer {
  padding: var(--space-3);
  border-top: 1px solid var(--color-border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.user-name {
  font-size: 13px;
  color: var(--color-text);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 11px;
  color: var(--color-text-dim);
}

.user-role.admin {
  color: var(--color-primary);
}

.admin-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-1) var(--space-2);
  cursor: pointer;
  color: var(--color-text-muted);
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.admin-toggle:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-muted);
}

.main-content {
  flex: 1;
  margin-left: 240px;
  padding: var(--space-8);
  transition: margin-left var(--transition-normal);
  min-height: 100vh;
}

.main-content.expanded {
  margin-left: 64px;
}

/* Page transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-fast);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    width: 64px;
  }

  .main-content {
    margin-left: 64px;
    padding: var(--space-4);
  }
}
</style>
