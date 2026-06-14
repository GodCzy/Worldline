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

      <div class="support-banner" :class="{ warning: supportHints.length }" data-branch-support-status="true">
        <strong>{{ branch.quality?.status || 'inspectable' }}</strong>
        <span>{{ supportHintCopy }}</span>
      </div>

      <div v-if="hasGateReplay" class="gate-replay-panel" data-quality-gate-replay="true">
        <div class="gate-replay-head">
          <div>
            <strong>Quality Gate Replay</strong>
            <small>{{ latestGate.gate_id || latestGate.gateId || 'latest failed gate' }}</small>
          </div>
          <span class="gate-status">{{ latestGate.status || 'failed' }}</span>
        </div>

        <article
          v-for="failure in replayFailures"
          :key="failure.check"
          class="gate-failure"
          :data-gate-failure="failure.check"
        >
          <div class="gate-failure-head">
            <strong>{{ failure.check }}</strong>
            <span>{{ failure.severity || 'review' }}</span>
          </div>
          <p>{{ failure.reason || failureSummary(failure) }}</p>
          <div class="gate-targets" aria-label="Quality gate replay targets">
            <button
              v-for="target in normalizedTargets(failure)"
              :key="target.id"
              class="gate-target"
              type="button"
              :data-gate-target="target.kind"
              @click.stop="emitReplayTarget(target, failure)"
            >
              {{ targetKindLabel(target.kind) }}
            </button>
          </div>
        </article>
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

      <dl class="route-trace-grid" data-branch-route-trace="true">
        <div>
          <dt>Trace</dt>
          <dd>{{ branchTrace.branch_id || branch.id }}</dd>
        </div>
        <div>
          <dt>Policy</dt>
          <dd>{{ branchTrace.conclusionPolicy || 'evidence_required' }}</dd>
        </div>
        <div>
          <dt>Path</dt>
          <dd>{{ routePathLabel }}</dd>
        </div>
        <div>
          <dt>Support</dt>
          <dd>{{ branchTrace.supportStatus || branch.quality?.status || 'inspectable' }}</dd>
        </div>
      </dl>

      <div v-if="gateRefs.length" class="gate-ref-strip" data-branch-gate-refs="true">
        <button
          v-for="gate in gateRefs"
          :key="gate.gateId || gate.id"
          class="gate-ref"
          type="button"
          @click.stop="emitReplayTarget({ kind: 'run', gate_id: gate.gateId || gate.id, target_id: gate.gateId || gate.id })"
        >
          <span>{{ gate.gateId || gate.id || 'gate' }}</span>
          <small>{{ gate.status || 'pending' }}</small>
        </button>
      </div>

      <div class="section-block subtle">
        <strong>什么时候切线</strong>
        <p>{{ branch.switchHint || '当证据不足、图谱冲突或质量门禁失败时，先回到当前层修复。' }}</p>
      </div>

      <div v-if="branch.nextActions?.length" class="action-list">
        <button
          v-for="action in branch.nextActions"
          :key="action.id"
          class="action-button"
          :class="{
            primary: action.emphasis === 'primary',
            danger: action.emphasis === 'danger'
          }"
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
  },
  quality: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['handoff', 'open-graph', 'focus-replay-ref'])

const evidenceCount = computed(() => props.branch?.evidenceRefs?.length || 0)
const supportChannels = computed(() => {
  if (!props.branch) return 0
  return ['evidenceRefs', 'wikiRefs', 'entityRefs', 'timelineRefs'].filter((key) => props.branch[key]?.length).length
})
const branchTrace = computed(() => props.branch?.routeTrace || {})
const gateRefs = computed(() => (Array.isArray(props.branch?.gateRefs) ? props.branch.gateRefs : []))
const supportHints = computed(() => {
  const hints = props.branch?.quality?.hints || branchTrace.value?.hints || []
  return Array.isArray(hints) ? hints.slice(0, 4) : []
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
const supportHintCopy = computed(() => {
  if (!supportHints.value.length) return 'Evidence, Wiki, Graph, Time, Gate refs 已连接。'
  return supportHints.value.map((hint) => hint.message || hint.code).filter(Boolean).join(' / ')
})
const routePathLabel = computed(() => {
  const path = branchTrace.value?.path || []
  return Array.isArray(path) && path.length ? path.join(' -> ') : 'branch_canvas -> branch_inspector'
})
const latestGate = computed(() => props.quality?.latestGate || props.quality?.latest_gate || {})
const replayFailures = computed(() => {
  const replay = latestGate.value?.failure_replay || latestGate.value?.failureReplay || []
  return Array.isArray(replay) ? replay.slice(0, 3) : []
})
const hasGateReplay = computed(() => replayFailures.value.length > 0)

const targetKindLabels = {
  evidence: 'Evidence',
  wiki: 'Wiki',
  graph: 'Graph',
  timeline: 'Time',
  run: 'Run'
}

const targetKindLabel = (kind = '') => targetKindLabels[kind] || kind || 'Open'
const targetStableId = (target = {}, index = 0) =>
  [
    target.kind,
    target.target_id,
    target.targetId,
    target.id,
    target.evidence_id,
    target.entity_id,
    target.fact_id,
    target.page_id,
    target.gate_id,
    index
  ]
    .filter(Boolean)
    .join(':')

const normalizedTargets = (failure = {}) => {
  const directTargets = Array.isArray(failure.jump_targets) ? failure.jump_targets : []
  if (directTargets.length) {
    return directTargets.slice(0, 8).map((target, index) => ({
      ...target,
      id: targetStableId(target, index)
    }))
  }

  const refs = failure.refs || {}
  return Object.entries(refs)
    .flatMap(([kind, items]) =>
      (Array.isArray(items) ? items : []).slice(0, 2).map((item, index) => ({
        kind,
        label: item.label || item.title || item.name || item.id || kind,
        target_id: item.id || item.page_id || item.entity_id || item.fact_id || item.gate_id,
        evidence_id: item.evidence_id,
        entity_id: item.entity_id,
        fact_id: item.fact_id,
        page_id: item.page_id,
        gate_id: item.gate_id,
        id: `${kind}:${item.id || item.page_id || item.entity_id || item.fact_id || item.gate_id || index}`
      }))
    )
    .slice(0, 8)
}

const failureSummary = (failure = {}) => `${failure.observed ?? 'unknown'} / ${failure.expected || 'expected'}`

const emitAction = (action) => {
  if (action.targetType === 'graph') {
    emit('open-graph', action)
    return
  }
  emit('handoff', action)
}

const emitReplayTarget = (target = {}, failure = {}) => {
  emit('focus-replay-ref', {
    ...target,
    failure,
    gate: latestGate.value
  })
}
</script>

<style scoped lang="less">
.detail-panel {
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
  line-height: 1.4;
}

.state-pill,
.metric-row span {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 9px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.28);
  border-radius: 999px;
  background: rgba(var(--wl-gold-rgb), 0.1);
  color: var(--wl-gold-soft);
  font-size: 12px;
  font-weight: 800;
  white-space: nowrap;
}

.lead,
.summary,
.empty-copy {
  color: var(--wl-muted);
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
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.05);
}

.quality-grid strong {
  display: block;
  color: var(--wl-text);
  font-size: 18px;
  font-weight: 900;
}

.quality-grid span {
  color: var(--wl-muted-soft);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
}

.support-banner {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 8px;
  align-items: center;
  margin-top: 12px;
  padding: 10px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.16);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.045);
}

.support-banner.warning {
  border-color: rgba(var(--wl-gold-rgb), 0.28);
  background: rgba(var(--wl-gold-rgb), 0.07);
}

.support-banner strong {
  color: var(--wl-text);
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
  white-space: nowrap;
}

.support-banner span {
  min-width: 0;
  overflow-wrap: anywhere;
  color: var(--wl-muted);
  font-size: 12px;
  line-height: 1.5;
}

.gate-replay-panel {
  margin-top: 14px;
  padding: 12px;
  border: 1px solid rgba(255, 108, 108, 0.34);
  border-radius: var(--wl-radius-sm);
  background: rgba(255, 108, 108, 0.06);
}

.gate-replay-head,
.gate-failure-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.gate-replay-head strong,
.gate-failure-head strong {
  display: block;
  color: var(--wl-text);
  font-size: 13px;
  font-weight: 900;
}

.gate-replay-head small,
.gate-failure p {
  color: var(--wl-muted);
  font-size: 12px;
  line-height: 1.55;
}

.gate-status,
.gate-failure-head span {
  display: inline-flex;
  align-items: center;
  min-height: 22px;
  padding: 0 8px;
  border: 1px solid rgba(255, 108, 108, 0.34);
  border-radius: 999px;
  color: #ffdede;
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
  white-space: nowrap;
}

.gate-failure {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.gate-failure p {
  margin: 7px 0 0;
}

.gate-targets {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 9px;
}

.gate-target {
  min-height: 26px;
  padding: 0 8px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.22);
  border-radius: 999px;
  background: rgba(var(--wl-cyan-rgb), 0.07);
  color: var(--wl-text-soft);
  cursor: pointer;
  font-size: 11px;
  font-weight: 900;
}

.gate-target:hover,
.gate-target:focus-visible {
  border-color: rgba(var(--wl-gold-rgb), 0.52);
  background: rgba(var(--wl-gold-rgb), 0.12);
  color: #fff7de;
  outline: none;
}

.section-block {
  margin-top: 14px;
  padding: 12px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(255, 255, 255, 0.035);
}

.section-block.subtle {
  border-color: rgba(var(--wl-gold-rgb), 0.16);
  background: rgba(var(--wl-gold-rgb), 0.055);
}

.section-block strong {
  display: block;
  color: var(--wl-text);
  font-size: 13px;
  font-weight: 800;
}

.section-block p {
  margin: 7px 0 0;
  color: var(--wl-muted);
  font-size: 13px;
  line-height: 1.7;
}

.detail-grid {
  display: grid;
  gap: 10px;
  margin: 14px 0 0;
}

.detail-grid dt {
  color: rgba(var(--wl-gold-rgb), 0.74);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.detail-grid dd {
  margin: 4px 0 0;
  color: var(--wl-text);
  font-size: 13px;
  line-height: 1.6;
}

.route-trace-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 14px;
  padding: 10px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.12);
  border-radius: var(--wl-radius-sm);
  background: rgba(255, 255, 255, 0.03);
}

.route-trace-grid div {
  min-width: 0;
}

.route-trace-grid dt {
  color: rgba(var(--wl-gold-rgb), 0.78);
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
}

.route-trace-grid dd {
  margin: 3px 0 0;
  overflow-wrap: anywhere;
  color: var(--wl-muted);
  font-size: 12px;
  line-height: 1.45;
}

.gate-ref-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.gate-ref {
  display: inline-flex;
  min-width: 0;
  min-height: 30px;
  align-items: center;
  gap: 8px;
  padding: 0 9px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.26);
  border-radius: 999px;
  background: rgba(var(--wl-gold-rgb), 0.08);
  color: #fff7de;
  cursor: pointer;
  font-size: 11px;
  font-weight: 900;
}

.gate-ref span {
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.gate-ref small {
  color: var(--wl-muted-soft);
  font-weight: 800;
  text-transform: uppercase;
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
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.06);
  color: var(--wl-text-soft);
  cursor: pointer;
  text-align: left;
}

.action-button.primary {
  border-color: rgba(var(--wl-gold-rgb), 0.5);
  background: rgba(var(--wl-gold-rgb), 0.12);
  color: #fff7de;
}

.action-button.danger {
  border-color: rgba(255, 108, 108, 0.42);
  background: rgba(255, 108, 108, 0.08);
  color: #ffdede;
}

.action-button span {
  font-weight: 900;
}

.action-button small {
  color: var(--wl-muted-soft);
  line-height: 1.45;
}
</style>
