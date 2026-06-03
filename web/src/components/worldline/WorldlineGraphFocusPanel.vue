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

    <dl class="trace-grid">
      <div v-if="routeTrace?.adapter">
        <dt>adapter</dt>
        <dd>{{ routeTrace.adapter }}</dd>
      </div>
      <div v-if="routeTrace?.facade">
        <dt>facade</dt>
        <dd>{{ routeTrace.facade }}</dd>
      </div>
      <div v-if="routeTrace?.evidence_count !== undefined">
        <dt>evidence</dt>
        <dd>{{ routeTrace.evidence_count }}</dd>
      </div>
      <div v-if="routeTrace?.timeline_count !== undefined">
        <dt>timeline</dt>
        <dd>{{ routeTrace.timeline_count }}</dd>
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

defineEmits(['open-graph', 'focus-entity'])

const qualityStatus = computed(() => props.quality?.status || props.quality?.latestGate?.status || 'pending')
</script>

<style scoped lang="less">
.graph-focus-panel {
  padding: 16px;
  border: 1px solid rgba(124, 246, 255, 0.16);
  border-radius: 8px;
  background: rgba(7, 15, 24, 0.88);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.eyebrow {
  margin: 0 0 6px;
  color: #ffd36f;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.panel-header h3 {
  margin: 0;
  color: #f6fbff;
  font-size: 16px;
  font-weight: 800;
}

.graph-button {
  min-height: 30px;
  padding: 0 10px;
  border: 1px solid rgba(255, 211, 111, 0.38);
  border-radius: 6px;
  background: rgba(255, 211, 111, 0.12);
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
  border: 1px solid rgba(124, 246, 255, 0.14);
  border-radius: 7px;
  background: rgba(124, 246, 255, 0.05);
}

.focus-summary strong,
.focus-summary span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.focus-summary strong {
  color: #f6fbff;
  font-size: 16px;
  font-weight: 900;
}

.focus-summary span {
  color: rgba(216, 251, 255, 0.6);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.entity-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.entity-chip {
  display: inline-flex;
  min-height: 34px;
  flex-direction: column;
  justify-content: center;
  max-width: 180px;
  padding: 6px 9px;
  border: 1px solid rgba(124, 246, 255, 0.16);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.035);
  color: #d8fbff;
  cursor: pointer;
  text-align: left;
}

.entity-chip span,
.entity-chip small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.entity-chip span {
  font-size: 12px;
  font-weight: 900;
}

.entity-chip small {
  color: rgba(216, 251, 255, 0.58);
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
  color: rgba(255, 211, 111, 0.78);
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
}

.trace-grid dd {
  margin: 3px 0 0;
  overflow-wrap: anywhere;
  color: rgba(216, 251, 255, 0.72);
  font-size: 12px;
}
</style>
