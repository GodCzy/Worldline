<template>
  <div class="worldline-hub-view">
    <section class="workspace-shell">
      <header class="workspace-header">
        <div class="workspace-copy">
          <p class="eyebrow">WORLDLINE</p>
          <h1>世界线</h1>
          <p class="subtitle">先选模块，再展开世界线。</p>
        </div>

        <div class="header-actions">
          <router-link class="ghost-link" to="/themes">主题分区</router-link>
          <a
            v-if="docsUrl"
            class="ghost-link"
            :href="docsUrl"
            target="_blank"
            rel="noopener noreferrer"
          >
            文档中心
          </a>
        </div>
      </header>

      <main class="workspace-main">
        <section class="workspace-panel controller-panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">模块选择</p>
              <h2>先选模块，再生成基础世界线</h2>
            </div>
            <span class="panel-badge">{{ themes.length }} 个模块</span>
          </div>

          <div v-if="hasAvailableThemes" class="module-strip" role="tablist" aria-label="世界线模块">
            <button
              v-for="theme in themes"
              :key="theme.id"
              class="module-pill"
              :class="{ active: theme.id === selectedThemeId }"
              type="button"
              @click="selectTheme(theme.id)"
            >
              <span class="module-pill-title">{{ theme.name }}</span>
              <small>{{ theme.subtitle || '世界线模块' }}</small>
            </button>
          </div>

          <div v-else class="empty-state">
            当前没有已接入世界线适配器的模块。
          </div>

          <div class="question-panel">
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
                :class="{ disabled: !activeThemeSupported }"
                type="button"
                :disabled="!activeThemeSupported"
                @click="openWorkbench()"
              >
                生成基础世界线
              </button>
              <button
                v-if="canResumeCurrentTheme"
                class="secondary-button"
                type="button"
                @click="resumeCurrentTheme()"
              >
                继续上次世界线
              </button>
            </div>
          </div>
        </section>

        <aside class="workspace-panel module-panel">
          <div class="module-card">
            <p class="eyebrow">当前模块</p>
            <h3>{{ activeTheme?.name || '未选择模块' }}</h3>
            <p class="module-description">
              {{ compactThemeDescription }}
            </p>

            <div v-if="compactHighlights.length" class="highlight-list">
              <div v-for="item in compactHighlights" :key="item" class="highlight-item">
                {{ item }}
              </div>
            </div>

            <div v-if="compactTags.length" class="tag-list">
              <span v-for="tag in compactTags" :key="tag">{{ tag }}</span>
            </div>
            <details
              v-if="remainingHighlights.length || remainingTags.length || activeTheme?.description"
              class="more-details"
            >
              <summary>查看更多</summary>
              <p v-if="activeTheme?.description">{{ activeTheme.description }}</p>
              <div v-if="remainingHighlights.length" class="highlight-list">
                <div v-for="item in remainingHighlights" :key="item" class="highlight-item">
                  {{ item }}
                </div>
              </div>
              <div v-if="remainingTags.length" class="tag-list">
                <span v-for="tag in remainingTags" :key="tag">{{ tag }}</span>
              </div>
            </details>
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
import { getWorldlineDefaultQuestion, hasWorldlineAdapter } from '@/data/worldline'

const router = useRouter()
const infoStore = useInfoStore()
const worldlineStore = useWorldlineContextStore()

const questionDraft = ref('')
const selectedThemeId = ref('')
const fallbackQuestion =
  '请描述你的目标、偏好和限制，让世界线先展开几条未来分支。'

const themes = computed(() => (infoStore.themes || []).filter((theme) => hasWorldlineAdapter(theme.id)))
const docsUrl = computed(() => infoStore.docsUrl || '')
const hasAvailableThemes = computed(() => themes.value.length > 0)
const activeTheme = computed(
  () => themes.value.find((theme) => theme.id === selectedThemeId.value) || themes.value[0] || null
)
const activeThemeSupported = computed(() => Boolean(activeTheme.value?.id))
const compactThemeDescription = computed(() => {
  const description = (activeTheme.value?.description || '').trim()
  if (!description) return '围绕当前模块，先生成基础分支再继续推进。'
  return description.length > 64 ? `${description.slice(0, 63)}…` : description
})
const compactHighlights = computed(() => (activeTheme.value?.highlights || []).slice(0, 2))
const remainingHighlights = computed(() => (activeTheme.value?.highlights || []).slice(2))
const compactTags = computed(() => (activeTheme.value?.tags || []).slice(0, 3))
const remainingTags = computed(() => (activeTheme.value?.tags || []).slice(3))
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

const ensureSelectedTheme = () => {
  if (selectedThemeId.value) {
    return
  }

  const storedThemeId =
    worldlineStore.themeId &&
    themes.value.some((theme) => theme.id === worldlineStore.themeId)
      ? worldlineStore.themeId
      : ''
  const primaryThemeId =
    infoStore.primaryTheme?.id && hasWorldlineAdapter(infoStore.primaryTheme.id)
      ? infoStore.primaryTheme.id
      : ''

  selectedThemeId.value = storedThemeId || primaryThemeId || themes.value[0]?.id || ''
}

const syncQuestionDraft = (themeId = selectedThemeId.value, { preserveExisting = false } = {}) => {
  if (preserveExisting && questionDraft.value) {
    return
  }

  if (worldlineStore.themeId && worldlineStore.themeId === themeId) {
    questionDraft.value = worldlineStore.questionDraft || worldlineStore.rootQuestion || ''
  }

  if (questionDraft.value) {
    return
  }

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
    query: questionDraft.value.trim() ? { question: questionDraft.value.trim() } : {}
  }
}

const openWorkbench = async () => {
  if (!activeThemeSupported.value) {
    return
  }

  await router.push(buildWorkbenchLocation())
}

const resumeCurrentTheme = async () => {
  if (!activeThemeSupported.value) {
    return
  }

  await router.push({
    path: `/worldline/${selectedThemeId.value || activeTheme.value?.id || ''}`
  })
}

watch(themes, () => {
  ensureSelectedTheme()
  syncQuestionDraft(selectedThemeId.value, { preserveExisting: true })
})

watch(selectedThemeId, (themeId, previousThemeId) => {
  if (!themeId || themeId === previousThemeId) {
    return
  }

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
  background:
    radial-gradient(circle at top left, color-mix(in srgb, var(--main-100) 45%, transparent), transparent 42%),
    radial-gradient(circle at top right, color-mix(in srgb, var(--main-200) 22%, transparent), transparent 28%),
    linear-gradient(180deg, var(--main-10), var(--gray-10));
}

.workspace-shell {
  max-width: 1480px;
  margin: 0 auto;
  padding: 28px 28px 56px;
}

.workspace-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 20px;
}

.workspace-copy h1 {
  margin: 0;
  color: var(--gray-1000);
  font-size: clamp(2.2rem, 4vw, 3.6rem);
  letter-spacing: -0.03em;
}

.subtitle {
  max-width: 560px;
  margin: 10px 0 0;
  color: var(--gray-600);
  line-height: 1.8;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.ghost-link {
  display: inline-flex;
  align-items: center;
  min-height: 40px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--gray-150) 90%, transparent);
  background: color-mix(in srgb, var(--gray-0) 84%, transparent);
  color: var(--gray-700);
  text-decoration: none;
  font-weight: 600;
}

.workspace-main {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(320px, 0.85fr);
  gap: 18px;
}

.workspace-panel {
  border: 1px solid color-mix(in srgb, var(--gray-120) 88%, transparent);
  border-radius: 28px;
  background: color-mix(in srgb, var(--gray-0) 92%, transparent);
  box-shadow: 0 24px 56px color-mix(in srgb, var(--gray-1000) 6%, transparent);
  backdrop-filter: blur(18px);
}

.controller-panel {
  padding: 26px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
}

.panel-head h2,
.module-card h3 {
  margin: 0;
  color: var(--gray-1000);
  font-size: 1.35rem;
}

.panel-badge {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--main-20) 84%, var(--gray-0));
  color: var(--main-700);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.eyebrow {
  margin: 0 0 8px;
  color: var(--main-600);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.module-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}

.module-pill {
  display: inline-flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 3px;
  min-width: 180px;
  padding: 14px 16px;
  border-radius: 20px;
  border: 1px solid color-mix(in srgb, var(--gray-120) 88%, transparent);
  background: linear-gradient(180deg, var(--gray-0), var(--main-10));
  color: var(--gray-800);
  cursor: pointer;
  transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
}

.module-pill.active {
  border-color: color-mix(in srgb, var(--main-300) 88%, transparent);
  box-shadow: 0 14px 28px color-mix(in srgb, var(--main-500) 12%, transparent);
  transform: translateY(-1px);
}

.module-pill-title {
  font-size: 14px;
  font-weight: 700;
}

.module-pill small {
  color: var(--gray-600);
  line-height: 1.5;
}

.empty-state {
  margin-top: 20px;
  padding: 16px 18px;
  border-radius: 20px;
  border: 1px dashed color-mix(in srgb, var(--gray-150) 90%, transparent);
  color: var(--gray-600);
}

.question-panel {
  margin-top: 22px;
  padding: 18px;
  border-radius: 24px;
  background:
    radial-gradient(circle at top right, color-mix(in srgb, var(--main-100) 32%, transparent), transparent 32%),
    linear-gradient(180deg, color-mix(in srgb, var(--gray-0) 92%, transparent), var(--main-10));
  border: 1px solid color-mix(in srgb, var(--gray-120) 88%, transparent);
}

.question-label {
  display: block;
  color: var(--gray-800);
  font-size: 14px;
  font-weight: 700;
}

.question-input {
  width: 100%;
  margin-top: 12px;
  padding: 16px 18px;
  border-radius: 20px;
  border: 1px solid color-mix(in srgb, var(--gray-150) 88%, transparent);
  background: color-mix(in srgb, var(--gray-0) 92%, transparent);
  color: var(--gray-1000);
  line-height: 1.7;
  resize: vertical;
}

.question-input:focus {
  outline: none;
  border-color: color-mix(in srgb, var(--main-400) 88%, transparent);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--main-100) 34%, transparent);
}

.tag-list,
.highlight-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hint-chip,
.tag-list span {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 11px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--main-20) 82%, var(--gray-0));
  color: var(--main-700);
  font-size: 12px;
  font-weight: 700;
}

.question-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 18px;
}

.primary-button,
.secondary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 46px;
  padding: 0 18px;
  border-radius: 999px;
  border: 1px solid transparent;
  cursor: pointer;
  font-weight: 700;
}

.primary-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.primary-button {
  background: linear-gradient(135deg, var(--main-700), var(--main-500));
  color: var(--gray-0);
}

.secondary-button {
  background: color-mix(in srgb, var(--gray-0) 90%, transparent);
  border-color: color-mix(in srgb, var(--gray-150) 88%, transparent);
  color: var(--gray-800);
}

.module-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
}

.module-card,
.resume-card {
  padding: 18px;
  border-radius: 22px;
  background: linear-gradient(180deg, color-mix(in srgb, var(--gray-0) 92%, transparent), var(--main-10));
  border: 1px solid color-mix(in srgb, var(--gray-120) 84%, transparent);
}

.module-description {
  margin: 12px 0 0;
  color: var(--gray-600);
  line-height: 1.8;
}

.highlight-list {
  margin-top: 16px;
}

.highlight-item {
  padding: 10px 12px;
  border-radius: 16px;
  background: color-mix(in srgb, var(--main-20) 78%, var(--gray-0));
  color: var(--gray-800);
  line-height: 1.6;
}

.tag-list {
  margin-top: 16px;
}

.resume-card ul {
  margin: 12px 0 0;
  padding-left: 18px;
  color: var(--gray-600);
  line-height: 1.8;
}

.more-details {
  margin-top: 14px;

  summary {
    cursor: pointer;
    color: var(--main-700);
    font-size: 13px;
    font-weight: 700;
  }

  p {
    margin: 10px 0 0;
    color: var(--gray-600);
    line-height: 1.7;
  }
}

@media (max-width: 1080px) {
  .workspace-main {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .workspace-shell {
    padding: 20px 16px 40px;
  }

  .workspace-header {
    flex-direction: column;
  }

  .controller-panel,
  .module-panel {
    padding: 18px;
  }

  .question-actions .primary-button,
  .question-actions .secondary-button {
    width: 100%;
  }
}
</style>
