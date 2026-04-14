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

const copyInstall = () => {
  navigator.clipboard.writeText(installCommand.value)
}

const goToDetail = () => {
  router.push(`/plugins/${props.plugin.name}`)
}
</script>

<template>
  <div class="plugin-card" @click="goToDetail">
    <!-- Header -->
    <div class="card-header">
      <div class="plugin-name">
        <span class="name-text">{{ plugin.name }}</span>
        <span class="version-tag">v{{ plugin.version }}</span>
      </div>
      <div class="plugin-rating">
        <RatingStars :rating="plugin.average_rating" :count="plugin.total_ratings" />
      </div>
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
        <span class="author-avatar">👤</span>
        <span class="author-name">{{ plugin.author?.name || '未知' }}</span>
      </div>
      <button class="install-btn" @click.stop="copyInstall">
        <span class="btn-icon">📋</span>
        <span class="btn-text">复制安装命令</span>
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
  padding: var(--space-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.plugin-card:hover {
  background: var(--color-card-hover);
  border-color: var(--color-border);
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
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-md);
}

.plugin-name {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.name-text {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--color-text);
}

.version-tag {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-primary);
  background: var(--color-primary-muted);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.card-body {
  margin-bottom: var(--space-md);
}

.plugin-description {
  font-family: var(--font-body);
  font-size: 15px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.card-tags {
  display: flex;
  gap: var(--space-xs);
  margin-bottom: var(--space-md);
}

.tag {
  font-family: var(--font-display);
  font-size: 11px;
  color: var(--color-text-muted);
  background: var(--color-bg);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border-subtle);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plugin-author {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.author-avatar {
  font-size: 14px;
}

.author-name {
  font-size: 13px;
  color: var(--color-text-muted);
}

.install-btn {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  background: transparent;
  border: 1px solid var(--color-primary);
  color: var(--color-primary);
  font-family: var(--font-display);
  font-size: 12px;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.install-btn:hover {
  background: var(--color-primary);
  color: var(--color-bg);
}

.btn-icon {
  font-size: 12px;
}
</style>