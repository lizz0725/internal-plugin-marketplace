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
  { path: '/plugins', label: '插件浏览', icon: '📦' },
  { path: '/submit', label: '提交插件', icon: '✨' },
  { path: '/my-submissions', label: '我的提交', icon: '📋' },
]

const adminNavItems = [
  { path: '/admin/reviews', label: '审核管理', icon: '⚖️', badge: true },
  { path: '/admin/stats', label: '统计分析', icon: '📊' },
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
  // Set mock user
  store.setUser(mockUserEmail.value, mockUserName.value, true) // Start as admin for testing
  store.fetchStats()
  store.fetchPendingCount()
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
          <span class="logo-icon">🔧</span>
          <span class="logo-text" v-if="!sidebarCollapsed">插件市场</span>
        </div>
        <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
          {{ sidebarCollapsed ? '→' : '←' }}
        </button>
      </div>

      <!-- Stats -->
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
              <span class="nav-icon">{{ item.icon }}</span>
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
              <span class="nav-icon">{{ item.icon }}</span>
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
          {{ store.isAdmin ? '👑' : '👤' }}
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <main class="main-content">
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
  padding: var(--space-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--color-border-subtle);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--color-primary);
}

.collapse-btn {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 12px;
  padding: var(--space-xs);
}

.collapse-btn:hover {
  color: var(--color-primary);
}

.sidebar-stats {
  padding: var(--space-md);
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
  color: var(--color-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-muted);
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-md);
}

.nav-section {
  margin-bottom: var(--space-lg);
}

.nav-section-title {
  font-family: var(--font-display);
  font-size: 11px;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: var(--space-sm);
}

.nav-list {
  list-style: none;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--color-text-secondary);
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
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.nav-label {
  font-size: 14px;
}

.nav-badge {
  background: var(--color-warning);
  color: var(--color-bg);
  font-family: var(--font-display);
  font-size: 11px;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  margin-left: auto;
}

.admin-section .nav-item.active {
  background: rgba(212, 165, 116, 0.1);
}

.sidebar-footer {
  padding: var(--space-md);
  border-top: 1px solid var(--color-border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  color: var(--color-text);
}

.user-role {
  font-size: 12px;
  color: var(--color-text-muted);
}

.user-role.admin {
  color: var(--color-primary);
}

.admin-toggle {
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-xs) var(--space-sm);
  cursor: pointer;
  font-size: 16px;
}

.admin-toggle:hover {
  border-color: var(--color-primary);
}

.main-content {
  flex: 1;
  margin-left: 240px;
  padding: var(--space-xl);
  transition: margin-left var(--transition-normal);
}

.sidebar.collapsed + .main-content {
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
    padding: var(--space-md);
  }
}
</style>