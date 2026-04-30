<template>
  <section class="branch-canvas">
    <div class="canvas-header">
      <div>
        <p class="eyebrow">WORLDLINE STAGE</p>
        <h2>{{ displayMeta.stageTitle || '线束树状世界线' }}</h2>
      </div>
      <div class="canvas-meta">
        <span>{{ branchCount || tree.nodes?.length || 0 }} 条分支</span>
      </div>
    </div>

    <div class="canvas-shell">
      <svg
        v-if="(tree.nodes || []).length"
        class="canvas-svg"
        :viewBox="`0 0 ${tree.width || 1200} ${tree.height || 640}`"
        preserveAspectRatio="xMinYMin meet"
        :style="svgStyle"
      >
        <defs>
          <pattern id="worldline-grid" width="28" height="28" patternUnits="userSpaceOnUse">
            <path
              d="M 28 0 L 0 0 0 28"
              fill="none"
              stroke="var(--main-300)"
              stroke-opacity="0.1"
              stroke-width="1"
            />
          </pattern>
          <linearGradient id="bundle-active" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="var(--main-300)" stop-opacity="0.38" />
            <stop offset="100%" stop-color="var(--main-700)" stop-opacity="0.78" />
          </linearGradient>
          <filter id="edgeGlow">
            <feDropShadow dx="0" dy="0" stdDeviation="2" flood-color="var(--main-500)" flood-opacity="0.18" />
          </filter>
        </defs>

        <rect x="0" y="0" :width="tree.width || 1200" :height="tree.height || 640" fill="url(#worldline-grid)" />

        <g v-for="edge in tree.edges || []" :key="edge.id">
          <path
            v-for="offset in bundleOffsets"
            :key="`${edge.id}-${offset}`"
            :d="buildEdgePath(edge, offset)"
            :class="['branch-edge', edge.kind, { highlighted: edge.isHighlighted }]"
            fill="none"
          />
        </g>

        <WorldlineBranchNode
          v-for="node in tree.nodes || []"
          :key="node.id"
          :node="node"
          :density-level="densityLevel"
          :is-active="node.branchId && node.branchId === activeBranchId"
          :is-selected="node.id === selectedNodeId"
          @select="$emit('select-node', $event)"
        />
      </svg>

      <div v-else class="empty-state">
        <strong>尚未生成世界线</strong>
        <p>先输入一句目标，生成基础分支。</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import WorldlineBranchNode from './WorldlineBranchNode.vue'

const props = defineProps({
  tree: {
    type: Object,
    required: true
  },
  activeBranchId: {
    type: String,
    default: ''
  },
  selectedNodeId: {
    type: String,
    default: ''
  },
  branchCount: {
    type: Number,
    default: 0
  },
  displayMeta: {
    type: Object,
    default: () => ({})
  }
})

defineEmits(['select-node'])

const branchNodeCount = computed(
  () => (props.tree.nodes || []).filter((node) => node.type === 'branch').length || props.branchCount || 0
)

const densityLevel = computed(() => {
  if (branchNodeCount.value >= 8) return 'dense'
  if (branchNodeCount.value >= 5) return 'compact'
  return 'normal'
})

const bundleOffsets = computed(() => {
  if (densityLevel.value === 'dense') return [-1, 0, 1]
  if (densityLevel.value === 'compact') return [-2, 0, 2]
  return [-3, 0, 3]
})

const svgStyle = computed(() => ({
  width: `${props.tree.width || 1200}px`,
  height: `${props.tree.height || 640}px`,
  minWidth: '100%'
}))

const findNode = (nodeId) => (props.tree.nodes || []).find((node) => node.id === nodeId)

const buildEdgePath = (edge, offset = 0) => {
  const source = findNode(edge.source)
  const target = findNode(edge.target)
  if (!source || !target) {
    return ''
  }

  const startX = Number(source.x || 0)
  const startY = Number(source.y || 0) + offset
  const endX = Number(target.x || 0)
  const endY = Number(target.y || 0) + offset
  const span = Math.max(70, (endX - startX) * 0.45)

  return `M ${startX} ${startY} C ${startX + span} ${startY}, ${endX - span} ${endY}, ${endX} ${endY}`
}
</script>

<style scoped lang="less">
.branch-canvas {
  border-radius: 22px;
  border: 1px solid color-mix(in srgb, var(--main-200) 30%, transparent);
  background:
    radial-gradient(circle at top left, color-mix(in srgb, var(--main-100) 16%, transparent), transparent 35%),
    linear-gradient(180deg, color-mix(in srgb, var(--gray-0) 95%, transparent), var(--main-10));
  box-shadow: 0 12px 28px color-mix(in srgb, var(--gray-1000) 6%, transparent);
}

.canvas-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 16px 0;
}

.eyebrow {
  margin: 0 0 6px;
  color: var(--main-600);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

.canvas-header h2 {
  margin: 0;
  font-size: 1.02rem;
  color: var(--gray-1000);
}

.canvas-meta span {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--main-30) 76%, var(--gray-0));
  color: var(--main-700);
  font-size: 12px;
  font-weight: 700;
}

.canvas-shell {
  margin-top: 12px;
  border-radius: 18px;
  max-height: min(72vh, 980px);
  overflow: auto;
  border: 1px solid color-mix(in srgb, var(--main-100) 20%, transparent);
}

.canvas-svg {
  display: block;
  min-height: 560px;
}

.branch-edge {
  stroke: color-mix(in srgb, var(--main-300) 40%, transparent);
  stroke-width: 0.9;

  &.secondary {
    stroke-opacity: 0.5;
  }

  &.guide {
    stroke-opacity: 0.38;
    stroke-dasharray: 3 4;
  }

  &.highlighted {
    stroke: url(#bundle-active);
    stroke-width: 1.15;
    filter: url(#edgeGlow);
  }
}

.empty-state {
  display: flex;
  min-height: 420px;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 8px;
  color: var(--gray-600);
}

.empty-state strong {
  color: var(--gray-900);
}

@media (max-width: 980px) {
  .canvas-header {
    flex-direction: column;
  }
}
</style>
