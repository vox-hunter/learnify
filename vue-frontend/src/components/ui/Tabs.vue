<script setup>
import { TabsRoot } from 'radix-vue'
import { cn } from '@/lib/utils'

defineProps({
  defaultValue: String,
  modelValue: String
})

defineEmits(['update:modelValue'])
</script>

<template>
  <TabsRoot
    v-bind="$attrs"
    :default-value="defaultValue"
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <slot />
  </TabsRoot>
</template>
