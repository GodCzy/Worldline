<template>
  <section class="branch-canvas" data-worldline-canvas="true">
    <div class="canvas-header">
      <div>
        <p class="eyebrow">{{ displayMeta.stageLabel || 'WORLDLINE STAGE' }}</p>
        <h2>{{ displayMeta.stageTitle || '世界线工作台' }}</h2>
        <p class="stage-subtitle">
          {{ displayMeta.stageSubtitle || '从证据出发，观察分支如何进入 Wiki、图谱和质量门禁。' }}
        </p>
      </div>
      <div class="canvas-meta">
        <span>{{ branchCount || branchNodeCount }} 条分支</span>
        <span v-if="activeSnapshot">{{ activeSnapshot.label }} / {{ activeSnapshot.metric }}</span>
      </div>
    </div>

    <div class="canvas-shell">
      <svg
        v-if="(tree.nodes || []).length"
        class="canvas-svg"
        :viewBox="`0 0 ${tree.width || 1200} ${tree.height || 640}`"
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <pattern id="worldline-grid" width="32" height="32" patternUnits="userSpaceOnUse">
            <path d="M 32 0 L 0 0 0 32" fill="none" stroke="rgba(124,246,255,0.08)" stroke-width="1" />
          </pattern>
          <linearGradient id="bundle-cyan" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#ffe2a6" stop-opacity="0.96" />
            <stop offset="45%" stop-color="#7cf6ff" stop-opacity="0.86" />
            <stop offset="100%" stop-color="#fff7de" stop-opacity="0.98" />
          </linearGradient>
          <linearGradient id="bundle-muted" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#d9b66f" stop-opacity="0.32" />
            <stop offset="100%" stop-color="#7cf6ff" stop-opacity="0.22" />
          </linearGradient>
          <filter id="edgeGlow">
            <feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="#7cf6ff" flood-opacity="0.42" />
            <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#ffd36f" flood-opacity="0.18" />
          </filter>
          <radialGradient id="rootFlare" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#fff7de" stop-opacity="0.96" />
            <stop offset="100%" stop-color="#ffd36f" stop-opacity="0" />
          </radialGradient>
        </defs>

        <rect x="0" y="0" :width="tree.width || 1200" :height="tree.height || 640" fill="url(#worldline-grid)" />
        <circle cx="92" cy="300" r="58" fill="url(#rootFlare)" opacity="0.9" />
        <circle :cx="(tree.width || 1200) - 100" cy="300" r="64" fill="url(#rootFlare)" opacity="0.75" />

        <g v-for="edge in tree.edges || []" :key="edge.id">
          <path
            v-for="offset in bundleOffsets"
            :key="`${edge.id}-${offset}`"
            :d="buildEdgePath(edge, offset)"
            :class="[
              'branch-edge',
              edge.kind,
              {
                highlighted: edge.isHighlighted || edge.branchId === activeBranchId,
                muted: activeBranchId && edge.branchId && edge.branchId !== activeBranchId
              }
            ]"
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
        <strong>等待世界线生成</strong>
        <p>输入目标后，系统会从证据、Wiki、图谱和质量门禁生成可验证分支。</p>
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
  },
  activeSnapshot: {
    type: Object,
    default: null
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
  return [-4, -1, 2, 5]
})

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
  const span = Math.max(90, (endX - startX) * 0.42)
  const lift = edge.kind === 'convergence' ? offset * 2 : offset * 1.4

  return `M ${startX} ${startY} C ${startX + span} ${startY - lift}, ${endX - span} ${endY + lift}, ${endX} ${endY}`
}
</script>

<style scoped lang="less">
.branch-canvas {
  min-height: 0;
  overflow: hidden;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background:
    radial-gradient(circle at 8% 50%, rgba(var(--wl-gold-rgb), 0.18), transparent 22%),
    radial-gradient(circle at 92% 50%, rgba(var(--wl-cyan-rgb), 0.18), transparent 24%),
    linear-gradient(180deg, rgba(7, 13, 22, 0.98), rgba(2, 5, 10, 0.98));
  box-shadow: var(--wl-shadow);
}

.canvas-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  padding: 16px 18px 6px;
}

.eyebrow {
  margin: 0 0 5px;
  color: var(--wl-gold);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.canvas-header h2 {
  margin: 0;
  color: var(--wl-text);
  font-size: 18px;
  font-weight: 800;
  line-height: 1.35;
}

.stage-subtitle {
  max-width: 780px;
  margin: 6px 0 0;
  color: var(--wl-muted);
  font-size: 13px;
  line-height: 1.6;
}

.canvas-meta {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.canvas-meta span {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border: 1px solid var(--wl-border-strong);
  border-radius: 999px;
  background: rgba(var(--wl-cyan-rgb), 0.08);
  color: var(--wl-text-soft);
  font-size: 12px;
  font-weight: 700;
}

.canvas-shell {
  width: 100%;
  min-height: 470px;
  overflow: hidden;
}

.canvas-svg {
  display: block;
  width: 100%;
  height: min(62vh, 680px);
  min-height: 520px;
}

.branch-edge {
  stroke: url(#bundle-muted);
  stroke-width: 1.1;
  opacity: 0.76;
  transition:
    opacity 160ms ease,
    stroke-width 160ms ease;

  &.guide {
    stroke-dasharray: 4 5;
  }

  &.convergence {
    stroke-width: 0.9;
  }

  &.highlighted {
    stroke: url(#bundle-cyan);
    stroke-width: 1.55;
    opacity: 1;
    filter: url(#edgeGlow);
  }

  &.muted {
    opacity: 0.24;
  }
}

.empty-state {
  display: flex;
  min-height: 420px;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 8px;
  color: var(--wl-muted);
  text-align: center;
}

.empty-state strong {
  color: var(--wl-text);
  font-weight: 800;
}

.empty-state p {
  max-width: 420px;
  margin: 0;
  line-height: 1.7;
}

@media (max-width: 780px) {
  .canvas-header {
    flex-direction: column;
  }

  .canvas-meta {
    justify-content: flex-start;
  }

  .canvas-shell {
    overflow-x: auto;
  }

  .canvas-svg {
    width: 980px;
    max-width: none;
    height: 560px;
  }
}
</style>
