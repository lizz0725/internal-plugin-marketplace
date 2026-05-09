<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from './stores'

const store = useAppStore()
const route = useRoute()
const router = useRouter()

// Navigation items
const navItems = [
  {
    path: '/plugins',
    label: '插件浏览',
    icon: ['polygon', { points: '13 2 3 14 12 14 11 22 21 10 12 10 13 2' }]
  },
]

const adminNavItems = [
  {
    path: '/admin/sync',
    label: '同步面板',
    icon: ['circle', { cx: 12, cy: 12, r: 10 }, ['polyline', { points: '12 6 12 12 16 14' }]],
  },
  {
    path: '/admin/stats',
    label: '统计分析',
    icon: ['line', { x1: 12, y1: 20, x2: 12, y2: 10 }, ['line', { x1: 18, y1: 20, x2: 18, y2: 4 }], ['line', { x1: 6, y1: 20, x2: 6, y2: 16 }]]
  },
]

const sidebarCollapsed = ref(false)
const currentPath = computed(() => route.path)

onMounted(() => {
  store.fetchStats()
})

const navigate = (path) => {
  router.push(path)
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
                  <circle v-if="item.path === '/admin/sync'" cx="12" cy="12" r="10" />
                  <polyline v-if="item.path === '/admin/sync'" points="12 6 12 12 16 14" />
                  <template v-if="item.path === '/admin/stats'">
                    <line x1="12" y1="20" x2="12" y2="10" />
                    <line x1="18" y1="20" x2="18" y2="4" />
                    <line x1="6" y1="20" x2="6" y2="16" />
                  </template>
                </svg>
              </span>
              <span class="nav-label" v-if="!sidebarCollapsed">{{ item.label }}</span>
            </li>
          </ul>
        </div>
      </nav>

      <!-- User section -->
      <div class="sidebar-footer" v-if="!sidebarCollapsed">
        <div class="user-info">
          <span class="user-name">{{ store.userName || '用户' }}</span>
        </div>
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
