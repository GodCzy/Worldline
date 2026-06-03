<template>
  <div class="worldline-workbench">
    <header class="workbench-header">
      <div class="header-copy">
        <p class="eyebrow">WORLDLINE WORKSPACE</p>
        <h1>世界线工作台</h1>
      </div>

      <div class="header-actions">
        <router-link class="header-link" to="/worldline">返回世界线 Hub</router-link>
        <router-link class="header-link" to="/themes">主题分区</router-link>
      </div>
    </header>

    <section class="module-strip" role="tablist" aria-label="世界线模块">
      <button
        v-for="theme in availableThemes"
        :key="theme.id"
        class="module-pill"
        :class="{ active: theme.id === currentThemeId }"
        type="button"
        @click="switchTheme(theme.id)"
      >
        <span>{{ theme.name }}</span>
      </button>
    </section>

    <main class="workbench-shell">
      <section v-if="!hasThemeId" class="unsupported-shell">
        <div class="unsupported-card">
          <p class="eyebrow">NO THEME SELECTED</p>
          <h2>请先选择一个主题模块</h2>
          <p class="unsupported-description">工作台不再绑定默认演示主题。请先从 Hub 选择已接入真实知识库的模块。</p>
          <div class="unsupported-actions">
            <router-link class="header-link" to="/worldline">返回世界线 Hub</router-link>
            <router-link class="header-link" to="/themes">去主题分区</router-link>
          </div>
        </div>
      </section>

      <template v-else-if="isThemeSupported">
        <section class="stage-column">
          <section class="stage-panel">
            <div v-if="!worldlineStore.hasBranches" class="live-empty-state">
              <p class="eyebrow">NO LIVE BRANCHES</p>
              <h2>{{ workbenchEmptyTitle }}</h2>
              <p>{{ workbenchEmptyDescription }}</p>
            </div>
            <WorldlineBranchCanvas
              v-else
              class="canvas-panel"
              :tree="worldlineStore.tree"
              :active-branch-id="worldlineStore.activeBranchId"
              :selected-node-id="worldlineStore.selectedNodeId"
              :branch-count="worldlineStore.branchCount"
              :display-meta="worldlineStore.displayMeta || {}"
              @select-node="handleNodeSelection"
            />
          </section>

          <WorldlineEvidenceRail :evidence-refs="worldlineStore.evidenceRefs" />

          <section class="selection-brief" v-if="worldlineStore.activeBranch">
            <p class="brief-tag">当前选中</p>
            <p>{{ branchBriefShort }}</p>
          </section>

          <section class="dialogue-panel">
            <div class="dialogue-head">
              <strong>继续生成或深聊这条世界线</strong>
              <p class="dialogue-hint">{{ handoffHint }}</p>
            </div>

            <div class="dialogue-input-wrap">
              <input
                class="dialogue-input"
                :value="questionDraft"
                type="text"
                placeholder="描述目标、限制与偏好"
                @input="questionDraft = $event.target.value"
                @keydown.enter.prevent="generateBaseWorldline"
              />
              <button class="dialogue-send" type="button" :disabled="isGenerating" @click="generateBaseWorldline">
                {{ isGenerating ? '生成中…' : '生成世界线' }}
              </button>
            </div>

            <div class="dialogue-actions">
              <button class="secondary-btn" type="button" @click="goToThemeChat">
                带当前分支继续深聊
              </button>
            </div>
          </section>
        </section>
      </template>

      <section v-else class="unsupported-shell">
        <div class="unsupported-card">
          <p class="eyebrow">UNSUPPORTED THEME</p>
          <h2>{{ unsupportedTitle }}</h2>
          <p class="unsupported-description">{{ unsupportedDescription }}</p>
          <div class="unsupported-actions">
            <router-link class="header-link" to="/worldline">返回世界线 Hub</router-link>
            <router-link class="header-link" to="/themes">返回主题分区</router-link>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useInfoStore } from '@/stores/info'
import { useUserStore } from '@/stores/user'
import { useAgentStore } from '@/stores/agent'
import { useThemeContextStore } from '@/stores/themeContext'
import { useWorldlineContextStore } from '@/stores/worldlineContext'
import {
  getWorldlineDefaultQuestion,
  resolveWorldlineAdapter
} from '@/data/worldline'
import { hasWorldlineLiveBridge, resolveThemeKnowledgeDbId, worldlineApi } from '@/apis/worldline_api'
import WorldlineBranchCanvas from '@/components/worldline/WorldlineBranchCanvas.vue'
import WorldlineEvidenceRail from '@/components/worldline/WorldlineEvidenceRail.vue'

const route = useRoute()
const router = useRouter()
const infoStore = useInfoStore()
const userStore = useUserStore()
const agentStore = useAgentStore()
const themeContextStore = useThemeContextStore()
const worldlineStore = useWorldlineContextStore()
const WORLDLINE_HANDOFF_KEY = 'worldline_agent_handoff'

const questionDraft = ref('')
const isGenerating = ref(false)
const liveStatus = ref({ state: 'idle', message: '' })

const currentThemeId = computed(() => String(route.params.themeId || '').trim().toLowerCase())
const hasThemeId = computed(() => Boolean(currentThemeId.value))
const currentThemeAdapter = computed(() => resolveWorldlineAdapter(currentThemeId.value))
const isWorldlineEntry = (theme = {}) => hasWorldlineLiveBridge(theme)
const configuredThemes = computed(() => (infoStore.themes || []).filter((theme) => isWorldlineEntry(theme)))
const availableThemes = computed(() => configuredThemes.value)
const currentTheme = computed(
  () => availableThemes.value.find((theme) => theme.id === currentThemeId.value) || null
)
const routeKnowledgeDbId = computed(() => {
  const fromQuery = route.query.knowledge_db_id || route.query.db_id
  return typeof fromQuery === 'string' ? fromQuery.trim() : ''
})
const currentKnowledgeDbId = computed(
  () => routeKnowledgeDbId.value || resolveThemeKnowledgeDbId(currentTheme.value)
)
const isLiveSupported = computed(() => Boolean(currentKnowledgeDbId.value))
const isThemeSupported = computed(() => Boolean(currentThemeAdapter.value || isLiveSupported.value))
const incomingQuestion = computed(() => (typeof route.query.question === 'string' ? route.query.question.trim() : ''))
const unsupportedTitle = computed(() =>
  hasThemeId.value ? `主题 ${currentThemeId.value} 尚未接入世界线工作台` : '当前未指定主题'
)
const unsupportedDescription = computed(() => '当前主题没有 live bridge。请先返回选择已接入真实知识库的模块。')
const workbenchEmptyTitle = computed(() =>
  isLiveSupported.value && !userStore.isAdmin ? '需要管理员权限读取真实知识库' : '当前知识库还没有可生成的世界线'
)
const workbenchEmptyDescription = computed(() => {
  if (liveStatus.value.message) return liveStatus.value.message
  if (isLiveSupported.value) {
    return '后端 live facade 没有返回可用分支。请先导入文档、重建 Wiki/Graph，或检查知识库映射。'
  }
  return '当前主题没有 live bridge，无法生成世界线分支。'
})

const branchBrief = computed(() => {
  const branch = worldlineStore.activeBranch
  if (!branch) return ''
  const summary = branch.summary || branch.subtitle || ''
  return summary.length > 60 ? `${summary.slice(0, 59)}…` : summary
})
const branchBriefShort = computed(() => {
  const content = branchBrief.value || ''
  return content.length > 42 ? `${content.slice(0, 41)}…` : content
})
const handoffHint = computed(() => {
  const activeBranch = worldlineStore.activeBranch
  if (!activeBranch) {
    return '先选中一条分支，再把该分支上下文带入智能体继续对话。'
  }

  return `将基于「${activeBranch.title}」继续深聊，并保留当前主题上下文。`
})

const ensureDefaultAgent = async () => {
  if (!agentStore.isInitialized) {
    await agentStore.initialize()
  }
  return agentStore.defaultAgent?.id || agentStore.selectedAgentId || ''
}

const syncThemeContextFromBranch = (branch) => {
  if (!branch?.context) return null
  return themeContextStore.setThemeContext(branch.context)
}

const applyWorldlineResult = (result, source) => {
  worldlineStore.hydrate(result)
  worldlineStore.rememberGenerationSource(source)
  questionDraft.value = result.rootQuestion || questionDraft.value
  syncThemeContextFromBranch(worldlineStore.activeBranch)
}

const hasHydratableBranches = (result) =>
  result && Array.isArray(result.branches) && result.branches.length > 0 && result.tree

const buildEmptyWorldlineResult = (message = '') => ({
  themeId: currentThemeId.value,
  moduleId: currentThemeId.value,
  rootQuestion: questionDraft.value,
  questionDraft: questionDraft.value,
  status: message ? 'blocked' : 'empty',
  error: message,
  branches: [],
  tree: { width: 1080, height: 560, nodes: [], edges: [] },
  displayMeta: {
    stageLabel: '等待数据',
    stageTitle: workbenchEmptyTitle.value,
    stageSubtitle: workbenchEmptyDescription.value,
    themeName: currentTheme.value?.name || currentThemeId.value,
    generationLabel: '生成世界线',
    generationMode: 'base',
    workspaceHint: '请先补齐 live bridge、知识库数据或静态 adapter。'
  }
})

const tryGenerateLiveWorldline = async () => {
  if (!currentKnowledgeDbId.value) {
    liveStatus.value = { state: 'idle', message: '' }
    return null
  }

  if (!userStore.isAdmin) {
    liveStatus.value = {
      state: 'blocked',
      message: '该主题已配置 live bridge，但后端 Worldline 契约保持 admin-only。请使用管理员账号进入。'
    }
    return null
  }

  try {
    liveStatus.value = { state: 'loading', message: '正在读取后端 Worldline facade。' }
    const result = await worldlineApi.generate({
      dbId: currentKnowledgeDbId.value,
      themeId: currentThemeId.value,
      question: questionDraft.value,
      mode: 'base',
      context: {
        theme: currentThemeId.value,
        module: currentThemeId.value,
        knowledge_db_id: currentKnowledgeDbId.value
      }
    })
    if (hasHydratableBranches(result)) {
      liveStatus.value = { state: 'ready', message: '已使用后端 Worldline facade 生成。' }
      return result
    }
    liveStatus.value = {
      state: 'empty',
      message: '后端 live facade 暂无可用分支。'
    }
    return null
  } catch (error) {
    console.warn('Worldline live generate failed:', error)
    liveStatus.value = {
      state: 'failed',
      message: error?.message || '后端 Worldline facade 调用失败。'
    }
    return null
  }
}

const generateBaseWorldline = async () => {
  if (!isThemeSupported.value) {
    worldlineStore.reset()
    return
  }

  isGenerating.value = true
  worldlineStore.clearHandoff()
  try {
    const liveResult = await tryGenerateLiveWorldline()
    if (liveResult) {
      applyWorldlineResult(liveResult, 'live-generate')
      return
    }

    if (currentThemeAdapter.value) {
      const result = currentThemeAdapter.value.buildWorldline(questionDraft.value, {
        theme: currentThemeId.value,
        module: currentThemeId.value
      })
      applyWorldlineResult(result, 'base-generate')
      return
    }

    applyWorldlineResult(buildEmptyWorldlineResult(liveStatus.value.message), 'empty-live-generate')
  } finally {
    isGenerating.value = false
  }
}

const handleNodeSelection = (nodeId) => {
  worldlineStore.clearHandoff()
  worldlineStore.setSelectedNode(nodeId)
  syncThemeContextFromBranch(worldlineStore.activeBranch)
}

const buildAgentLocation = async (branch) => {
  syncThemeContextFromBranch(branch)
  const query = themeContextStore.toRouteQuery(branch.context)
  const defaultAgentId = await ensureDefaultAgent()
  if (defaultAgentId) {
    return {
      name: 'AgentCompWithId',
      params: { agent_id: defaultAgentId },
      query
    }
  }
  return { name: 'AgentComp', query }
}

const goToThemeChat = async () => {
  const branch = worldlineStore.activeBranch
  if (!branch) return

  worldlineStore.setHandoff({
    target: 'chat',
    label: '带着当前主线进入对话'
  })
  sessionStorage.setItem(WORLDLINE_HANDOFF_KEY, '1')

  if (!userStore.isLoggedIn) {
    syncThemeContextFromBranch(branch)
    const fallbackTarget = {
      name: 'AgentComp',
      query: themeContextStore.toRouteQuery(branch.context)
    }
    sessionStorage.setItem('redirect', router.resolve(fallbackTarget).fullPath)
    await router.push('/login')
    return
  }

  const target = await buildAgentLocation(branch)
  await router.push(target)
}

const switchTheme = async (themeId) => {
  const targetTheme = availableThemes.value.find((theme) => theme.id === themeId)
  if (!targetTheme || !isWorldlineEntry(targetTheme)) return
  await router.push({ path: `/worldline/${themeId}` })
}

const ensureWorkbenchData = async () => {
  await infoStore.loadInfoConfig()

  if (!hasThemeId.value || !isThemeSupported.value) {
    worldlineStore.reset()
    questionDraft.value = getWorldlineDefaultQuestion(currentThemeId.value)
    return
  }

  const canReuseCurrentState =
    worldlineStore.themeId === currentThemeId.value &&
    worldlineStore.hasBranches &&
    (!incomingQuestion.value || incomingQuestion.value === worldlineStore.rootQuestion)

  if (canReuseCurrentState) {
    questionDraft.value = worldlineStore.rootQuestion
    syncThemeContextFromBranch(worldlineStore.activeBranch)
    return
  }

  questionDraft.value =
    incomingQuestion.value || worldlineStore.questionDraft || getWorldlineDefaultQuestion(currentThemeId.value)

  await generateBaseWorldline()
}

watch(
  () => route.fullPath,
  async () => {
    await ensureWorkbenchData()
  }
)

onMounted(async () => {
  await ensureWorkbenchData()
})
</script>

<style scoped lang="less">
.worldline-workbench {
  min-height: 100vh;
  padding: 18px 20px 30px;
  background:
    radial-gradient(circle at top left, color-mix(in srgb, var(--main-100) 26%, transparent), transparent 32%),
    linear-gradient(180deg, var(--main-10), var(--gray-10));
}

.workbench-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18px;
  max-width: 1660px;
  margin: 0 auto 12px;
}

.header-copy h1 {
  margin: 0;
  color: var(--gray-1000);
  font-size: clamp(1.9rem, 3.6vw, 2.8rem);
  letter-spacing: -0.03em;
}

.eyebrow {
  margin: 0 0 7px;
  color: var(--main-600);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.header-link {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--gray-150) 88%, transparent);
  background: color-mix(in srgb, var(--gray-0) 90%, transparent);
  color: var(--gray-700);
  text-decoration: none;
  font-weight: 600;
}

.module-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  max-width: 1660px;
  margin: 0 auto 12px;
}

.module-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 11px;
  border-radius: 14px;
  border: 1px solid color-mix(in srgb, var(--gray-120) 88%, transparent);
  background: color-mix(in srgb, var(--gray-0) 92%, transparent);
  cursor: pointer;
}

.module-pill.active {
  border-color: color-mix(in srgb, var(--main-300) 88%, transparent);
  box-shadow: 0 8px 18px color-mix(in srgb, var(--main-500) 10%, transparent);
}

.module-pill span {
  color: var(--gray-900);
  font-weight: 700;
}

.workbench-shell {
  max-width: 1660px;
  margin: 0 auto;
}

.stage-column {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stage-panel {
  padding: 14px;
  border-radius: 24px;
  border: 1px solid color-mix(in srgb, var(--gray-120) 88%, transparent);
  background:
    radial-gradient(circle at top left, color-mix(in srgb, var(--main-100) 14%, transparent), transparent 36%),
    linear-gradient(180deg, color-mix(in srgb, var(--gray-0) 94%, transparent), var(--main-10));
  box-shadow: 0 18px 38px color-mix(in srgb, var(--gray-1000) 7%, transparent);
}

.live-empty-state {
  min-height: 360px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 28px;
  border-radius: 16px;
  border: 1px dashed color-mix(in srgb, var(--gray-180) 80%, transparent);
  background: color-mix(in srgb, var(--gray-0) 88%, transparent);
}

.live-empty-state h2 {
  margin: 0;
  color: var(--gray-1000);
  font-size: 1.2rem;
}

.live-empty-state p:last-child {
  max-width: 680px;
  margin: 10px 0 0;
  color: var(--gray-600);
  line-height: 1.7;
}

.selection-brief {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid color-mix(in srgb, var(--main-200) 35%, transparent);
  background: color-mix(in srgb, var(--gray-0) 92%, transparent);
}

.brief-tag {
  margin: 0;
  color: var(--main-700);
  font-size: 11px;
  font-weight: 700;
}

.selection-brief p {
  margin: 4px 0 0;
  color: var(--gray-600);
  font-size: 12px;
  line-height: 1.45;
}

.dialogue-panel {
  border-radius: 18px;
  border: 1px solid color-mix(in srgb, var(--main-300) 34%, transparent);
  background:
    radial-gradient(circle at 10% 0, color-mix(in srgb, var(--main-80) 18%, transparent), transparent 45%),
    color-mix(in srgb, var(--gray-0) 95%, transparent);
  padding: 12px;
}

.dialogue-head strong {
  color: var(--gray-900);
  font-size: 13px;
}

.dialogue-hint {
  margin: 6px 0 0;
  color: var(--gray-600);
  font-size: 12px;
  line-height: 1.6;
}

.dialogue-input-wrap {
  margin-top: 10px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
}

.dialogue-input {
  width: 100%;
  border: 1px solid color-mix(in srgb, var(--gray-180) 72%, transparent);
  border-radius: 12px;
  background: color-mix(in srgb, var(--gray-0) 96%, transparent);
  color: var(--gray-900);
  padding: 10px 12px;
  font-size: 14px;
  outline: none;
}

.dialogue-input:focus {
  border-color: color-mix(in srgb, var(--main-400) 80%, transparent);
}

.dialogue-send,
.secondary-btn {
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
}

.dialogue-send {
  border: 1px solid color-mix(in srgb, var(--main-500) 75%, transparent);
  background: color-mix(in srgb, var(--main-40) 78%, var(--gray-0));
  color: var(--main-800);
  min-height: 40px;
  padding: 0 14px;
}

.dialogue-send:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.dialogue-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-start;
}

.secondary-btn {
  border: 1px solid color-mix(in srgb, var(--gray-180) 74%, transparent);
  background: color-mix(in srgb, var(--gray-0) 92%, transparent);
  color: var(--gray-700);
  min-height: 34px;
  padding: 0 12px;
}

.unsupported-shell {
  display: block;
}

.unsupported-card {
  padding: 18px;
  border-radius: 20px;
  border: 1px solid color-mix(in srgb, var(--gray-120) 88%, transparent);
  background: color-mix(in srgb, var(--gray-0) 94%, transparent);
}

.unsupported-card h2 {
  margin: 0;
  color: var(--gray-1000);
  font-size: 1.1rem;
}

.unsupported-description {
  margin: 8px 0 0;
  color: var(--gray-600);
  line-height: 1.55;
}

.unsupported-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 14px;
}

@media (max-width: 920px) {
  .workbench-header {
    flex-direction: column;
  }

  .dialogue-input-wrap {
    grid-template-columns: 1fr;
  }
}
</style>
