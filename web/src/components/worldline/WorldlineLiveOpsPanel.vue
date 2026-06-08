<template>
  <section class="live-ops-panel" data-worldline-live-ops="true">
    <div class="panel-header">
      <div>
        <p class="eyebrow">LIVE OPS</p>
        <h3>后端联通</h3>
      </div>
      <button
        class="icon-button"
        type="button"
        title="刷新概览"
        :disabled="disabled || Boolean(loadingKey)"
        @click="$emit('action', 'refresh')"
      >
        <RefreshCw :size="15" />
      </button>
    </div>

    <div class="ops-grid">
      <div>
        <strong>{{ count('evidence_anchors') }}</strong>
        <span>Evidence</span>
      </div>
      <div>
        <strong>{{ count('wiki_pages') }}</strong>
        <span>Wiki</span>
      </div>
      <div>
        <strong>{{ count('entities') }}</strong>
        <span>Entities</span>
      </div>
      <div>
        <strong>{{ count('temporal_facts') }}</strong>
        <span>Timeline</span>
      </div>
      <div>
        <strong>{{ gateStatus }}</strong>
        <span>Gate</span>
      </div>
      <div>
        <strong>{{ toolCount }}</strong>
        <span>MCP Tools</span>
      </div>
    </div>

    <div class="action-grid">
      <button
        v-for="action in actions"
        :key="action.key"
        class="action-button"
        type="button"
        :title="action.title"
        :disabled="disabled || Boolean(loadingKey)"
        @click="$emit('action', action.key)"
      >
        <component :is="action.icon" :size="15" />
        <span>{{ loadingKey === action.key ? '处理中' : action.label }}</span>
      </button>
    </div>

    <div class="ops-strip">
      <span>{{ overview?.db_id || 'no-db' }}</span>
      <span>Workflow {{ count('workflow_runs') }}</span>
      <span>Audit {{ auditCount }}</span>
      <span>{{ overview?.status || 'idle' }}</span>
    </div>

    <p v-if="statusMessage" class="status-copy">{{ statusMessage }}</p>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import {
  BookOpen,
  GitBranch,
  ListChecks,
  Network,
  RefreshCw,
  Route,
  ShieldCheck
} from 'lucide-vue-next'

const props = defineProps({
  overview: {
    type: Object,
    default: null
  },
  loadingKey: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  statusMessage: {
    type: String,
    default: ''
  }
})

defineEmits(['action'])

const actions = [
  { key: 'planWorkflow', label: '规划流程', title: '规划 Worldline workflow', icon: Route },
  { key: 'rebuildWiki', label: '重建 Wiki', title: '重建 Auto-Wiki', icon: BookOpen },
  { key: 'rebuildGraph', label: '重建图谱', title: '重建 Graph 和 Timeline', icon: GitBranch },
  { key: 'buildGoldenSet', label: '构建样本', title: '构建 Golden Set', icon: ListChecks },
  { key: 'runQualityGate', label: '运行门禁', title: '运行 Quality Gate', icon: ShieldCheck },
  { key: 'refreshManifest', label: 'MCP 状态', title: '刷新 MCP manifest 和审计摘要', icon: Network }
]

const counts = computed(() => props.overview?.counts || {})
const latestGate = computed(() => props.overview?.quality_gate?.latest || props.overview?.qualityGate?.latest || {})
const manifest = computed(() => props.overview?.mcp?.manifest || props.overview?.manifest || {})
const auditItems = computed(() => props.overview?.mcp?.audit_logs?.items || props.overview?.audit_logs?.items || [])

const count = (key) => Number(counts.value?.[key] || 0)
const gateStatus = computed(() => latestGate.value?.status || props.overview?.quality?.status || 'pending')
const toolCount = computed(() => (Array.isArray(manifest.value?.tools) ? manifest.value.tools.length : 0))
const auditCount = computed(() => auditItems.value.length || count('mcp_audit_logs'))
</script>

<style scoped lang="less">
.live-ops-panel {
  padding: 16px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background: var(--wl-panel);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.eyebrow {
  margin: 0 0 6px;
  color: var(--wl-gold);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.panel-header h3 {
  margin: 0;
  color: var(--wl-text);
  font-size: 16px;
  font-weight: 800;
}

.icon-button,
.action-button {
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.06);
  color: var(--wl-text-soft);
  cursor: pointer;
}

.icon-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.icon-button:disabled,
.action-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ops-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-top: 14px;
}

.ops-grid div {
  min-width: 0;
  padding: 10px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.05);
}

.ops-grid strong,
.ops-grid span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ops-grid strong {
  color: var(--wl-text);
  font-size: 16px;
  font-weight: 900;
}

.ops-grid span {
  color: var(--wl-muted-soft);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 12px;
}

.action-button {
  display: inline-flex;
  align-items: center;
  justify-content: flex-start;
  gap: 7px;
  min-height: 36px;
  padding: 0 10px;
  font-size: 12px;
  font-weight: 900;
}

.action-button:hover:not(:disabled) {
  border-color: var(--wl-border-gold);
  background: rgba(var(--wl-gold-rgb), 0.1);
  color: #fff7de;
}

.action-button span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ops-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.ops-strip span {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 8px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.18);
  border-radius: 999px;
  background: rgba(var(--wl-gold-rgb), 0.08);
  color: var(--wl-muted);
  font-size: 11px;
  font-weight: 800;
}

.status-copy {
  margin: 10px 0 0;
  color: var(--wl-muted);
  font-size: 12px;
  line-height: 1.6;
}

@media (max-width: 700px) {
  .ops-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
