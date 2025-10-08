<script setup>
import { SelectContent, SelectGroup, SelectItem, SelectItemText, SelectLabel, SelectPortal, SelectRoot, SelectScrollDownButton, SelectScrollUpButton, SelectTrigger, SelectValue, SelectViewport } from 'radix-vue'
import { ChevronDown, ChevronUp } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <SelectRoot
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <SelectTrigger
      :class="cn(
        'flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
        $attrs.class
      )"
    >
      <SelectValue :placeholder="$attrs.placeholder || 'Select an option'" />
      <ChevronDown class="h-4 w-4 opacity-50" />
    </SelectTrigger>
    <SelectPortal>
      <SelectContent
        :class="cn(
          'relative z-50 max-h-96 min-w-[8rem] overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2'
        )"
        position="popper"
      >
        <SelectScrollUpButton class="flex cursor-default items-center justify-center py-1">
          <ChevronUp class="h-4 w-4" />
        </SelectScrollUpButton>
        <SelectViewport class="p-1">
          <slot />
        </SelectViewport>
        <SelectScrollDownButton class="flex cursor-default items-center justify-center py-1">
          <ChevronDown class="h-4 w-4" />
        </SelectScrollDownButton>
      </SelectContent>
    </SelectPortal>
  </SelectRoot>
</template>
