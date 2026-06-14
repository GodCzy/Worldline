<template>
  <section class="graph-focus-panel" data-worldline-graph-focus="true">
    <div class="panel-header">
      <div>
        <p class="eyebrow">GRAPH FOCUS</p>
        <h3>图谱聚焦</h3>
      </div>
      <button class="graph-button" type="button" @click="$emit('open-graph')">打开图谱</button>
    </div>

    <div class="focus-summary">
      <div>
        <strong>{{ entityRefs.length }}</strong>
        <span>Entities</span>
      </div>
      <div>
        <strong>{{ timelineRefs.length }}</strong>
        <span>Temporal</span>
      </div>
      <div>
        <strong>{{ qualityStatus }}</strong>
        <span>Quality</span>
      </div>
    </div>

    <div v-if="entityRefs.length" class="entity-list">
      <button
        v-for="entity in entityRefs.slice(0, 5)"
        :key="entity.id || entity.name"
        class="entity-chip"
        type="button"
        @click="$emit('focus-entity', entity)"
      >
        <span>{{ entity.name || entity.id }}</span>
        <small>{{ entity.type || 'entity' }}</small>
      </button>
    </div>

    <div v-if="timelineRefs.length" class="timeline-list">
      <button
        v-for="fact in timelineRefs.slice(0, 4)"
        :key="fact.id || fact.fact_id || fact.title"
        class="timeline-chip"
        type="button"
        @click="$emit('focus-timeline', fact)"
      >
        <span>{{ timelineTitle(fact) }}</span>
        <small>{{ timelineBadge(fact) }}</small>
      </button>
    </div>

    <dl class="trace-grid">
      <div v-if="routeTrace?.db_id">
        <dt>db</dt>
        <dd>{{ routeTrace.db_id }}</dd>
      </div>
      <div v-if="routeTrace?.adapter">
        <dt>adapter</dt>
        <dd>{{ routeTrace.adapter }}</dd>
      </div>
      <div v-if="routeTrace?.facade">
        <dt>facade</dt>
        <dd>{{ routeTrace.facade }}</dd>
      </div>
      <div v-if="routeTrace?.branch_id">
        <dt>branch</dt>
        <dd>{{ routeTrace.branch_id }}</dd>
      </div>
      <div v-if="routeTrace?.supportStatus">
        <dt>support</dt>
        <dd>{{ routeTrace.supportStatus }}</dd>
      </div>
      <div v-if="traceEvidenceCount !== undefined">
        <dt>evidence</dt>
        <dd>{{ traceEvidenceCount }}</dd>
      </div>
      <div v-if="traceTimelineCount !== undefined">
        <dt>timeline</dt>
        <dd>{{ traceTimelineCount }}</dd>
      </div>
    </dl>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  entityRefs: {
    type: Array,
    default: () => []
  },
  timelineRefs: {
    type: Array,
    default: () => []
  },
  quality: {
    type: Object,
    default: () => ({})
  },
  routeTrace: {
    type: Object,
    default: () => ({})
  }
})

defineEmits(['open-graph', 'focus-entity', 'focus-timeline'])

const qualityStatus = computed(() => props.quality?.status || props.quality?.latestGate?.status || 'pending')
const traceEvidenceCount = computed(() => props.routeTrace?.evidence_count ?? props.routeTrace?.counts?.evidence)
const traceTimelineCount = computed(() => props.routeTrace?.timeline_count ?? props.routeTrace?.counts?.timeline)
const timelineTitle = (item = {}) => item.title || item.subject || item.label || item.id || item.fact_id || 'Timeline fact'
const timelineBadge = (item = {}) => item.validFrom || item.occurred_at || item.date || item.status || 'temporal'
</script>

<style scoped lang="less">
.graph-focus-panel {
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

.graph-button {
  min-height: 30px;
  padding: 0 10px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.38);
  border-radius: 6px;
  background: rgba(var(--wl-gold-rgb), 0.12);
  color: #fff7de;
  cursor: pointer;
  font-size: 12px;
  font-weight: 900;
}

.focus-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-top: 14px;
}

.focus-summary div {
  padding: 10px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.05);
}

.focus-summary strong,
.focus-summary span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.focus-summary strong {
  color: var(--wl-text);
  font-size: 16px;
  font-weight: 900;
}

.focus-summary span {
  color: var(--wl-muted-soft);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.entity-list,
.timeline-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.entity-chip,
.timeline-chip {
  display: inline-flex;
  min-height: 34px;
  flex-direction: column;
  justify-content: center;
  max-width: 180px;
  padding: 6px 9px;
  border: 1px solid var(--wl-border);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.035);
  color: var(--wl-text-soft);
  cursor: pointer;
  text-align: left;
}

.timeline-chip {
  border-color: rgba(var(--wl-gold-rgb), 0.24);
}

.entity-chip span,
.entity-chip small,
.timeline-chip span,
.timeline-chip small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.entity-chip span,
.timeline-chip span {
  font-size: 12px;
  font-weight: 900;
}

.entity-chip small,
.timeline-chip small {
  color: var(--wl-muted-soft);
  font-size: 11px;
}

.trace-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin: 12px 0 0;
}

.trace-grid div {
  min-width: 0;
}

.trace-grid dt {
  color: rgba(var(--wl-gold-rgb), 0.78);
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
}

.trace-grid dd {
  margin: 3px 0 0;
  overflow-wrap: anywhere;
  color: var(--wl-muted);
  font-size: 12px;
}
</style>
