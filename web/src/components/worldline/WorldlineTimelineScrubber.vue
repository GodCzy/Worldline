<template>
  <section class="timeline-scrubber" data-worldline-scrubber="true">
    <div class="scrubber-head">
      <div>
        <p class="eyebrow">TIME SCRUBBER</p>
        <h3>{{ activeSnapshot?.title || '时间快照' }}</h3>
      </div>
      <span>{{ activeIndex + 1 }} / {{ normalizedSnapshots.length || 1 }}</span>
    </div>

    <div class="scrubber-track" role="tablist" aria-label="Worldline snapshots">
      <button
        v-for="(snapshot, index) in normalizedSnapshots"
        :key="snapshot.id || index"
        class="snapshot-step"
        :class="{ active: index === activeIndex }"
        type="button"
        @click="$emit('update:activeIndex', index)"
      >
        <span class="step-dot"></span>
        <strong>{{ snapshot.label || `T${index + 1}` }}</strong>
        <small>{{ snapshot.metric ?? '-' }}</small>
      </button>
    </div>

    <p class="snapshot-summary">
      {{ activeSnapshot?.summary || '当前还没有快照。生成世界线后会展示证据、Wiki、图谱和质量门禁的演进。' }}
    </p>

    <div v-if="timelineRefs.length" class="temporal-list">
      <div v-for="item in timelineRefs.slice(0, 4)" :key="item.id || item.label" class="temporal-item">
        <strong>{{ item.label || item.id }}</strong>
        <span>{{ item.validFrom || 'unknown' }} -> {{ item.validTo || 'present' }}</span>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  snapshots: {
    type: Array,
    default: () => []
  },
  activeIndex: {
    type: Number,
    default: 0
  },
  timelineRefs: {
    type: Array,
    default: () => []
  }
})

defineEmits(['update:activeIndex'])

const normalizedSnapshots = computed(() =>
  props.snapshots.length
    ? props.snapshots
    : [
        {
          id: 'empty',
          label: 'Idle',
          title: '等待生成',
          metric: 0,
          summary: '生成世界线后会出现阶段快照。'
        }
      ]
)
const activeSnapshot = computed(
  () => normalizedSnapshots.value[props.activeIndex] || normalizedSnapshots.value[0] || null
)
</script>

<style scoped lang="less">
.timeline-scrubber {
  padding: 14px 16px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background: var(--wl-panel);
}

.scrubber-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.eyebrow {
  margin: 0 0 4px;
  color: var(--wl-gold);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.scrubber-head h3 {
  margin: 0;
  color: var(--wl-text);
  font-size: 15px;
  font-weight: 800;
}

.scrubber-head > span {
  color: var(--wl-muted-soft);
  font-size: 12px;
  font-weight: 800;
}

.scrubber-track {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  margin-top: 12px;
}

.snapshot-step {
  min-width: 0;
  min-height: 58px;
  padding: 9px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.05);
  color: var(--wl-muted);
  cursor: pointer;
  text-align: left;
}

.snapshot-step.active {
  border-color: var(--wl-border-gold);
  background: rgba(var(--wl-gold-rgb), 0.12);
  color: #fff7de;
}

.step-dot {
  display: block;
  width: 8px;
  height: 8px;
  margin-bottom: 8px;
  border-radius: 999px;
  background: var(--wl-cyan);
  box-shadow: 0 0 10px rgba(var(--wl-cyan-rgb), 0.68);
}

.snapshot-step.active .step-dot {
  background: var(--wl-gold);
  box-shadow: 0 0 12px rgba(var(--wl-gold-rgb), 0.82);
}

.snapshot-step strong,
.snapshot-step small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.snapshot-step strong {
  font-size: 12px;
  font-weight: 900;
}

.snapshot-step small {
  color: var(--wl-muted-soft);
  font-size: 11px;
  font-weight: 800;
}

.snapshot-summary {
  margin: 12px 0 0;
  color: var(--wl-muted);
  font-size: 13px;
  line-height: 1.6;
}

.temporal-list {
  display: grid;
  gap: 7px;
  margin-top: 12px;
}

.temporal-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 10px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.035);
  color: var(--wl-muted);
  font-size: 12px;
}

.temporal-item strong {
  color: var(--wl-text);
  font-weight: 800;
}

@media (max-width: 700px) {
  .scrubber-track {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .temporal-item {
    flex-direction: column;
    gap: 3px;
  }
}
</style>
