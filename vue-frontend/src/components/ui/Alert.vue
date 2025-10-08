<script setup>
import { computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps({
  variant: {
    type: String,
    default: 'default'
  }
})

const alertClass = computed(() => {
  const variants = {
    default: 'bg-background text-foreground',
    destructive: 'border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive',
    success: 'border-green-500/50 text-green-600 dark:border-green-500 [&>svg]:text-green-600',
    warning: 'border-yellow-500/50 text-yellow-600 dark:border-yellow-500 [&>svg]:text-yellow-600',
    info: 'border-blue-500/50 text-blue-600 dark:border-blue-500 [&>svg]:text-blue-600'
  }

  return cn(
    'relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground',
    variants[props.variant]
  )
})
</script>

<template>
  <div :class="alertClass" role="alert">
    <slot />
  </div>
</template>
