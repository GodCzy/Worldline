import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

const emptyTree = () => ({
  width: 1320,
  height: 720,
  nodes: [],
  edges: []
})

const emptyViewState = () => ({
  handoffTarget: '',
  handoffLabel: '',
  lastGeneratedFrom: '',
  lastInteractionAt: '',
  protocolVersion: 'v1.2-alpha'
})

const emptyDisplayMeta = () => ({
  stageLabel: '',
  stageTitle: '',
  stageSubtitle: '',
  branchCount: 0,
  themeName: '',
  generationLabel: '',
  generationMode: 'base',
  workspaceHint: ''
})

const emptyQuality = () => ({
  status: '',
  gateId: '',
  branchCount: 0,
  citationCoverage: 0,
  latestGate: null
})

export const useWorldlineContextStore = defineStore('worldlineContext', () => {
  const themeId = ref('')
  const moduleId = ref('')
  const knowledgeDbId = ref('')
  const knowledgeMode = ref('')
  const layers = ref([])
  const rootQuestion = ref('')
  const questionDraft = ref('')
  const status = ref('idle')
  const error = ref('')
  const generatedAt = ref('')
  const sourceType = ref('')
  const generationMode = ref('base')
  const generationRound = ref(0)
  const branches = ref([])
  const activeBranchId = ref('')
  const selectedNodeId = ref('')
  const tree = ref(emptyTree())
  const snapshots = ref([])
  const activeSnapshotIndex = ref(0)
  const quality = ref(emptyQuality())
  const routeTrace = ref({})
  const overview = ref({})
  const viewState = ref(emptyViewState())
  const displayMeta = ref(emptyDisplayMeta())

  const activeBranch = computed(
    () => branches.value.find((branch) => branch.id === activeBranchId.value) || null
  )
  const activeBranchIndex = computed(
    () => branches.value.findIndex((branch) => branch.id === activeBranchId.value)
  )
  const selectedNode = computed(
    () => (tree.value.nodes || []).find((node) => node.id === selectedNodeId.value) || null
  )
  const branchCount = computed(() => branches.value.length)
  const hasBranches = computed(() => branchCount.value > 0)
  const evidenceRefs = computed(() => activeBranch.value?.evidenceRefs || [])
  const wikiRefs = computed(() => activeBranch.value?.wikiRefs || [])
  const entityRefs = computed(() => activeBranch.value?.entityRefs || [])
  const timelineRefs = computed(() => activeBranch.value?.timelineRefs || [])
  const activeSnapshot = computed(() => snapshots.value[activeSnapshotIndex.value] || snapshots.value[0] || null)
  const nextActions = computed(() => activeBranch.value?.nextActions || [])
  const handoffTarget = computed(() => viewState.value.handoffTarget || '')
  const handoffLabel = computed(() => viewState.value.handoffLabel || '')
  const lastGeneratedFrom = computed(() => viewState.value.lastGeneratedFrom || '')
  const protocolVersion = computed(() => viewState.value.protocolVersion || 'v1.2-alpha')

  const reset = () => {
    themeId.value = ''
    moduleId.value = ''
    knowledgeDbId.value = ''
    knowledgeMode.value = ''
    layers.value = []
    rootQuestion.value = ''
    questionDraft.value = ''
    status.value = 'idle'
    error.value = ''
    generatedAt.value = ''
    sourceType.value = ''
    generationMode.value = 'base'
    generationRound.value = 0
    branches.value = []
    activeBranchId.value = ''
    selectedNodeId.value = ''
    tree.value = emptyTree()
    snapshots.value = []
    activeSnapshotIndex.value = 0
    quality.value = emptyQuality()
    routeTrace.value = {}
    overview.value = {}
    viewState.value = emptyViewState()
    displayMeta.value = emptyDisplayMeta()
  }

  const hydrate = (payload = {}) => {
    themeId.value = payload.themeId || ''
    moduleId.value = payload.moduleId || payload.themeId || ''
    knowledgeDbId.value = payload.knowledgeDbId || payload.knowledge_db_id || ''
    knowledgeMode.value = payload.knowledgeMode || payload.knowledge_mode || ''
    layers.value = Array.isArray(payload.layers) ? payload.layers : []
    rootQuestion.value = payload.rootQuestion || ''
    questionDraft.value = payload.questionDraft || payload.rootQuestion || ''
    status.value = payload.status || 'ready'
    error.value = payload.error || ''
    generatedAt.value = payload.generatedAt || new Date().toISOString()
    sourceType.value = payload.sourceType || ''
    generationMode.value = payload.generationMode || 'base'
    generationRound.value = Number(payload.generationRound || 1)
    branches.value = Array.isArray(payload.branches) ? payload.branches : []
    activeBranchId.value = payload.activeBranchId || branches.value[0]?.id || ''
    selectedNodeId.value = payload.selectedNodeId || activeBranchId.value || ''
    tree.value = payload.tree || emptyTree()
    snapshots.value = Array.isArray(payload.snapshots) ? payload.snapshots : []
    activeSnapshotIndex.value = 0
    quality.value = {
      ...emptyQuality(),
      ...(payload.quality || {})
    }
    routeTrace.value = payload.routeTrace || {}
    overview.value = payload.overview || {}
    viewState.value = {
      ...emptyViewState(),
      ...(payload.viewState || {})
    }
    displayMeta.value = {
      ...emptyDisplayMeta(),
      ...(payload.displayMeta || {}),
      branchCount: branches.value.length,
      generationMode: payload.generationMode || payload.displayMeta?.generationMode || 'base'
    }
  }

  const setRootQuestion = (value = '') => {
    rootQuestion.value = typeof value === 'string' ? value.trim() : ''
    if (!questionDraft.value) {
      questionDraft.value = rootQuestion.value
    }
  }

  const setQuestionDraft = (value = '') => {
    questionDraft.value = typeof value === 'string' ? value.trim() : ''
  }

  const setGenerationMode = (value = 'base') => {
    generationMode.value = value || 'base'
    displayMeta.value = {
      ...displayMeta.value,
      generationMode: generationMode.value
    }
  }

  const setActiveBranch = (branchId = '') => {
    if (!branchId) {
      return
    }

    const target = branches.value.find((branch) => branch.id === branchId)
    if (!target) {
      return
    }

    activeBranchId.value = branchId
    selectedNodeId.value = branchId
  }

  const setSelectedNode = (nodeId = '') => {
    selectedNodeId.value = nodeId

    const branchMatch = branches.value.find((branch) => branch.id === nodeId)
    if (branchMatch) {
      activeBranchId.value = branchMatch.id
      return
    }

    const nodeMatch = (tree.value.nodes || []).find((node) => node.id === nodeId)
    if (nodeMatch?.branchId) {
      activeBranchId.value = nodeMatch.branchId
    }
  }

  const setActiveSnapshot = (index = 0) => {
    const numericIndex = Number(index)
    if (!Number.isFinite(numericIndex) || snapshots.value.length === 0) {
      activeSnapshotIndex.value = 0
      return
    }

    activeSnapshotIndex.value = Math.min(Math.max(0, numericIndex), snapshots.value.length - 1)
  }

  const setHandoff = ({ target = '', label = '' } = {}) => {
    viewState.value = {
      ...viewState.value,
      handoffTarget: target,
      handoffLabel: label,
      lastInteractionAt: new Date().toISOString()
    }
  }

  const clearHandoff = () => {
    viewState.value = {
      ...viewState.value,
      handoffTarget: '',
      handoffLabel: ''
    }
  }

  const rememberGenerationSource = (value = '') => {
    viewState.value = {
      ...viewState.value,
      lastGeneratedFrom: typeof value === 'string' ? value.trim() : ''
    }
  }

  return {
    themeId,
    moduleId,
    knowledgeDbId,
    knowledgeMode,
    layers,
    rootQuestion,
    questionDraft,
    status,
    error,
    generatedAt,
    sourceType,
    generationMode,
    generationRound,
    branches,
    activeBranchId,
    selectedNodeId,
    tree,
    snapshots,
    activeSnapshotIndex,
    activeSnapshot,
    quality,
    routeTrace,
    overview,
    viewState,
    displayMeta,
    activeBranch,
    activeBranchIndex,
    selectedNode,
    branchCount,
    hasBranches,
    evidenceRefs,
    wikiRefs,
    entityRefs,
    timelineRefs,
    nextActions,
    handoffTarget,
    handoffLabel,
    lastGeneratedFrom,
    protocolVersion,
    reset,
    hydrate,
    setRootQuestion,
    setQuestionDraft,
    setGenerationMode,
    setActiveBranch,
    setSelectedNode,
    setActiveSnapshot,
    setHandoff,
    clearHandoff,
    rememberGenerationSource
  }
})
