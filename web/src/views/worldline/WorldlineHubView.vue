<template>
  <div class="worldline-hub-view">
    <section class="hub-shell">
      <header class="hub-header">
        <div class="header-copy">
          <p class="eyebrow">WORLDLINE COMMAND</p>
          <h1>证据驱动的世界线工作台</h1>
          <p class="subtitle">
            LLM Wiki 是主线，RAG 只做证据候选召回；Temporal Evidence Graph 用来解释事实如何分叉、变化和收束。
          </p>
        </div>

        <div class="header-actions">
          <router-link class="ghost-link" to="/">首页</router-link>
          <router-link class="ghost-link" to="/worldline/agent">Agent</router-link>
          <router-link class="ghost-link" to="/themes">模块</router-link>
          <a v-if="docsUrl" class="ghost-link" :href="docsUrl" target="_blank" rel="noopener noreferrer">文档</a>
        </div>
      </header>

      <main class="hub-grid">
        <section class="launch-panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">LAUNCH</p>
              <h2>选择真实知识模块并生成基础世界线</h2>
            </div>
            <span class="panel-badge">{{ moduleBadgeText }}</span>
          </div>

          <div v-if="hasAvailableThemes" class="module-grid" role="tablist" aria-label="世界线模块">
            <button
              v-for="theme in themes"
              :key="theme.id"
              class="module-tile"
              :class="{ active: theme.id === selectedThemeId }"
              type="button"
              @click="selectTheme(theme.id)"
            >
              <span class="module-title">{{ theme.name }}</span>
              <small>{{ theme.subtitle || 'Live knowledge bridge' }}</small>
              <em>{{ moduleTypeLabel(theme) }}</em>
            </button>
          </div>

          <div v-else class="empty-state">
            <strong>暂无可用 Worldline 模块</strong>
            <p>旧主题和演示入口已移除。请先在主题分区添加真实知识模块，再进入工作台生成世界线。</p>
            <router-link class="secondary-button" to="/themes">
              <Plus :size="17" />
              <span>添加自定义模块</span>
            </router-link>
          </div>

          <label class="question-label" for="worldline-hub-question">问题起点</label>
          <textarea
            id="worldline-hub-question"
            v-model="questionDraft"
            class="question-input"
            rows="4"
            :placeholder="placeholderQuestion"
          />

          <div class="question-actions">
            <button
              class="primary-button"
              type="button"
              :disabled="!activeThemeSupported"
              @click="openWorkbench()"
            >
              生成世界线
            </button>
            <button
              v-if="canResumeCurrentTheme"
              class="secondary-button"
              type="button"
              @click="resumeCurrentTheme()"
            >
              继续上次分支
            </button>
          </div>
        </section>

        <aside class="status-panel">
          <div class="status-block">
            <p class="eyebrow">ACTIVE MODULE</p>
            <h3>{{ activeTheme?.name || '未选择模块' }}</h3>
            <p>{{ compactThemeDescription }}</p>
            <div class="tag-list">
              <span v-for="tag in compactTags" :key="tag">{{ tag }}</span>
            </div>
          </div>

          <div class="status-matrix">
            <div>
              <strong>{{ hasLiveBridge ? 'Live' : '-' }}</strong>
              <span>Bridge</span>
            </div>
            <div>
              <strong>{{ worldlineStore.branchCount || '-' }}</strong>
              <span>Branches</span>
            </div>
            <div>
              <strong>{{ worldlineStore.quality.status || 'pending' }}</strong>
              <span>Quality</span>
            </div>
            <div>
              <strong>{{ worldlineStore.protocolVersion }}</strong>
              <span>Protocol</span>
            </div>
          </div>

          <div class="pipeline-list">
            <p class="eyebrow">CORE SURFACES</p>
            <div v-for="item in surfaces" :key="item.title" class="pipeline-item">
              <strong>{{ item.title }}</strong>
              <span>{{ item.detail }}</span>
            </div>
          </div>
        </aside>
      </main>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useInfoStore } from '@/stores/info'
import { useWorldlineContextStore } from '@/stores/worldlineContext'
import { getWorldlineDefaultQuestion } from '@/data/worldline'
import { hasWorldlineLiveBridge, resolveThemeKnowledgeDbId } from '@/apis/worldline_api'
import { Plus } from 'lucide-vue-next'

const router = useRouter()
const infoStore = useInfoStore()
const worldlineStore = useWorldlineContextStore()

const questionDraft = ref('')
const selectedThemeId = ref('')
const fallbackQuestion = '描述你的目标、约束和证据来源，让 Worldline 展开几条可验证分支。'

const isWorldlineEntry = (theme = {}) => hasWorldlineLiveBridge(theme)
const themes = computed(() => (infoStore.themes || []).filter((theme) => isWorldlineEntry(theme)))
const docsUrl = computed(() => infoStore.docsUrl || '')
const hasAvailableThemes = computed(() => themes.value.length > 0)
const moduleBadgeText = computed(() => (themes.value.length ? `${themes.value.length} 个模块` : '等待接入'))
const activeTheme = computed(
  () => themes.value.find((theme) => theme.id === selectedThemeId.value) || themes.value[0] || null
)
const hasLiveBridge = computed(() => Boolean(activeTheme.value && hasWorldlineLiveBridge(activeTheme.value)))
const activeThemeSupported = computed(() => Boolean(activeTheme.value?.id && hasWorldlineLiveBridge(activeTheme.value)))
const compactThemeDescription = computed(() => {
  const description = (activeTheme.value?.description || '').trim()
  if (!description) return '当前没有真实知识模块。添加模块后，Worldline 会生成证据、Wiki、图谱与时间事实同屏可见的分支。'
  return description.length > 96 ? `${description.slice(0, 95)}...` : description
})
const compactTags = computed(() => (activeTheme.value?.tags || []).slice(0, 5))
const placeholderQuestion = computed(() =>
  getWorldlineDefaultQuestion(activeTheme.value?.id || selectedThemeId.value || '', fallbackQuestion)
)
const canResumeCurrentTheme = computed(
  () =>
    activeThemeSupported.value &&
    worldlineStore.hasBranches &&
    worldlineStore.themeId &&
    worldlineStore.themeId === selectedThemeId.value
)
const surfaces = [
  {
    title: 'Worldline Stage',
    detail: '左到右分叉与收束的青金发光世界线舞台'
  },
  {
    title: 'Evidence Rail',
    detail: 'source uri、page、line、bbox、Wiki refs 同屏可见'
  },
  {
    title: 'Temporal Scrubber',
    detail: 'Source、Wiki、Graph、Gate 快照可切换'
  },
  {
    title: 'Agent Handoff',
    detail: '将选中分支上下文交给受控 Agent 继续验证'
  }
]

const moduleTypeLabel = (theme = {}) => {
  if (hasWorldlineLiveBridge(theme)) return 'Live Bridge'
  return 'Worldline'
}

const ensureSelectedTheme = () => {
  if (selectedThemeId.value && themes.value.some((theme) => theme.id === selectedThemeId.value)) return

  const storedThemeId =
    worldlineStore.themeId && themes.value.some((theme) => theme.id === worldlineStore.themeId)
      ? worldlineStore.themeId
      : ''
  const primaryThemeId =
    infoStore.primaryTheme?.id && themes.value.some((theme) => theme.id === infoStore.primaryTheme.id)
      ? infoStore.primaryTheme.id
      : ''

  selectedThemeId.value = storedThemeId || primaryThemeId || themes.value[0]?.id || ''
}

const syncQuestionDraft = (themeId = selectedThemeId.value, { preserveExisting = false } = {}) => {
  if (preserveExisting && questionDraft.value) return

  if (worldlineStore.themeId && worldlineStore.themeId === themeId) {
    questionDraft.value = worldlineStore.questionDraft || worldlineStore.rootQuestion || ''
  }

  if (questionDraft.value) return
  questionDraft.value = getWorldlineDefaultQuestion(themeId, fallbackQuestion)
}

const selectTheme = (themeId) => {
  selectedThemeId.value = themeId
  syncQuestionDraft(themeId)
}

const buildWorkbenchLocation = () => {
  const targetThemeId = selectedThemeId.value || themes.value[0]?.id || ''

  return {
    path: targetThemeId ? `/worldline/${targetThemeId}` : '/worldline',
    query: {
      ...(questionDraft.value.trim() ? { question: questionDraft.value.trim() } : {}),
      ...(resolveThemeKnowledgeDbId(activeTheme.value)
        ? { knowledge_db_id: resolveThemeKnowledgeDbId(activeTheme.value) }
        : {})
    }
  }
}

const openWorkbench = async () => {
  if (!activeThemeSupported.value) return
  await router.push(buildWorkbenchLocation())
}

const resumeCurrentTheme = async () => {
  if (!activeThemeSupported.value) return
  await router.push({ path: `/worldline/${selectedThemeId.value || activeTheme.value?.id || ''}` })
}

watch(themes, () => {
  ensureSelectedTheme()
  syncQuestionDraft(selectedThemeId.value, { preserveExisting: true })
})

watch(selectedThemeId, (themeId, previousThemeId) => {
  if (!themeId || themeId === previousThemeId) return
  syncQuestionDraft(themeId)
})

onMounted(async () => {
  await infoStore.loadInfoConfig()
  ensureSelectedTheme()
  syncQuestionDraft(selectedThemeId.value, { preserveExisting: true })
})
</script>

<style scoped lang="less">
.worldline-hub-view {
  min-height: 100vh;
  color: var(--wl-text);
  background: var(--wl-page-bg);
}

.hub-shell {
  max-width: 1500px;
  margin: 0 auto;
  padding: 24px 24px 44px;
}

.hub-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 18px;
}

.header-copy h1 {
  max-width: 760px;
  margin: 0;
  color: var(--wl-text);
  font-size: 52px;
  font-weight: 950;
  line-height: 1.08;
  letter-spacing: 0;
}

.subtitle {
  max-width: 760px;
  margin: 12px 0 0;
  color: var(--wl-muted);
  line-height: 1.75;
}

.eyebrow {
  margin: 0 0 8px;
  color: var(--wl-gold);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0;
  text-transform: uppercase;
}

.header-actions,
.question-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.ghost-link,
.primary-button,
.secondary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 40px;
  padding: 0 14px;
  border-radius: var(--wl-radius-sm);
  border: 1px solid var(--wl-border);
  color: var(--wl-text-soft);
  text-decoration: none;
  font-weight: 800;
  cursor: pointer;
}

.ghost-link,
.secondary-button {
  background: rgba(var(--wl-cyan-rgb), 0.06);
}

.primary-button {
  border-color: var(--wl-border-gold);
  background: linear-gradient(135deg, rgba(var(--wl-gold-rgb), 0.92), rgba(var(--wl-cyan-rgb), 0.7));
  color: var(--wl-ink);
}

.primary-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hub-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.65fr);
  gap: 16px;
}

.launch-panel,
.status-panel {
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background: var(--wl-panel);
  box-shadow: var(--wl-shadow);
}

.launch-panel {
  padding: 20px;
}

.status-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
}

.panel-head h2,
.status-block h3 {
  margin: 0;
  color: var(--wl-text);
  font-size: 20px;
  font-weight: 950;
}

.panel-badge {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  background: rgba(var(--wl-gold-rgb), 0.1);
  color: var(--wl-gold-soft);
  font-size: 12px;
  font-weight: 900;
  white-space: nowrap;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 10px;
  margin-top: 18px;
}

.module-tile {
  min-height: 118px;
  padding: 14px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background: rgba(255, 255, 255, 0.035);
  color: var(--wl-text-soft);
  cursor: pointer;
  text-align: left;
}

.module-tile.active {
  border-color: var(--wl-border-gold);
  background:
    linear-gradient(90deg, rgba(var(--wl-gold-rgb), 0.12), transparent 45%),
    rgba(var(--wl-cyan-rgb), 0.07);
}

.module-title,
.module-tile small,
.module-tile em {
  display: block;
}

.module-title {
  color: var(--wl-text);
  font-size: 15px;
  font-weight: 900;
}

.module-tile small {
  margin-top: 8px;
  color: var(--wl-muted);
  line-height: 1.5;
}

.module-tile em {
  margin-top: 12px;
  color: var(--wl-gold);
  font-size: 11px;
  font-style: normal;
  font-weight: 900;
  text-transform: uppercase;
}

.empty-state {
  display: grid;
  gap: 10px;
  margin-top: 18px;
  padding: 16px;
  border: 1px dashed var(--wl-border-strong);
  border-radius: var(--wl-radius);
  color: var(--wl-muted);
}

.empty-state strong {
  color: var(--wl-text);
  font-weight: 900;
}

.empty-state p {
  margin: 0;
  line-height: 1.7;
}

.empty-state .secondary-button {
  justify-self: flex-start;
}

.question-label {
  display: block;
  margin-top: 18px;
  color: var(--wl-gold-soft);
  font-size: 13px;
  font-weight: 900;
}

.question-input {
  width: 100%;
  margin-top: 10px;
  padding: 14px 16px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background: rgba(2, 5, 10, 0.72);
  color: var(--wl-text);
  line-height: 1.7;
  resize: vertical;
}

.question-input:focus {
  outline: none;
  border-color: var(--wl-border-gold);
  box-shadow: var(--wl-focus-ring);
}

.question-actions {
  margin-top: 14px;
}

.status-block p {
  margin: 10px 0 0;
  color: var(--wl-muted);
  line-height: 1.7;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.tag-list span {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 9px;
  border: 1px solid var(--wl-border);
  border-radius: 999px;
  color: var(--wl-text-soft);
  font-size: 12px;
  font-weight: 800;
}

.status-matrix {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.status-matrix div,
.pipeline-item {
  padding: 12px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(255, 255, 255, 0.035);
}

.status-matrix strong,
.status-matrix span,
.pipeline-item strong,
.pipeline-item span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-matrix strong {
  color: var(--wl-text);
  font-size: 18px;
  font-weight: 900;
}

.status-matrix span,
.pipeline-item span {
  color: var(--wl-muted-soft);
  font-size: 12px;
}

.pipeline-list {
  display: grid;
  gap: 9px;
}

.pipeline-item strong {
  color: var(--wl-text);
  font-weight: 900;
}

@media (max-width: 980px) {
  .hub-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 680px) {
  .hub-shell {
    padding: 18px 14px 34px;
  }

  .hub-header {
    flex-direction: column;
  }

  .header-copy h1 {
    font-size: 38px;
  }

  .header-actions,
  .question-actions {
    width: 100%;
  }

  .ghost-link,
  .primary-button,
  .secondary-button {
    flex: 1;
  }

  .panel-head {
    flex-direction: column;
  }

  .status-matrix {
    grid-template-columns: 1fr;
  }
}
</style>
