<script setup>
import { ProgressIndicator, ProgressRoot } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps({
  modelValue: {
    type: [Number, null],
    default: 0
  },
  max: {
    type: Number,
    default: 100
  }
})
</script>

<template>
  <ProgressRoot
    :model-value="modelValue"
    :max="max"
    :class="cn('relative h-4 w-full overflow-hidden rounded-full bg-secondary', $attrs.class)"
  >
    <ProgressIndicator
      class="h-full w-full flex-1 bg-primary transition-all"
      :style="`transform: translateX(-${100 - (modelValue ?? 0)}%)`"
    />
  </ProgressRoot>
</template>
