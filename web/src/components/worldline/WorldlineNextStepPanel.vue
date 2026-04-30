<template>
  <section class="inspect-panel next-step-panel">
    <div class="panel-header">
      <div>
        <p class="eyebrow">下一步</p>
        <h3>选中一条线后，你可以立刻继续推进</h3>
      </div>
      <span class="count-pill">{{ actions.length }} 个动作</span>
    </div>

    <div v-if="actions.length" class="action-list">
      <button
        v-for="action in actions"
        :key="action.id"
        class="action-item"
        :class="action.emphasis || 'ghost'"
        type="button"
        @click="$emit('trigger', action)"
      >
        <div class="action-copy">
          <strong>{{ action.label }}</strong>
          <small>{{ action.description }}</small>
        </div>
        <span class="action-tag">{{ getTargetLabel(action.targetType) }}</span>
      </button>
    </div>

    <p v-else class="empty-copy">先选中一条世界线，再决定继续生成、进入对话或查看图谱。</p>
  </section>
</template>

<script setup>
defineProps({
  actions: {
    type: Array,
    default: () => []
  }
})

defineEmits(['trigger'])

const targetLabelMap = {
  continue: '继续生成',
  chat: '进入对话',
  graph: '查看图谱',
  theme: '返回模块'
}

const getTargetLabel = (value) => targetLabelMap[value] || value || '下一步'
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

.count-pill,
.action-tag {
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

.action-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 14px;
}

.action-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  width: 100%;
  min-height: 62px;
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid color-mix(in srgb, var(--gray-120) 84%, transparent);
  background: color-mix(in srgb, var(--gray-0) 88%, var(--main-10));
  color: var(--gray-900);
  cursor: pointer;
  text-align: left;
  transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
}

.action-item.primary {
  border-color: color-mix(in srgb, var(--main-300) 88%, transparent);
  background: linear-gradient(180deg, color-mix(in srgb, var(--main-20) 78%, var(--gray-0)), color-mix(in srgb, var(--gray-0) 88%, transparent));
}

.action-item:hover {
  transform: translateY(-1px);
  border-color: color-mix(in srgb, var(--main-400) 84%, transparent);
  box-shadow: 0 14px 24px color-mix(in srgb, var(--main-500) 10%, transparent);
}

.action-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.action-copy strong {
  color: var(--gray-1000);
  line-height: 1.5;
}

.action-copy small,
.empty-copy {
  color: var(--gray-600);
  line-height: 1.7;
}
</style>
