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

export const useWorldlineContextStore = defineStore('worldlineContext', () => {
  const themeId = ref('')
  const moduleId = ref('')
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
  const nextActions = computed(() => activeBranch.value?.nextActions || [])
  const handoffTarget = computed(() => viewState.value.handoffTarget || '')
  const handoffLabel = computed(() => viewState.value.handoffLabel || '')
  const lastGeneratedFrom = computed(() => viewState.value.lastGeneratedFrom || '')
  const protocolVersion = computed(() => viewState.value.protocolVersion || 'v1.2-alpha')

  const reset = () => {
    themeId.value = ''
    moduleId.value = ''
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
    viewState.value = emptyViewState()
    displayMeta.value = emptyDisplayMeta()
  }

  const hydrate = (payload = {}) => {
    themeId.value = payload.themeId || ''
    moduleId.value = payload.moduleId || payload.themeId || ''
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
    viewState,
    displayMeta,
    activeBranch,
    activeBranchIndex,
    selectedNode,
    branchCount,
    hasBranches,
    evidenceRefs,
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
    setHandoff,
    clearHandoff,
    rememberGenerationSource
  }
})
