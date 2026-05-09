<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import RatingStars from './RatingStars.vue'

const props = defineProps({
  plugin: {
    type: Object,
    required: true
  }
})

const router = useRouter()

const installCommand = computed(() => {
  return `/plugin install ${props.plugin.name}@internal`
})

const copyInstall = (e) => {
  e.stopPropagation()
  navigator.clipboard.writeText(installCommand.value)
}

const goToDetail = () => {
  router.push(`/plugins/${props.plugin.name}`)
}

const pluginInitial = computed(() => {
  return props.plugin.name?.charAt(0).toUpperCase() || 'P'
})
</script>

<template>
  <div class="plugin-card" @click="goToDetail">
    <!-- Header -->
    <div class="card-header">
      <div class="card-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 6v6l4 2" />
        </svg>
      </div>
      <div class="card-rating">
        <RatingStars :rating="plugin.average_rating" :count="plugin.total_ratings" />
      </div>
    </div>

    <!-- Name & version -->
    <div class="card-title-row">
      <span class="name-text">{{ plugin.name }}</span>
      <span class="version-tag">v{{ plugin.version }}</span>
    </div>

    <!-- Description -->
    <div class="card-body">
      <p class="plugin-description">{{ plugin.description }}</p>
    </div>

    <!-- Tags -->
    <div class="card-tags" v-if="plugin.keywords?.length">
      <span class="tag" v-for="keyword in plugin.keywords.slice(0, 3)" :key="keyword">
        {{ keyword }}
      </span>
    </div>

    <!-- Footer -->
    <div class="card-footer">
      <div class="plugin-author">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="author-icon">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </svg>
        <span class="author-name">{{ plugin.author?.name || '未知' }}</span>
      </div>
      <button class="install-btn" @click="copyInstall" title="复制安装命令">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="install-icon">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
        </svg>
        <span class="install-text">复制安装</span>
      </button>
    </div>

    <!-- Decorative corner -->
    <div class="card-corner"></div>
  </div>
</template>

<style scoped>
.plugin-card {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.plugin-card:hover {
  background: var(--color-card-hover);
  border-color: var(--color-border-active);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.card-corner {
  position: absolute;
  top: 0;
  right: 0;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, transparent 50%, var(--color-primary-muted) 50%);
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.plugin-card:hover .card-corner {
  opacity: 1;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--color-primary-muted);
  border: 1px solid var(--color-border-active);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  flex-shrink: 0;
}

.card-icon svg {
  width: 20px;
  height: 20px;
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.name-text {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text);
}

.version-tag {
  font-family: var(--font-display);
  font-size: 11px;
  color: var(--color-primary);
  background: var(--color-primary-muted);
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.card-body {
  margin-bottom: var(--space-3);
}

.plugin-description {
  font-size: 13px;
  color: var(--color-text-muted);
  line-height: 1.5;

  /* Clamp to 2 lines */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-tags {
  display: flex;
  gap: var(--space-1);
  margin-bottom: var(--space-3);
}

.tag {
  font-family: var(--font-display);
  font-size: 10px;
  color: var(--color-text-dim);
  background: var(--color-bg-subtle);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border-subtle);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border-subtle);
}

.plugin-author {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.author-icon {
  width: 14px;
  height: 14px;
  color: var(--color-text-dim);
}

.author-name {
  font-size: 12px;
  color: var(--color-text-dim);
}

.install-btn {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  background: transparent;
  border: none;
  color: var(--color-text-dim);
  font-family: var(--font-display);
  font-size: 11px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.install-btn:hover {
  color: var(--color-primary);
  background: var(--color-primary-muted);
}

.install-icon {
  width: 14px;
  height: 14px;
}
</style>
