<script setup>
import { computed } from 'vue'

const props = defineProps({
  rating: {
    type: Number,
    default: 0
  },
  count: {
    type: Number,
    default: 0
  },
  interactive: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'md' // sm, md, lg
  }
})

const emit = defineEmits(['update:rating'])

const stars = computed(() => {
  const filled = Math.floor(props.rating)
  const hasHalf = props.rating - filled >= 0.5
  return Array(5).fill(0).map((_, i) => {
    if (i < filled) return 'full'
    if (i === filled && hasHalf) return 'half'
    return 'empty'
  })
})

const handleClick = (index) => {
  if (props.interactive) {
    emit('update:rating', index + 1)
  }
}

const sizeClass = computed(() => `stars-${props.size}`)
</script>

<template>
  <div class="rating-stars" :class="sizeClass">
    <span
      v-for="(star, index) in stars"
      :key="index"
      :class="['star', star, { interactive: interactive }]"
      @click="handleClick(index)"
    >
      {{ star === 'full' ? '★' : star === 'half' ? '½' : '☆' }}
    </span>
    <span class="rating-count" v-if="count > 0">({{ count }})</span>
  </div>
</template>

<style scoped>
.rating-stars {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.stars-sm .star {
  font-size: 14px;
}

.stars-md .star {
  font-size: 16px;
}

.stars-lg .star {
  font-size: 20px;
}

.star {
  color: var(--color-border);
  transition: color var(--transition-fast);
}

.star.full {
  color: var(--color-primary);
}

.star.half {
  color: var(--color-primary);
  opacity: 0.7;
}

.star.interactive {
  cursor: pointer;
}

.star.interactive:hover {
  color: var(--color-primary-hover);
}

.rating-count {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-text-muted);
  margin-left: 4px;
}
</style>