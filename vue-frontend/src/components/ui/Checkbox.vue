<script setup>
import { CheckboxIndicator, CheckboxRoot } from 'radix-vue'
import { Check } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

const props = defineProps({
  checked: {
    type: [Boolean, String],
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  id: {
    type: String,
    default: undefined
  }
})

const emit = defineEmits(['update:checked'])
</script>

<template>
  <CheckboxRoot
    :id="id"
    :checked="checked"
    :disabled="disabled"
    :class="cn(
      'peer h-4 w-4 shrink-0 rounded-sm border border-primary ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground',
      $attrs.class
    )"
    @update:checked="emit('update:checked', $event)"
  >
    <CheckboxIndicator class="flex items-center justify-center text-current">
      <Check class="h-4 w-4" />
    </CheckboxIndicator>
  </CheckboxRoot>
</template>
