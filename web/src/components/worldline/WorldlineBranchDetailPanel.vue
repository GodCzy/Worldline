<template>
  <section class="inspect-panel detail-panel">
    <div class="panel-header">
      <div>
        <p class="eyebrow">节点详情</p>
        <h3>{{ branch ? branch.title : '等待选择一条世界线' }}</h3>
      </div>
      <div class="panel-actions" v-if="branch">
        <span class="state-pill">{{ branch.stageLabel }}</span>
        <button class="detail-toggle" type="button" @click="isExpanded = !isExpanded">
          {{ isExpanded ? '收起' : '展开' }}
        </button>
      </div>
    </div>

    <template v-if="branch">
      <p class="lead">{{ branch.subtitle }}</p>
      <p class="summary">{{ shortSummary }}</p>

      <div class="meta-row">
        <span class="meta-chip">{{ branch.riskLabel }}</span>
        <span class="meta-chip">{{ branch.costLabel }}</span>
        <span class="meta-chip">{{ branch.confidenceLabel }}</span>
      </div>

      <template v-if="isExpanded">
        <div class="section-block">
          <strong>为什么会生成这条线</strong>
          <p>{{ branch.choiceReason || branch.summary }}</p>
        </div>

        <dl class="detail-grid">
          <div>
            <dt>当前聚焦</dt>
            <dd>{{ branch.choiceLabel }}</dd>
          </div>
          <div>
            <dt>适合人群</dt>
            <dd>{{ (branch.suitability || []).join(' / ') || '未标注' }}</dd>
          </div>
          <div>
            <dt>当前节奏</dt>
            <dd>{{ branch.routeTone }}</dd>
          </div>
          <div>
            <dt>下一步</dt>
            <dd>{{ branch.nextStepTitle }}</dd>
          </div>
        </dl>

        <div class="section-block subtle">
          <strong>什么时候应该切线</strong>
          <p>{{ branch.switchHint }}</p>
        </div>
      </template>
    </template>

    <p v-else class="empty-copy">先在主舞台中点击一条分支，再查看模型对这条世界线的解释。</p>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  branch: {
    type: Object,
    default: null
  }
})

const isExpanded = ref(false)

const shortSummary = computed(() => {
  const summary = props.branch?.summary || ''
  if (!summary) {
    return '选择一条分支后，这里会显示简要说明。'
  }
  return summary.length > 120 ? `${summary.slice(0, 118)}…` : summary
})

watch(
  () => props.branch?.id,
  () => {
    isExpanded.value = false
  }
)
</script>

<style scoped lang="less">
.inspect-panel {
  padding: 20px;
  border-radius: 24px;
  border: 1px solid color-mix(in srgb, var(--gray-120) 86%, transparent);
  background:
    radial-gradient(circle at top right, color-mix(in srgb, var(--main-100) 18%, transparent), transparent 34%),
    linear-gradient(180deg, color-mix(in srgb, var(--gray-0) 94%, transparent), var(--main-10));
  box-shadow: 0 18px 38px color-mix(in srgb, var(--gray-1000) 7%, transparent);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.panel-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.eyebrow {
  margin: 0 0 8px;
  color: var(--main-600);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.panel-header h3 {
  margin: 0;
  color: var(--gray-1000);
  font-size: 1.15rem;
  line-height: 1.45;
}

.state-pill,
.meta-chip {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--main-20) 82%, var(--gray-0));
  color: var(--main-700);
  font-size: 12px;
  font-weight: 700;
}

.detail-toggle {
  border: 1px solid color-mix(in srgb, var(--gray-150) 70%, transparent);
  background: color-mix(in srgb, var(--gray-0) 88%, transparent);
  color: var(--gray-700);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  cursor: pointer;
}

.detail-toggle:hover {
  color: var(--main-700);
  border-color: color-mix(in srgb, var(--main-300) 70%, transparent);
}

.lead,
.summary,
.empty-copy {
  color: var(--gray-600);
  line-height: 1.75;
}

.lead {
  margin: 12px 0 0;
  font-weight: 600;
}

.summary {
  margin: 10px 0 0;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.section-block {
  margin-top: 16px;
  padding: 14px 16px;
  border-radius: 18px;
  background: color-mix(in srgb, var(--gray-0) 84%, var(--main-10));
  border: 1px solid color-mix(in srgb, var(--gray-120) 72%, transparent);
}

.section-block.subtle {
  background: color-mix(in srgb, var(--main-10) 84%, var(--gray-0));
}

.section-block strong {
  display: block;
  color: var(--gray-900);
  font-size: 14px;
}

.section-block p {
  margin: 8px 0 0;
  color: var(--gray-600);
  line-height: 1.75;
}

.detail-grid {
  display: grid;
  gap: 12px;
  margin: 16px 0 0;
}

.detail-grid dt {
  color: var(--gray-500);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.detail-grid dd {
  margin: 4px 0 0;
  color: var(--gray-900);
  line-height: 1.7;
}
</style>
