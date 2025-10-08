<script setup>
import { SelectItem as RadixSelectItem, SelectItemText } from 'radix-vue'
import { Check } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

defineProps({
  value: {
    type: String,
    required: true
  },
  disabled: {
    type: Boolean,
    default: false
  }
})
</script>

<template>
  <RadixSelectItem
    :value="value"
    :disabled="disabled"
    :class="cn(
      'relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
      $attrs.class
    )"
  >
    <span class="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
      <Check class="h-4 w-4 data-[state=unchecked]:hidden" />
    </span>
    <SelectItemText>
      <slot />
    </SelectItemText>
  </RadixSelectItem>
</template>
