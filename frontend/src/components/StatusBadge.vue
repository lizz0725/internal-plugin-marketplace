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
  pending: { label: '待审核', icon: '⏳', class: 'pending' },
  approved: { label: '已通过', icon: '✓', class: 'approved' },
  rejected: { label: '已拒绝', icon: '✕', class: 'rejected' }
}

const config = computed(() => statusConfig[props.status])
</script>

<template>
  <span :class="['status-badge', config.class, `size-${size}`]">
    <span class="badge-icon">{{ config.icon }}</span>
    <span class="badge-label">{{ config.label }}</span>
  </span>
</template>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: var(--font-display);
  border-radius: var(--radius-sm);
}

.size-sm {
  font-size: 11px;
  padding: 2px 6px;
}

.size-md {
  font-size: 12px;
  padding: 4px 10px;
}

.size-lg {
  font-size: 14px;
  padding: 6px 12px;
}

.pending {
  background: rgba(229, 165, 59, 0.2);
  color: var(--color-warning);
}

.approved {
  background: rgba(124, 184, 124, 0.2);
  color: var(--color-success);
}

.rejected {
  background: rgba(212, 95, 95, 0.2);
  color: var(--color-error);
}

.badge-icon {
  font-size: 10px;
}
</style>