<template>
  <section class="evidence-rail" data-worldline-evidence="true">
    <div class="panel-header">
      <div>
        <p class="eyebrow">EVIDENCE RAIL</p>
        <h3>证据、Wiki、图谱与时间事实</h3>
      </div>
      <span class="count-pill">{{ totalCount }} 条支撑</span>
    </div>

    <div class="rail-tabs" role="tablist" aria-label="Worldline evidence layers">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="rail-tab"
        :class="{ active: activeTab === tab.key }"
        type="button"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
        <span>{{ tab.count }}</span>
      </button>
    </div>

    <div v-if="activeItems.length" class="rail-list">
      <article
        v-for="(item, index) in activeItems"
        :key="`${activeTab}-${item.id || item.title || item.name || index}`"
        class="rail-item"
      >
        <div class="rail-item-top">
          <strong>{{ itemTitle(item) }}</strong>
          <small>{{ itemBadge(item) }}</small>
        </div>
        <p>{{ itemSummary(item) }}</p>
        <dl class="evidence-meta">
          <div v-if="item.evidenceId">
            <dt>ID</dt>
            <dd>{{ item.evidenceId }}</dd>
          </div>
          <div v-if="item.sourceUri">
            <dt>来源</dt>
            <dd>{{ item.sourceUri }}</dd>
          </div>
          <div v-if="formatLocation(item)">
            <dt>位置</dt>
            <dd>{{ formatLocation(item) }}</dd>
          </div>
          <div v-if="formatBBox(item)">
            <dt>BBox</dt>
            <dd>{{ formatBBox(item) }}</dd>
          </div>
        </dl>
      </article>
    </div>

    <p v-else class="empty-copy">当前分支还没有该层支撑。先重建 Wiki/Graph 或运行质量门禁，再继续扩展世界线。</p>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  evidenceRefs: {
    type: Array,
    default: () => []
  },
  wikiRefs: {
    type: Array,
    default: () => []
  },
  entityRefs: {
    type: Array,
    default: () => []
  },
  timelineRefs: {
    type: Array,
    default: () => []
  }
})

const activeTab = ref('evidence')

const tabs = computed(() => [
  { key: 'evidence', label: 'Evidence', count: props.evidenceRefs.length },
  { key: 'wiki', label: 'Wiki', count: props.wikiRefs.length },
  { key: 'graph', label: 'Graph', count: props.entityRefs.length },
  { key: 'timeline', label: 'Time', count: props.timelineRefs.length }
])

const activeItems = computed(() => {
  if (activeTab.value === 'wiki') return props.wikiRefs
  if (activeTab.value === 'graph') return props.entityRefs
  if (activeTab.value === 'timeline') return props.timelineRefs
  return props.evidenceRefs
})

const totalCount = computed(
  () => props.evidenceRefs.length + props.wikiRefs.length + props.entityRefs.length + props.timelineRefs.length
)

const itemTitle = (item = {}) => item.title || item.name || item.label || item.slug || item.id || '未命名支撑'
const itemBadge = (item = {}) => item.typeLabel || item.type || item.status || activeTab.value
const itemSummary = (item = {}) => {
  if (item.summary) return item.summary
  if (activeTab.value === 'wiki') return item.slug ? `Wiki slug: ${item.slug}` : '该 Wiki 页面参与当前分支解释。'
  if (activeTab.value === 'graph') return item.confidence ? `实体置信度 ${item.confidence}` : '该实体参与当前分支图谱支撑。'
  if (activeTab.value === 'timeline') return `${item.validFrom || 'unknown'} -> ${item.validTo || 'present'}`
  return '该证据解释当前世界线为什么值得继续推进。'
}

const formatLocation = (item = {}) => {
  const parts = []
  if (item.page) parts.push(`page ${item.page}`)
  if (item.lineStart && item.lineEnd) parts.push(`line ${item.lineStart}-${item.lineEnd}`)
  else if (item.lineStart) parts.push(`line ${item.lineStart}`)
  return parts.join(' / ')
}

const formatBBox = (item = {}) => {
  if (!Array.isArray(item.bbox) || !item.bbox.length) return ''
  return item.bbox.join(', ')
}
</script>

<style scoped lang="less">
.evidence-rail {
  min-height: 0;
  padding: 16px;
  border: 1px solid rgba(124, 246, 255, 0.16);
  border-radius: 8px;
  background: rgba(7, 15, 24, 0.88);
  box-shadow: inset 0 0 28px rgba(124, 246, 255, 0.04);
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

.count-pill {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 9px;
  border-radius: 999px;
  background: rgba(255, 211, 111, 0.11);
  color: #ffe2a6;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.rail-tabs {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 6px;
  margin-top: 14px;
}

.rail-tab {
  min-width: 0;
  min-height: 34px;
  border: 1px solid rgba(124, 246, 255, 0.16);
  border-radius: 6px;
  background: rgba(124, 246, 255, 0.05);
  color: rgba(216, 251, 255, 0.72);
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}

.rail-tab span {
  margin-left: 4px;
  color: #ffd36f;
  font-weight: 800;
}

.rail-tab.active {
  border-color: rgba(255, 211, 111, 0.5);
  background: rgba(255, 211, 111, 0.12);
  color: #fff7de;
}

.rail-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 360px;
  margin-top: 12px;
  overflow: auto;
  padding-right: 4px;
}

.rail-item {
  padding: 12px;
  border: 1px solid rgba(124, 246, 255, 0.14);
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.035);
}

.rail-item-top {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: flex-start;
}

.rail-item-top strong {
  color: #f6fbff;
  font-weight: 800;
  line-height: 1.5;
}

.rail-item-top small {
  flex-shrink: 0;
  color: #7cf6ff;
  font-size: 11px;
  font-weight: 800;
}

.rail-item p,
.empty-copy {
  margin: 8px 0 0;
  color: rgba(216, 251, 255, 0.68);
  line-height: 1.65;
  font-size: 13px;
}

.evidence-meta {
  display: grid;
  gap: 6px;
  margin: 10px 0 0;
  color: rgba(216, 251, 255, 0.62);
  font-size: 12px;
}

.evidence-meta div {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr);
  gap: 8px;
}

.evidence-meta dt {
  color: rgba(255, 211, 111, 0.78);
  font-weight: 800;
}

.evidence-meta dd {
  min-width: 0;
  margin: 0;
  overflow-wrap: anywhere;
}
</style>
