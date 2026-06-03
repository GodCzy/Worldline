<template>
  <section class="question-bar">
    <div class="bar-header">
      <div class="header-copy">
        <p class="eyebrow">世界线控制台</p>
        <h2>先展开基础分支，再选主线继续生成</h2>
      </div>

      <div class="meta-strip">
        <span class="meta-chip">{{ themeName || '未选择模块' }}</span>
        <span class="meta-chip">{{ modeLabel }}</span>
        <span class="meta-chip">{{ branchCount }} 条分支</span>
        <span class="meta-chip">第 {{ generationRound || 1 }} 轮</span>
      </div>
    </div>

    <div class="controller-shell">
      <div class="controller-main">
        <label class="question-label" for="worldline-question-input">问题起点</label>
        <textarea
          id="worldline-question-input"
          :value="modelValue"
          class="question-input"
          rows="3"
          placeholder="输入你的目标与限制，让模型先展开几条未来分支。"
          @input="$emit('update:modelValue', $event.target.value)"
        />

        <div class="hint-row">
          <span class="hint-pill">先生成基础分支</span>
          <span class="hint-pill">再选择主线</span>
        </div>
      </div>

      <aside class="controller-side">
        <div class="focus-box">
          <p class="focus-label">当前焦点</p>
          <strong>{{ activeBranchTitle || '尚未锁定主线' }}</strong>
          <span>
            {{ activeBranchTitle ? '继续沿当前主线推进，生成下一层世界线。' : '先生成基础世界线，再点击一条分支进入聚焦状态。' }}
          </span>
        </div>

        <button class="generate-button" type="button" :disabled="busy" @click="$emit('generate')">
          {{ busy ? '正在展开世界线…' : generateLabel }}
        </button>
      </aside>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  busy: {
    type: Boolean,
    default: false
  },
  branchCount: {
    type: Number,
    default: 0
  },
  activeBranchTitle: {
    type: String,
    default: ''
  },
  themeName: {
    type: String,
    default: ''
  },
  generationMode: {
    type: String,
    default: 'base'
  },
  generationRound: {
    type: Number,
    default: 1
  }
})

defineEmits(['update:modelValue', 'generate'])

const modeLabel = computed(() => (props.generationMode === 'focused' ? '聚焦生成' : '基础生成'))

const generateLabel = computed(() =>
  props.generationMode === 'focused' ? '重新生成当前主线后续' : '生成基础世界线'
)
</script>

<style scoped lang="less">
.question-bar {
  padding: 18px 20px;
  border-radius: var(--wl-radius);
  border: 1px solid var(--wl-border);
  background:
    radial-gradient(circle at top left, rgba(var(--wl-cyan-rgb), 0.12), transparent 34%),
    var(--wl-panel);
  box-shadow: var(--wl-shadow-soft);
}

.bar-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.header-copy h2 {
  margin: 0;
  color: var(--wl-text);
  font-size: 1.05rem;
  line-height: 1.3;
}

.eyebrow {
  margin: 0 0 8px;
  color: var(--wl-gold);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.meta-strip {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.meta-chip,
.hint-pill {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  background: rgba(var(--wl-cyan-rgb), 0.07);
  color: var(--wl-text-soft);
  font-size: 11px;
  font-weight: 700;
}

.controller-shell {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) 240px;
  gap: 16px;
  margin-top: 18px;
}

.question-label,
.focus-label {
  display: block;
  color: var(--wl-gold);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.question-input {
  width: 100%;
  margin-top: 10px;
  padding: 12px 14px;
  border-radius: var(--wl-radius-sm);
  border: 1px solid var(--wl-border);
  background: rgba(2, 5, 10, 0.72);
  color: var(--wl-text);
  line-height: 1.6;
  resize: vertical;
}

.question-input:focus {
  outline: none;
  border-color: var(--wl-border-gold);
  box-shadow: var(--wl-focus-ring);
}

.hint-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.controller-side {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.focus-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 100%;
  padding: 16px;
  border-radius: var(--wl-radius);
  background:
    radial-gradient(circle at top right, rgba(var(--wl-gold-rgb), 0.12), transparent 32%),
    rgba(2, 5, 10, 0.56);
  border: 1px solid var(--wl-border);
}

.focus-box strong {
  color: var(--wl-text);
  font-size: 1rem;
  line-height: 1.5;
}

.focus-box span {
  color: var(--wl-muted);
  line-height: 1.7;
}

.generate-button {
  min-height: 48px;
  border: none;
  border-radius: var(--wl-radius-sm);
  background: linear-gradient(135deg, rgba(var(--wl-gold-rgb), 0.92), rgba(var(--wl-cyan-rgb), 0.7));
  color: var(--wl-ink);
  font-weight: 700;
  cursor: pointer;
}

.generate-button:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

@media (max-width: 980px) {
  .bar-header,
  .controller-shell {
    grid-template-columns: 1fr;
    display: grid;
  }

  .meta-strip {
    justify-content: flex-start;
  }
}
</style>
