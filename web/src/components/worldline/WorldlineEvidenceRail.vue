<template>
  <section class="inspect-panel evidence-rail">
    <div class="panel-header">
      <div>
        <p class="eyebrow">证据轨</p>
        <h3>这条世界线站在什么依据之上</h3>
      </div>
      <span class="count-pill">{{ evidenceRefs.length }} 条支撑</span>
    </div>

    <div v-if="evidenceRefs.length" class="evidence-list">
      <article
        v-for="(item, index) in evidenceRefs"
        :key="`${item.id || item.title || 'evidence'}-${index}`"
        class="evidence-item"
      >
        <div class="evidence-top">
          <strong>{{ item.title }}</strong>
          <small>{{ item.typeLabel || item.type }}</small>
        </div>
        <p>{{ item.summary || '这条证据解释了为什么当前世界线值得继续推进。' }}</p>
        <dl v-if="item.evidenceId || item.sourceUri || item.page || item.lineStart" class="evidence-meta">
          <div v-if="item.evidenceId">
            <dt>ID</dt>
            <dd>{{ item.evidenceId }}</dd>
          </div>
          <div v-if="item.sourceUri">
            <dt>来源</dt>
            <dd>{{ item.sourceUri }}</dd>
          </div>
          <div v-if="item.page || item.lineStart">
            <dt>位置</dt>
            <dd>{{ formatLocation(item) }}</dd>
          </div>
        </dl>
      </article>
    </div>

    <p v-else class="empty-copy">当前还没有更多证据条目，后续会由知识库、图谱和文档补充。</p>
  </section>
</template>

<script setup>
defineProps({
  evidenceRefs: {
    type: Array,
    default: () => []
  }
})

const formatLocation = (item = {}) => {
  const parts = []
  if (item.page) parts.push(`page ${item.page}`)
  if (item.lineStart && item.lineEnd) parts.push(`line ${item.lineStart}-${item.lineEnd}`)
  else if (item.lineStart) parts.push(`line ${item.lineStart}`)
  return parts.join(' / ')
}
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
  font-size: 1.08rem;
}

.count-pill {
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

.evidence-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 14px;
}

.evidence-item {
  padding: 14px 16px;
  border-radius: 18px;
  background: color-mix(in srgb, var(--gray-0) 84%, var(--main-10));
  border: 1px solid color-mix(in srgb, var(--gray-120) 72%, transparent);
}

.evidence-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.evidence-top strong {
  color: var(--gray-900);
  line-height: 1.6;
}

.evidence-top small {
  color: var(--main-700);
  font-weight: 700;
  white-space: nowrap;
}

.evidence-item p,
.empty-copy {
  margin: 8px 0 0;
  color: var(--gray-600);
  line-height: 1.75;
}

.evidence-meta {
  display: grid;
  gap: 6px;
  margin: 10px 0 0;
  color: var(--gray-600);
  font-size: 12px;
}

.evidence-meta div {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr);
  gap: 8px;
}

.evidence-meta dt {
  color: var(--gray-500);
  font-weight: 700;
}

.evidence-meta dd {
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
</style>
