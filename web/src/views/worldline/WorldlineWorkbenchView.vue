<template>
  <div class="worldline-workbench">
    <header class="workbench-header">
      <div class="header-copy">
        <p class="eyebrow">WORLDLINE WORKBENCH</p>
        <h1>{{ workbenchTitle }}</h1>
        <p>{{ workbenchSubtitle }}</p>
      </div>

      <div class="header-actions">
        <router-link class="header-link" to="/worldline">Hub</router-link>
        <router-link class="header-link" to="/graph">Graph</router-link>
        <router-link class="header-link" to="/themes">Modules</router-link>
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
        <small>{{ moduleTypeLabel(theme) }}</small>
      </button>
    </section>

    <main class="workbench-shell">
      <section v-if="!hasThemeId" class="unsupported-shell">
        <div class="unsupported-card">
          <p class="eyebrow">NO MODULE</p>
          <h2>请先选择一个 Worldline 模块</h2>
          <p>工作台需要真实知识模块和 live bridge 才能生成世界线。</p>
          <router-link class="header-link" to="/worldline">返回 Hub</router-link>
        </div>
      </section>

      <template v-else-if="isThemeSupported">
        <section class="command-bar">
          <div class="question-box">
            <label for="worldline-workbench-question">问题起点</label>
            <input
              id="worldline-workbench-question"
              v-model="questionDraft"
              type="text"
              placeholder="描述目标、约束和证据来源"
              @keydown.enter.prevent="generateBaseWorldline"
            />
          </div>
          <button class="generate-button" type="button" :disabled="isGenerating" @click="generateBaseWorldline">
            {{ isGenerating ? '生成中' : generationLabel }}
          </button>
          <button class="handoff-button" type="button" :disabled="!worldlineStore.activeBranch" @click="goToThemeChat">
            Agent Handoff
          </button>
        </section>

        <section class="status-line" :class="liveStatus.state">
          <span>{{ liveStatusLabel }}</span>
          <strong>{{ worldlineStore.quality.status || worldlineStore.status }}</strong>
          <em>{{ worldlineStore.knowledgeMode || 'llm_wiki_primary_rag_auxiliary' }}</em>
        </section>

        <section class="workbench-grid">
          <div class="stage-column">
            <WorldlineBranchCanvas
              class="canvas-panel"
              :tree="worldlineStore.tree"
              :active-branch-id="worldlineStore.activeBranchId"
              :selected-node-id="worldlineStore.selectedNodeId"
              :branch-count="worldlineStore.branchCount"
              :display-meta="worldlineStore.displayMeta || {}"
              :active-snapshot="worldlineStore.activeSnapshot"
              @select-node="handleNodeSelection"
            />

            <WorldlineTimelineScrubber
              :snapshots="worldlineStore.snapshots"
              :active-index="worldlineStore.activeSnapshotIndex"
              :timeline-refs="worldlineStore.timelineRefs"
              @update:active-index="worldlineStore.setActiveSnapshot"
            />
          </div>

          <aside class="inspect-column">
            <WorldlineBranchDetailPanel
              :branch="worldlineStore.activeBranch"
              @handoff="goToThemeChat"
              @open-graph="openGraphFocus"
            />
            <WorldlineEvidenceRail
              :evidence-refs="worldlineStore.evidenceRefs"
              :wiki-refs="worldlineStore.wikiRefs"
              :entity-refs="worldlineStore.entityRefs"
              :timeline-refs="worldlineStore.timelineRefs"
            />
            <WorldlineGraphFocusPanel
              :entity-refs="worldlineStore.entityRefs"
              :timeline-refs="worldlineStore.timelineRefs"
              :quality="worldlineStore.quality"
              :route-trace="worldlineStore.routeTrace"
              @open-graph="openGraphFocus"
            />
            <WorldlineLiveOpsPanel
              :overview="liveOverviewForPanel"
              :loading-key="liveActionKey"
              :disabled="!canUseLiveOps"
              :status-message="liveOpsMessage"
              @action="handleLiveOpsAction"
            />
          </aside>
        </section>
      </template>

      <section v-else class="unsupported-shell">
        <div class="unsupported-card">
          <p class="eyebrow">UNSUPPORTED MODULE</p>
          <h2>{{ unsupportedTitle }}</h2>
          <p>{{ unsupportedDescription }}</p>
          <router-link class="header-link" to="/worldline">返回 Hub</router-link>
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
import { setStoredRedirect } from '@/router'
import { getWorldlineDefaultQuestion, hasWorldlineAdapter, resolveWorldlineAdapter } from '@/data/worldline'
import { hasWorldlineLiveBridge, resolveThemeKnowledgeDbId, worldlineApi } from '@/apis/worldline_api'
import WorldlineBranchCanvas from '@/components/worldline/WorldlineBranchCanvas.vue'
import WorldlineEvidenceRail from '@/components/worldline/WorldlineEvidenceRail.vue'
import WorldlineBranchDetailPanel from '@/components/worldline/WorldlineBranchDetailPanel.vue'
import WorldlineTimelineScrubber from '@/components/worldline/WorldlineTimelineScrubber.vue'
import WorldlineGraphFocusPanel from '@/components/worldline/WorldlineGraphFocusPanel.vue'
import WorldlineLiveOpsPanel from '@/components/worldline/WorldlineLiveOpsPanel.vue'

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
const liveOverview = ref(null)
const liveActionKey = ref('')
const liveOpsMessage = ref('')

const currentThemeId = computed(() => String(route.params.themeId || '').trim().toLowerCase())
const hasThemeId = computed(() => Boolean(currentThemeId.value))
const currentThemeAdapter = computed(() => resolveWorldlineAdapter(currentThemeId.value))
const isWorldlineEntry = (theme = {}) => hasWorldlineLiveBridge(theme) || hasWorldlineAdapter(theme.id)
const availableThemes = computed(() => (infoStore.themes || []).filter((theme) => isWorldlineEntry(theme)))
const currentTheme = computed(() => availableThemes.value.find((theme) => theme.id === currentThemeId.value) || null)
const routeKnowledgeDbId = computed(() => {
  const fromQuery = route.query.knowledge_db_id || route.query.db_id
  return typeof fromQuery === 'string' ? fromQuery.trim() : ''
})
const currentKnowledgeDbId = computed(() => routeKnowledgeDbId.value || resolveThemeKnowledgeDbId(currentTheme.value))
const currentGenerationConfig = computed(
  () => currentTheme.value?.worldline?.generation || currentTheme.value?.context?.generation || {}
)
const currentEvidenceSources = computed(() => {
  const value = currentTheme.value?.worldline?.evidence_sources || currentTheme.value?.context?.evidence_sources || []
  if (Array.isArray(value)) return value
  return String(value || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
})
const isLiveSupported = computed(() => Boolean(currentKnowledgeDbId.value))
const isThemeSupported = computed(() => Boolean(currentThemeAdapter.value || isLiveSupported.value))
const canUseLiveOps = computed(() => Boolean(isLiveSupported.value && userStore.isAdmin))
const liveOverviewForPanel = computed(() => {
  if (liveOverview.value) return liveOverview.value
  const overview = worldlineStore.overview || {}
  const counts = overview.counts || worldlineStore.routeTrace?.counts || {}
  return {
    ...overview,
    counts,
    quality_gate: overview.quality_gate || { latest: worldlineStore.quality?.latestGate || null },
    quality: worldlineStore.quality,
    status: overview.status || worldlineStore.status
  }
})
const incomingQuestion = computed(() => (typeof route.query.question === 'string' ? route.query.question.trim() : ''))
const generationLabel = computed(() => worldlineStore.displayMeta.generationLabel || '生成世界线')
const workbenchTitle = computed(() => currentTheme.value?.name || worldlineStore.displayMeta.themeName || 'Worldline')
const workbenchSubtitle = computed(
  () =>
    worldlineStore.displayMeta.workspaceHint ||
    '检查分支证据、Wiki 引用、图谱实体、时间事实和 Agent handoff。'
)
const unsupportedTitle = computed(() =>
  hasThemeId.value ? `模块 ${currentThemeId.value} 尚未接入 Worldline` : '当前没有指定模块'
)
const unsupportedDescription = computed(
  () => '请返回 Hub 选择已配置 live bridge 的真实知识模块，或先在主题分区添加自定义模块。'
)
const liveStatusLabel = computed(() => {
  if (liveStatus.value.message) return liveStatus.value.message
  if (worldlineStore.lastGeneratedFrom === 'live-generate') return '已使用真实 Worldline facade'
  if (worldlineStore.lastGeneratedFrom === 'local-adapter') return '已使用本地模块 adapter'
  return '等待生成'
})
const defaultQuestionForTheme = () =>
  currentTheme.value?.worldline?.default_question ||
  currentTheme.value?.context?.default_question ||
  getWorldlineDefaultQuestion(currentThemeId.value)

const moduleTypeLabel = (theme = {}) => {
  if (hasWorldlineLiveBridge(theme)) return 'Live Bridge'
  if (hasWorldlineAdapter(theme.id)) return 'Local Adapter'
  return 'Worldline'
}

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

const refreshLiveOverview = async ({ silent = false } = {}) => {
  if (!canUseLiveOps.value) {
    liveOverview.value = null
    return null
  }

  if (!silent) {
    liveActionKey.value = 'refresh'
  }

  try {
    const result = await worldlineApi.overview(currentKnowledgeDbId.value)
    liveOverview.value = result
    if (!silent) {
      liveOpsMessage.value = '后端概览已刷新。'
    }
    return result
  } catch (error) {
    liveOpsMessage.value = error?.message || '后端概览读取失败。'
    if (!silent) {
      liveStatus.value = { state: 'failed', message: liveOpsMessage.value }
    }
    return null
  } finally {
    if (!silent && liveActionKey.value === 'refresh') {
      liveActionKey.value = ''
    }
  }
}

const buildEmptyWorldlineResult = (message = '') => ({
  themeId: currentThemeId.value,
  moduleId: currentThemeId.value,
  knowledgeDbId: currentKnowledgeDbId.value,
  knowledgeMode: 'llm_wiki_primary_rag_auxiliary',
  layers: ['evidence_ledger', 'llm_wiki', 'temporal_evidence_graph', 'quality_gate'],
  rootQuestion: questionDraft.value,
  questionDraft: questionDraft.value,
  status: message ? 'blocked' : 'empty',
  error: message,
  branches: [],
  tree: { width: 1160, height: 560, nodes: [], edges: [] },
  snapshots: [],
  quality: { status: message ? 'blocked' : 'empty' },
  displayMeta: {
    stageLabel: '等待数据',
    stageTitle: '当前知识库还没有可生成的世界线',
    stageSubtitle: message || '请导入文档、重建 Wiki/Graph，或检查知识库映射。',
    themeName: currentTheme.value?.name || currentThemeId.value,
    generationLabel: '生成世界线',
    generationMode: 'base',
    workspaceHint: '先补齐 live bridge 或知识库数据。'
  }
})

const tryGenerateLiveWorldline = async () => {
  if (!currentKnowledgeDbId.value) {
    liveStatus.value = { state: 'idle', message: '' }
    return null
  }

  if (!userStore.isAdmin) {
    liveStatus.value = currentThemeAdapter.value
      ? { state: 'preview', message: '未登录管理员，已回退到本地 adapter。' }
      : { state: 'blocked', message: '该模块需要管理员权限读取真实 Worldline facade。' }
    return null
  }

  try {
    liveStatus.value = { state: 'loading', message: '正在读取后端 Worldline facade。' }
    const result = await worldlineApi.generate({
      dbId: currentKnowledgeDbId.value,
      themeId: currentThemeId.value,
      question: questionDraft.value,
      mode: currentGenerationConfig.value.mode || 'base',
      context: {
        ...(currentTheme.value?.context || {}),
        theme: currentThemeId.value,
        module: currentThemeId.value,
        db_id: currentKnowledgeDbId.value,
        knowledge_db_id: currentKnowledgeDbId.value,
        knowledge_name: currentTheme.value?.knowledge?.name || currentTheme.value?.metadata?.knowledge_name || '',
        knowledge_type: currentTheme.value?.knowledge?.kb_type || currentTheme.value?.metadata?.knowledge_type || '',
        objective: currentTheme.value?.worldline?.objective || currentTheme.value?.context?.objective || '',
        evidence_sources: currentEvidenceSources.value,
        generation: currentGenerationConfig.value
      }
    })
    if (hasHydratableBranches(result)) {
      liveStatus.value = { state: 'ready', message: '已使用真实 Worldline facade 生成。' }
      return result
    }
    liveStatus.value = { state: 'empty', message: '后端 facade 暂无可用分支。' }
    return null
  } catch (error) {
    console.warn('Worldline live generate failed:', error)
    liveStatus.value = {
      state: currentThemeAdapter.value ? 'preview' : 'failed',
      message: currentThemeAdapter.value
        ? '后端调用失败，已回退到本地 adapter。'
        : error?.message || '后端 Worldline facade 调用失败。'
    }
    return null
  }
}

const handleLiveOpsAction = async (actionKey) => {
  if (!canUseLiveOps.value || liveActionKey.value) {
    return
  }

  liveActionKey.value = actionKey
  liveOpsMessage.value = ''

  try {
    if (actionKey === 'refresh') {
      await refreshLiveOverview({ silent: true })
      liveOpsMessage.value = '后端概览已刷新。'
      return
    }

    if (actionKey === 'refreshManifest') {
      const [manifest, auditLogs] = await Promise.all([
        worldlineApi.getMcpManifest(currentKnowledgeDbId.value),
        worldlineApi.listMcpAuditLogs(currentKnowledgeDbId.value, { limit: 8 })
      ])
      liveOverview.value = {
        ...(liveOverview.value || {}),
        mcp: {
          ...(liveOverview.value?.mcp || {}),
          manifest,
          audit_logs: auditLogs
        }
      }
      liveOpsMessage.value = 'MCP manifest 与审计摘要已刷新。'
      return
    }

    if (actionKey === 'planWorkflow') {
      const plan = await worldlineApi.planWorkflow(currentKnowledgeDbId.value, {
        workflow_type: 'knowledge_refresh'
      })
      await refreshLiveOverview({ silent: true })
      liveOpsMessage.value = `Workflow 已规划：${plan.workflow_id || plan.status || 'planned'}。`
      return
    }

    if (actionKey === 'rebuildWiki') {
      const result = await worldlineApi.rebuildWiki(currentKnowledgeDbId.value, { max_topics: 8 })
      await refreshLiveOverview({ silent: true })
      liveOpsMessage.value = `Wiki 已重建：${result.status || 'success'}。`
      await generateBaseWorldline()
      return
    }

    if (actionKey === 'rebuildGraph') {
      const result = await worldlineApi.rebuildGraph(currentKnowledgeDbId.value, { max_entities: 40 })
      await refreshLiveOverview({ silent: true })
      liveOpsMessage.value = `图谱已重建：${result.status || 'success'}。`
      await generateBaseWorldline()
      return
    }

    if (actionKey === 'buildGoldenSet') {
      const result = await worldlineApi.buildGoldenSet(currentKnowledgeDbId.value, { limit: 20 })
      await refreshLiveOverview({ silent: true })
      liveOpsMessage.value = `Golden Set：${result.item_count ?? 0} 项。`
      return
    }

    if (actionKey === 'runQualityGate') {
      const result = await worldlineApi.runQualityGate(currentKnowledgeDbId.value, { thresholds: {} })
      await refreshLiveOverview({ silent: true })
      liveOpsMessage.value = `Quality Gate：${result.status || 'finished'}。`
      await generateBaseWorldline()
    }
  } catch (error) {
    liveOpsMessage.value = error?.message || 'Live Ops 执行失败。'
    liveStatus.value = { state: 'failed', message: liveOpsMessage.value }
  } finally {
    liveActionKey.value = ''
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
      applyWorldlineResult(result, 'local-adapter')
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
    label: '带着当前世界线分支进入 Agent'
  })
  sessionStorage.setItem(WORLDLINE_HANDOFF_KEY, '1')

  if (!userStore.isLoggedIn) {
    syncThemeContextFromBranch(branch)
    const fallbackTarget = {
      name: 'AgentComp',
      query: themeContextStore.toRouteQuery(branch.context)
    }
    const redirectPath = router.resolve(fallbackTarget).fullPath
    setStoredRedirect(redirectPath)
    await router.push({ name: 'Home', query: { login: '1', redirect: redirectPath } })
    return
  }

  const target = await buildAgentLocation(branch)
  await router.push(target)
}

const openGraphFocus = async () => {
  const branch = worldlineStore.activeBranch
  if (branch?.context) {
    syncThemeContextFromBranch(branch)
  }
  await router.push({
    path: '/graph',
    query: themeContextStore.toRouteQuery(branch?.context || themeContextStore.activeContext || {})
  })
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
    liveOverview.value = null
    liveOpsMessage.value = ''
    questionDraft.value = defaultQuestionForTheme()
    return
  }

  await refreshLiveOverview({ silent: true })

  const canReuseCurrentState =
    worldlineStore.themeId === currentThemeId.value &&
    (!currentKnowledgeDbId.value || worldlineStore.knowledgeDbId === currentKnowledgeDbId.value) &&
    worldlineStore.hasBranches &&
    (!incomingQuestion.value || incomingQuestion.value === worldlineStore.rootQuestion)

  if (canReuseCurrentState) {
    questionDraft.value = worldlineStore.rootQuestion
    syncThemeContextFromBranch(worldlineStore.activeBranch)
    return
  }

  questionDraft.value =
    incomingQuestion.value || worldlineStore.questionDraft || defaultQuestionForTheme()

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
  color: var(--wl-text);
  background:
    radial-gradient(circle at 4% 48%, rgba(var(--wl-gold-rgb), 0.14), transparent 25%),
    radial-gradient(circle at 94% 50%, rgba(var(--wl-cyan-rgb), 0.14), transparent 27%),
    linear-gradient(180deg, var(--wl-bg-1), var(--wl-bg-0) 72%, #060a10);
}

.workbench-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18px;
  max-width: 1700px;
  margin: 0 auto 12px;
}

.header-copy h1 {
  margin: 0;
  color: var(--wl-text);
  font-size: clamp(1.8rem, 3vw, 2.7rem);
  font-weight: 900;
  line-height: 1.12;
}

.header-copy p:last-child {
  max-width: 860px;
  margin: 8px 0 0;
  color: var(--wl-muted);
  line-height: 1.6;
}

.eyebrow {
  margin: 0 0 6px;
  color: var(--wl-gold);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.header-actions,
.module-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.header-link,
.module-pill,
.generate-button,
.handoff-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 36px;
  padding: 0 12px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.06);
  color: var(--wl-text-soft);
  cursor: pointer;
  text-decoration: none;
  font-weight: 800;
}

.module-strip {
  max-width: 1700px;
  margin: 0 auto 12px;
}

.module-pill {
  gap: 8px;
}

.module-pill small {
  color: var(--wl-muted-soft);
  font-weight: 800;
}

.module-pill.active {
  border-color: var(--wl-border-gold);
  background: rgba(var(--wl-gold-rgb), 0.12);
  color: #fff7de;
}

.workbench-shell {
  max-width: 1700px;
  margin: 0 auto;
}

.command-bar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 10px;
  align-items: end;
  margin-bottom: 10px;
  padding: 12px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background: var(--wl-panel);
}

.question-box label {
  display: block;
  margin-bottom: 6px;
  color: var(--wl-gold);
  font-size: 12px;
  font-weight: 900;
}

.question-box input {
  width: 100%;
  min-height: 38px;
  padding: 0 12px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(2, 5, 10, 0.72);
  color: var(--wl-text);
}

.question-box input:focus {
  outline: none;
  border-color: var(--wl-border-gold);
  box-shadow: var(--wl-focus-ring);
}

.generate-button {
  border-color: var(--wl-border-gold);
  background: linear-gradient(135deg, rgba(var(--wl-gold-rgb), 0.92), rgba(var(--wl-cyan-rgb), 0.7));
  color: var(--wl-ink);
}

.generate-button:disabled,
.handoff-button:disabled {
  opacity: 0.52;
  cursor: not-allowed;
}

.status-line {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
  padding: 10px 12px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius);
  background: rgba(var(--wl-cyan-rgb), 0.05);
  color: var(--wl-muted);
  font-size: 12px;
}

.status-line strong,
.status-line em {
  color: #fff7de;
  font-style: normal;
  font-weight: 900;
}

.workbench-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(330px, 0.55fr);
  gap: 12px;
}

.stage-column,
.inspect-column {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 12px;
}

.unsupported-shell {
  display: grid;
  min-height: 460px;
  place-items: center;
}

.unsupported-card {
  width: min(620px, 100%);
  padding: 20px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background: var(--wl-panel);
}

.unsupported-card h2 {
  margin: 0;
  color: var(--wl-text);
  font-weight: 900;
}

.unsupported-card p {
  color: var(--wl-muted);
  line-height: 1.7;
}

@media (max-width: 1180px) {
  .workbench-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .worldline-workbench {
    padding: 14px 12px 24px;
  }

  .workbench-header {
    flex-direction: column;
  }

  .header-actions,
  .module-strip {
    width: 100%;
  }

  .header-link,
  .module-pill {
    flex: 1;
  }

  .command-bar {
    grid-template-columns: 1fr;
  }
}
</style>
