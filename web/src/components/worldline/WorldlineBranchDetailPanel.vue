<template>
  <section class="detail-panel" data-worldline-detail="true">
    <div class="panel-header">
      <div>
        <p class="eyebrow">BRANCH INSPECTOR</p>
        <h3>{{ branch ? branch.title : '等待选择世界线分支' }}</h3>
      </div>
      <span v-if="branch" class="state-pill">{{ branch.choiceLabel || branch.stageLabel || 'Branch' }}</span>
    </div>

    <template v-if="branch">
      <p class="lead">{{ branch.subtitle }}</p>
      <p class="summary">{{ shortSummary }}</p>

      <div class="metric-row">
        <span>{{ branch.riskLabel || '可验证' }}</span>
        <span>{{ branch.costLabel || '低扰动' }}</span>
        <span>{{ branch.confidenceLabel || '证据基线' }}</span>
      </div>

      <div class="quality-grid">
        <div>
          <strong>{{ branch.quality?.evidenceCount ?? evidenceCount }}</strong>
          <span>Evidence</span>
        </div>
        <div>
          <strong>{{ coverageLabel }}</strong>
          <span>Coverage</span>
        </div>
        <div>
          <strong>{{ branch.quality?.supportChannels ?? supportChannels }}</strong>
          <span>Channels</span>
        </div>
      </div>

      <div class="section-block">
        <strong>为什么生成这条线</strong>
        <p>{{ branch.choiceReason || branch.summary }}</p>
      </div>

      <dl class="detail-grid">
        <div>
          <dt>当前焦点</dt>
          <dd>{{ branch.focus || branch.choiceLabel || branch.id }}</dd>
        </div>
        <div>
          <dt>适合场景</dt>
          <dd>{{ (branch.suitability || []).join(' / ') || '未标注' }}</dd>
        </div>
        <div>
          <dt>路线语气</dt>
          <dd>{{ branch.routeTone || '先验证，再生成。' }}</dd>
        </div>
        <div>
          <dt>下一步</dt>
          <dd>{{ branch.nextStepTitle }}</dd>
        </div>
      </dl>

      <div class="section-block subtle">
        <strong>什么时候切线</strong>
        <p>{{ branch.switchHint || '当证据不足、图谱冲突或质量门禁失败时，先回到当前层修复。' }}</p>
      </div>

      <div v-if="branch.nextActions?.length" class="action-list">
        <button
          v-for="action in branch.nextActions"
          :key="action.id"
          class="action-button"
          :class="{ primary: action.emphasis === 'primary' }"
          type="button"
          @click="emitAction(action)"
        >
          <span>{{ action.label }}</span>
          <small>{{ action.description }}</small>
        </button>
      </div>
    </template>

    <p v-else class="empty-copy">先在主舞台中点击一条分支，再检查它的证据、图谱、时间事实和 Agent 交接路径。</p>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  branch: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['handoff', 'open-graph'])

const evidenceCount = computed(() => props.branch?.evidenceRefs?.length || 0)
const supportChannels = computed(() => {
  if (!props.branch) return 0
  return ['evidenceRefs', 'wikiRefs', 'entityRefs', 'timelineRefs'].filter((key) => props.branch[key]?.length).length
})
const shortSummary = computed(() => {
  const summary = props.branch?.summary || ''
  if (!summary) return '选择分支后，这里会显示可验证说明。'
  return summary.length > 180 ? `${summary.slice(0, 178)}…` : summary
})
const coverageLabel = computed(() => {
  const coverage = Number(props.branch?.quality?.citationCoverage ?? 0)
  return `${Math.round(coverage * 100)}%`
})

const emitAction = (action) => {
  if (action.targetType === 'graph') {
    emit('open-graph', action)
    return
  }
  emit('handoff', action)
}
</script>

<style scoped lang="less">
.detail-panel {
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
  line-height: 1.4;
}

.state-pill,
.metric-row span {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 9px;
  border: 1px solid rgba(255, 211, 111, 0.28);
  border-radius: 999px;
  background: rgba(255, 211, 111, 0.1);
  color: #ffe2a6;
  font-size: 12px;
  font-weight: 800;
  white-space: nowrap;
}

.lead,
.summary,
.empty-copy {
  color: rgba(216, 251, 255, 0.72);
  line-height: 1.7;
}

.lead {
  margin: 12px 0 0;
  font-weight: 700;
}

.summary {
  margin: 8px 0 0;
  font-size: 13px;
}

.metric-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.quality-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-top: 14px;
}

.quality-grid div {
  padding: 10px;
  border: 1px solid rgba(124, 246, 255, 0.14);
  border-radius: 7px;
  background: rgba(124, 246, 255, 0.05);
}

.quality-grid strong {
  display: block;
  color: #f6fbff;
  font-size: 18px;
  font-weight: 900;
}

.quality-grid span {
  color: rgba(216, 251, 255, 0.62);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
}

.section-block {
  margin-top: 14px;
  padding: 12px;
  border: 1px solid rgba(124, 246, 255, 0.14);
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.035);
}

.section-block.subtle {
  border-color: rgba(255, 211, 111, 0.16);
  background: rgba(255, 211, 111, 0.055);
}

.section-block strong {
  display: block;
  color: #f6fbff;
  font-size: 13px;
  font-weight: 800;
}

.section-block p {
  margin: 7px 0 0;
  color: rgba(216, 251, 255, 0.68);
  font-size: 13px;
  line-height: 1.7;
}

.detail-grid {
  display: grid;
  gap: 10px;
  margin: 14px 0 0;
}

.detail-grid dt {
  color: rgba(255, 211, 111, 0.74);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.detail-grid dd {
  margin: 4px 0 0;
  color: #f6fbff;
  font-size: 13px;
  line-height: 1.6;
}

.action-list {
  display: grid;
  gap: 8px;
  margin-top: 14px;
}

.action-button {
  display: flex;
  min-height: 48px;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 3px;
  padding: 10px 12px;
  border: 1px solid rgba(124, 246, 255, 0.18);
  border-radius: 7px;
  background: rgba(124, 246, 255, 0.06);
  color: #d8fbff;
  cursor: pointer;
  text-align: left;
}

.action-button.primary {
  border-color: rgba(255, 211, 111, 0.5);
  background: rgba(255, 211, 111, 0.12);
  color: #fff7de;
}

.action-button span {
  font-weight: 900;
}

.action-button small {
  color: rgba(216, 251, 255, 0.62);
  line-height: 1.45;
}
</style>
