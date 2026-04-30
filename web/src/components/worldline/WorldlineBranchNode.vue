<template>
  <g
    class="branch-node"
    :class="[`kind-${node.type || 'branch'}`, `tone-${node.tone || 'calm'}`, { active: isActive, selected: isSelected }]"
    @click="$emit('select', node.id)"
  >
    <circle :cx="cx" :cy="cy" :r="outerRadius" class="node-halo" />
    <circle :cx="cx" :cy="cy" :r="innerRadius" class="node-core" />
    <text :x="cx + outerRadius + 10" :y="cy - 2" class="node-title">{{ titleText }}</text>
    <text v-if="showSubtitle" :x="cx + outerRadius + 10" :y="cy + 14" class="node-subtitle">{{ subtitleText }}</text>

    <g class="node-tooltip" :class="{ show: isSelected }">
      <rect
        :x="tooltipBox.x"
        :y="tooltipBox.y"
        :width="tooltipBox.width"
        :height="tooltipBox.height"
        rx="12"
        ry="12"
        class="tooltip-shell"
      />
      <text
        v-for="(line, index) in tooltipLines"
        :key="`${node.id}-tip-${index}`"
        :x="tooltipBox.x + 10"
        :y="tooltipBox.y + 20 + index * 15"
        class="tooltip-text"
      >
        {{ line }}
      </text>
    </g>
  </g>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  node: {
    type: Object,
    required: true
  },
  isActive: {
    type: Boolean,
    default: false
  },
  isSelected: {
    type: Boolean,
    default: false
  },
  densityLevel: {
    type: String,
    default: 'normal'
  }
})

defineEmits(['select'])

const truncate = (value, limit) => {
  if (!value) return ''
  return value.length > limit ? `${value.slice(0, limit - 1)}…` : value
}

const cx = computed(() => Number(props.node.x || 0))
const cy = computed(() => Number(props.node.y || 0))
const outerRadius = computed(() => Number(props.node.radius || 9))
const innerRadius = computed(() => Math.max(3, outerRadius.value - 4))

const titleLimit = computed(() => {
  if (props.densityLevel === 'dense') return 12
  if (props.densityLevel === 'compact') return 14
  return 16
})
const subtitleLimit = computed(() => {
  if (props.densityLevel === 'dense') return 0
  return 18
})
const showSubtitle = computed(() => subtitleLimit.value > 0 && (props.isSelected || props.isActive))
const titleText = computed(() => truncate(props.node.title, titleLimit.value))
const subtitleText = computed(() =>
  subtitleLimit.value > 0 ? truncate(props.node.subtitle || props.node.meta, subtitleLimit.value) : ''
)
const tooltipLines = computed(() => {
  const fallback = props.node.title || ''
  const primary = props.node.subtitle || props.node.meta || fallback
  const secondary = props.node.meta && props.node.meta !== primary ? props.node.meta : ''
  return [primary, secondary].filter(Boolean).slice(0, 2).map((line) => truncate(line, 32))
})

const tooltipBox = computed(() => {
  const lineCount = Math.max(1, tooltipLines.value.length)
  return {
    x: cx.value + outerRadius.value + 8,
    y: cy.value - 12,
    width: 188,
    height: 10 + lineCount * 15
  }
})
</script>

<style scoped lang="less">
.branch-node {
  cursor: pointer;
}

.node-halo {
  fill: color-mix(in srgb, var(--main-500) 12%, transparent);
  stroke: color-mix(in srgb, var(--main-400) 46%, transparent);
  stroke-width: 1.1;
  transition: fill 160ms ease, stroke 160ms ease, filter 160ms ease;
}

.node-core {
  fill: color-mix(in srgb, var(--gray-0) 96%, transparent);
  stroke: color-mix(in srgb, var(--main-500) 68%, transparent);
  stroke-width: 1;
}

.branch-node.kind-root .node-core {
  fill: color-mix(in srgb, var(--main-30) 85%, var(--gray-0));
}

.branch-node.kind-focus .node-halo,
.branch-node.kind-focus .node-core {
  stroke: color-mix(in srgb, var(--main-700) 82%, transparent);
}

.branch-node.tone-peak .node-core {
  stroke: color-mix(in srgb, var(--color-info-500) 70%, transparent);
}

.branch-node.active .node-halo,
.branch-node.selected .node-halo {
  fill: color-mix(in srgb, var(--main-500) 20%, transparent);
  filter: drop-shadow(0 0 7px color-mix(in srgb, var(--main-500) 28%, transparent));
}

.node-title {
  fill: var(--gray-1000);
  font-size: 12px;
  font-weight: 700;
}

.node-subtitle {
  fill: var(--gray-600);
  font-size: 10px;
  font-weight: 600;
}

.node-tooltip {
  opacity: 0;
  pointer-events: none;
  transition: opacity 140ms ease;
}

.branch-node:hover .node-tooltip,
.node-tooltip.show {
  opacity: 1;
}

.tooltip-shell {
  fill: color-mix(in srgb, var(--gray-0) 94%, transparent);
  stroke: color-mix(in srgb, var(--main-300) 56%, transparent);
  stroke-width: 1;
}

.tooltip-text {
  fill: var(--gray-900);
  font-size: 10px;
  font-weight: 600;
}
</style>
