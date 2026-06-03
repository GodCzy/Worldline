<template>
  <g
    class="branch-node"
    :class="[
      `kind-${node.type || 'branch'}`,
      `tone-${node.tone || 'calm'}`,
      { active: isActive, selected: isSelected }
    ]"
    tabindex="0"
    @click="$emit('select', node.id)"
    @keydown.enter.prevent="$emit('select', node.id)"
  >
    <circle :cx="cx" :cy="cy" :r="outerRadius + 10" class="node-aura" />
    <circle :cx="cx" :cy="cy" :r="outerRadius" class="node-halo" />
    <circle :cx="cx" :cy="cy" :r="innerRadius" class="node-core" />
    <text :x="labelX" :y="cy - 4" class="node-title">{{ titleText }}</text>
    <text v-if="showSubtitle" :x="labelX" :y="cy + 16" class="node-subtitle">{{ subtitleText }}</text>

    <g class="node-tooltip" :class="{ show: isSelected }">
      <rect
        :x="tooltipBox.x"
        :y="tooltipBox.y"
        :width="tooltipBox.width"
        :height="tooltipBox.height"
        rx="8"
        ry="8"
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
const labelX = computed(() => cx.value + outerRadius.value + 14)

const titleLimit = computed(() => {
  if (props.densityLevel === 'dense') return 12
  if (props.densityLevel === 'compact') return 15
  return 18
})
const subtitleLimit = computed(() => (props.densityLevel === 'dense' ? 0 : 24))
const showSubtitle = computed(() => subtitleLimit.value > 0 && (props.isSelected || props.isActive))
const titleText = computed(() => truncate(props.node.title, titleLimit.value))
const subtitleText = computed(() =>
  subtitleLimit.value > 0 ? truncate(props.node.subtitle || props.node.meta, subtitleLimit.value) : ''
)
const tooltipLines = computed(() => {
  const fallback = props.node.title || ''
  const primary = props.node.subtitle || props.node.meta || fallback
  const secondary = props.node.meta && props.node.meta !== primary ? props.node.meta : ''
  return [primary, secondary].filter(Boolean).slice(0, 2).map((line) => truncate(line, 34))
})

const tooltipBox = computed(() => {
  const lineCount = Math.max(1, tooltipLines.value.length)
  const width = 214
  const x = Math.min(labelX.value, 1200 - width - 24)
  return {
    x,
    y: cy.value + 24,
    width,
    height: 12 + lineCount * 16
  }
})
</script>

<style scoped lang="less">
.branch-node {
  cursor: pointer;
  outline: none;
}

.node-aura {
  fill: transparent;
  opacity: 0;
}

.node-halo {
  fill: rgba(90, 242, 255, 0.1);
  stroke: rgba(var(--wl-cyan-rgb), 0.55);
  stroke-width: 1.2;
  transition:
    fill 160ms ease,
    stroke 160ms ease,
    filter 160ms ease;
}

.node-core {
  fill: #f8fcff;
  stroke: rgba(255, 218, 138, 0.85);
  stroke-width: 1;
}

.branch-node.kind-root .node-core {
  fill: #ffe3a4;
}

.branch-node.kind-convergence .node-core {
  fill: #fff7de;
  stroke: var(--wl-gold);
}

.branch-node.tone-focus .node-core {
  stroke: var(--wl-cyan);
}

.branch-node.tone-peak .node-core {
  stroke: var(--wl-gold);
}

.branch-node:hover .node-halo,
.branch-node.active .node-halo,
.branch-node.selected .node-halo {
  fill: rgba(90, 242, 255, 0.18);
  stroke: rgba(255, 218, 138, 0.85);
  filter: drop-shadow(0 0 10px rgba(var(--wl-cyan-rgb), 0.48));
}

.branch-node.selected .node-core {
  filter: drop-shadow(0 0 8px rgba(var(--wl-gold-rgb), 0.72));
}

.node-title {
  fill: var(--wl-text);
  font-size: 12px;
  font-weight: 700;
  paint-order: stroke;
  stroke: rgba(5, 9, 14, 0.75);
  stroke-width: 3px;
}

.node-subtitle {
  fill: #9feaf2;
  font-size: 10px;
  font-weight: 600;
  paint-order: stroke;
  stroke: rgba(5, 9, 14, 0.8);
  stroke-width: 3px;
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
  fill: rgba(7, 15, 24, 0.94);
  stroke: rgba(var(--wl-cyan-rgb), 0.48);
  stroke-width: 1;
}

.tooltip-text {
  fill: var(--wl-text-soft);
  font-size: 10px;
  font-weight: 600;
}
</style>
