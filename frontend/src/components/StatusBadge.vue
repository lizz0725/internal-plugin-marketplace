<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: (value) => ['pending', 'approved', 'rejected'].includes(value)
  },
  size: {
    type: String,
    default: 'md'
  }
})

const statusConfig = {
  pending: {
    label: '待审核',
    class: 'pending',
    icon: ['circle', { cx: 12, cy: 12, r: 10 }, ['polyline', { points: '12 6 12 12 16 14' }]]
  },
  approved: {
    label: '已上架',
    class: 'approved',
    icon: ['polyline', { points: '20 6 9 17 4 12' }]
  },
  rejected: {
    label: '已拒绝',
    class: 'rejected',
    icon: [
      ['line', { x1: 18, y1: 6, x2: 6, y2: 18 }],
      ['line', { x1: 6, y1: 6, x2: 18, y2: 18 }]
    ]
  }
}

const config = computed(() => statusConfig[props.status])
</script>

<template>
  <span :class="['badge', config.class, `size-${size}`]">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="badge-icon">
      <polyline v-if="config.icon.length && config.icon[0] === 'polyline'" :points="config.icon[1].points" />
      <circle v-if="config.icon.cx !== undefined" :cx="config.icon.cx" :cy="config.icon.cy" :r="config.icon.r" />
      <polyline v-if="config.icon[0]?.points" :points="config.icon[0].points" />
      <line v-if="config.icon[0]?.x1" :x1="config.icon[0].x1" :y1="config.icon[0].y1" :x2="config.icon[0].x2" :y2="config.icon[0].y2" />
      <line v-if="config.icon[1]?.x1" :x1="config.icon[1].x1" :y1="config.icon[1].y1" :x2="config.icon[1].x2" :y2="config.icon[1].y2" />
    </svg>
    <span class="badge-label">{{ config.label }}</span>
  </span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: var(--font-display);
  border-radius: var(--radius-full);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-icon {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
}

.size-sm {
  font-size: 10px;
  padding: 2px 6px;
}

.size-md {
  font-size: 11px;
  padding: 2px 8px;
}

.size-lg {
  font-size: 12px;
  padding: 4px 10px;
}

.pending {
  background: var(--color-warning-muted);
  color: var(--color-warning);
  border: 1px solid rgba(229, 165, 59, 0.2);
}

.approved {
  background: var(--color-success-muted);
  color: var(--color-success);
  border: 1px solid rgba(124, 184, 124, 0.2);
}

.rejected {
  background: var(--color-error-muted);
  color: var(--color-error);
  border: 1px solid rgba(212, 95, 95, 0.2);
}
</style>
