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

const starPath = 'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z'
</script>

<template>
  <div :class="['rating-stars', `stars-${size}`]">
    <button
      v-for="(star, index) in stars"
      :key="index"
      :class="['star', star, { interactive }]"
      @click="handleClick(index)"
      :disabled="!interactive"
      :aria-label="`${index + 1} 星`"
    >
      <svg viewBox="0 0 24 24" :fill="star === 'empty' ? 'none' : 'currentColor'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path :d="starPath" />
        <clipPath v-if="star === 'half'" :id="`half-${index}`">
          <rect x="0" y="0" width="12" height="24" />
        </clipPath>
      </svg>
    </button>
    <span class="rating-count" v-if="count > 0">({{ count }})</span>
  </div>
</template>

<style scoped>
.rating-stars {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.star {
  display: inline-flex;
  align-items: center;
  background: none;
  border: none;
  padding: 0;
  transition: all var(--transition-fast);
}

.star svg {
  transition: all var(--transition-fast);
}

.stars-sm .star svg {
  width: 14px;
  height: 14px;
}

.stars-md .star svg {
  width: 16px;
  height: 16px;
}

.stars-lg .star svg {
  width: 20px;
  height: 20px;
}

.star.empty {
  color: var(--color-border);
}

.star.full {
  color: var(--color-primary);
}

.star.half {
  color: var(--color-primary);
  opacity: 0.6;
}

.star.interactive {
  cursor: pointer;
}

.star.interactive:hover {
  color: var(--color-primary-hover);
  transform: scale(1.15);
}

.star.interactive:active {
  transform: scale(0.95);
}

.rating-count {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-text-muted);
  margin-left: 4px;
}
</style>
