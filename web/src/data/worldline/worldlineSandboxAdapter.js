const defaultQuestion =
  'If I need a lightweight module to validate facade-only integration, which sandbox path should I start with?'

const manifestSummary = {
  card_count: 5
}

const cardTitleMap = {
  'sandbox-contract-card': 'Contract check',
  'sandbox-demo-card': 'Demo route',
  'sandbox-handoff-card': 'Handoff pack',
  'sandbox-graph-card': 'Graph probe',
  'sandbox-entry-card': 'Entry checklist'
}

const labelMap = {
  sandbox_contract: 'Contract check',
  sandbox_demo: 'Demo route',
  sandbox_handoff: 'Handoff pack',
  low_change: 'Low change',
  facade_only: 'Facade only',
  module_contract: 'Module contract',
  graph_probe: 'Graph probe',
  handoff_ready: 'Handoff ready',
  demo: 'Demo',
  validation: 'Validation',
  release: 'Release'
}

const recommendationCandidates = [
  {
    candidate_id: 'sandbox-contract-check',
    title: 'Verify adapter contract',
    build_title: 'Contract-first sandbox route',
    next_scene: 'sandbox_contract',
    graph_loop_id: 'sandbox-contract-loop',
    build_card_id: 'sandbox-contract-card',
    why_selected: [
      'Start from the thinnest path that proves the third module can be discovered and consumed through the facade.',
      'Useful when the goal is to validate structure before expanding any module semantics.'
    ],
    next_card_items: [
      { id: 'sandbox-entry-card', title: 'Entry checklist' },
      { id: 'sandbox-graph-card', title: 'Graph probe' }
    ],
    filters: {
      experience_level: 'module_contract',
      budget_level: 'low_change',
      playstyle: ['facade_only', 'validation'],
      content_goals: ['release']
    }
  },
  {
    candidate_id: 'sandbox-demo-loop',
    title: 'Run a demo-ready branch',
    build_title: 'Demo-focused sandbox route',
    next_scene: 'sandbox_demo',
    graph_loop_id: 'sandbox-demo-loop',
    build_card_id: 'sandbox-demo-card',
    why_selected: [
      'Keep the module readable in ThemeDetail and Workbench with a small but distinct showcase surface.',
      'Useful when a new module must be explainable without touching shared pages.'
    ],
    next_card_items: [
      { id: 'sandbox-demo-card', title: 'Demo route' },
      { id: 'sandbox-entry-card', title: 'Entry checklist' }
    ],
    filters: {
      experience_level: 'module_contract',
      budget_level: 'low_change',
      playstyle: ['demo', 'facade_only'],
      content_goals: ['validation']
    }
  },
  {
    candidate_id: 'sandbox-handoff-pack',
    title: 'Prepare a handoff context',
    build_title: 'Agent-ready sandbox route',
    next_scene: 'sandbox_handoff',
    graph_loop_id: 'sandbox-handoff-loop',
    build_card_id: 'sandbox-handoff-card',
    why_selected: [
      'Focus on the smallest context package that can be handed to Agent or Graph without backend support.',
      'Useful when the module must prove that context, graph and evidence hints stay coherent.'
    ],
    next_card_items: [
      { id: 'sandbox-handoff-card', title: 'Handoff pack' },
      { id: 'sandbox-graph-card', title: 'Graph probe' }
    ],
    filters: {
      experience_level: 'handoff_ready',
      budget_level: 'low_change',
      playstyle: ['graph_probe', 'facade_only'],
      content_goals: ['release']
    }
  }
]

const graphLoops = [
  {
    graph_id: 'sandbox-contract-loop',
    label: 'Contract loop',
    focus: 'sandbox_contract',
    node_count: 4,
    edge_count: 3,
    entry_card_id: 'sandbox-contract-card',
    build_card_id: 'sandbox-contract-card',
    related_cards: [
      { id: 'sandbox-contract-card', title: 'Contract check' },
      { id: 'sandbox-entry-card', title: 'Entry checklist' }
    ],
    nodes: [
      { type: 'theme', label: 'Theme metadata' },
      { type: 'facade', label: 'Adapter registration' },
      { type: 'view', label: 'Shared consumption' }
    ]
  },
  {
    graph_id: 'sandbox-demo-loop',
    label: 'Demo loop',
    focus: 'sandbox_demo',
    node_count: 4,
    edge_count: 3,
    entry_card_id: 'sandbox-demo-card',
    build_card_id: 'sandbox-demo-card',
    related_cards: [
      { id: 'sandbox-demo-card', title: 'Demo route' },
      { id: 'sandbox-entry-card', title: 'Entry checklist' }
    ],
    nodes: [
      { type: 'detail', label: 'Theme detail' },
      { type: 'workbench', label: 'Workbench branch' },
      { type: 'showcase', label: 'Showcase summary' }
    ]
  },
  {
    graph_id: 'sandbox-handoff-loop',
    label: 'Handoff loop',
    focus: 'sandbox_handoff',
    node_count: 4,
    edge_count: 3,
    entry_card_id: 'sandbox-handoff-card',
    build_card_id: 'sandbox-handoff-card',
    related_cards: [
      { id: 'sandbox-handoff-card', title: 'Handoff pack' },
      { id: 'sandbox-graph-card', title: 'Graph probe' }
    ],
    nodes: [
      { type: 'context', label: 'Agent context' },
      { type: 'graph', label: 'Graph keyword' },
      { type: 'handoff', label: 'Next prompt' }
    ]
  }
]

const summarizeQuestion = (question = '') => {
  const normalized = typeof question === 'string' ? question.trim() : ''
  if (!normalized) {
    return defaultQuestion
  }
  return normalized.length > 72 ? `${normalized.slice(0, 71)}...` : normalized
}

const cloneItems = (items = []) => items.map((item) => ({ ...item }))

const getDisplayLabel = (value = '') => labelMap[value] || value || ''

const getCardTitleById = (cardId = '') => cardTitleMap[cardId] || cardId || ''

const getManifestSummary = () => ({ ...manifestSummary })

const getRecommendationCandidates = () =>
  recommendationCandidates.map((item) => ({
    ...item,
    why_selected: [...(item.why_selected || [])],
    next_card_items: cloneItems(item.next_card_items)
  }))

const getRecommendationCandidateById = (candidateId = '') =>
  recommendationCandidates.find((item) => item.candidate_id === candidateId) || null

const getGraphLoops = () =>
  graphLoops.map((item) => ({
    ...item,
    related_cards: cloneItems(item.related_cards),
    nodes: cloneItems(item.nodes)
  }))

const getGraphLoopById = (graphId = '') =>
  graphLoops.find((item) => item.graph_id === graphId) || null

const getGraphDefaultKeyword = (graphLoopOrGraphId = '') => {
  if (graphLoopOrGraphId && typeof graphLoopOrGraphId === 'object') {
    return getDisplayLabel(graphLoopOrGraphId.focus || '')
  }

  const graphLoop = getGraphLoopById(graphLoopOrGraphId)
  return getDisplayLabel(graphLoop?.focus || '')
}

const getCandidateDisplayLabels = (candidate) => {
  const filters = candidate?.filters || {}
  return [
    filters.experience_level,
    filters.budget_level,
    ...(filters.playstyle || []).slice(0, 2),
    ...(filters.content_goals || []).slice(0, 1)
  ]
    .filter(Boolean)
    .map((item) => getDisplayLabel(item))
}

const createRecommendationContext = (candidate) => ({
  theme: 'worldline-sandbox',
  module: 'worldline-sandbox',
  scene: candidate?.next_scene || 'sandbox_contract',
  version: 'phase8-minimal',
  focus: candidate?.candidate_id || '',
  candidate: candidate?.candidate_id || '',
  graph: candidate?.graph_loop_id || '',
  build: candidate?.build_card_id || '',
  entry: 'recommendation'
})

const createGraphContext = (graphLoop) => ({
  theme: 'worldline-sandbox',
  module: 'worldline-sandbox',
  scene: 'graph_loop',
  version: 'phase8-minimal',
  focus: graphLoop?.focus || graphLoop?.graph_id || '',
  graph: graphLoop?.graph_id || '',
  build: graphLoop?.build_card_id || '',
  entry: 'graph'
})

const getThemeShowcaseMeta = () => ({
  eyebrow: 'Third module validation',
  title: 'Sandbox facade probe',
  description:
    'A lightweight module that only proves the shared discovery, workbench, agent and graph chains stay facade-only.',
  stats: {
    cards: 'Sandbox cards',
    recommendations: 'Sandbox routes',
    graphs: 'Probe loops'
  },
  recommendationTitle: 'Validation routes',
  recommendationDescription:
    'Each route is intentionally small and exists only to prove the contract can be reused.',
  graphTitle: 'Graph probes',
  graphDescription: 'Each probe shows the smallest graph summary needed by shared views.',
  recommendationActionLabel: 'Write route context',
  recommendationChatLabel: 'Send route to agent',
  graphActionLabel: 'Write graph context',
  graphAdminLabel: 'Open graph page',
  graphUserLabel: 'Ask with graph context'
})

const getThemeShowcaseCandidates = () =>
  recommendationCandidates.map((candidate) => ({
    id: candidate.candidate_id,
    title: candidate.title,
    subtitle: candidate.build_title,
    badge: getDisplayLabel(candidate.next_scene) || 'Sandbox route',
    labels: getCandidateDisplayLabels(candidate),
    reasons: [...(candidate.why_selected || [])],
    relatedItems: cloneItems(candidate.next_card_items),
    context: createRecommendationContext(candidate)
  }))

const getThemeShowcaseGraphs = () =>
  graphLoops.map((graphLoop) => ({
    id: graphLoop.graph_id,
    title: graphLoop.label,
    subtitle: getCardTitleById(graphLoop.entry_card_id),
    badge: `${graphLoop.node_count} nodes / ${graphLoop.edge_count} edges`,
    focusLabel: getDisplayLabel(graphLoop.focus),
    nodePreview: (graphLoop.nodes || []).slice(0, 4).map((node) => `${node.type}: ${node.label}`),
    relatedItems: cloneItems(graphLoop.related_cards),
    context: createGraphContext(graphLoop)
  }))

const getAgentContextView = (activeContext = {}) => {
  const candidate = getRecommendationCandidateById(activeContext?.candidate || '')
  const graphLoop = getGraphLoopById(activeContext?.graph || '')

  const candidateSummary = candidate
    ? {
        key: `candidate:${candidate.candidate_id}`,
        label: 'Current route',
        title: candidate.title,
        description: `The sandbox is currently focused on ${candidate.build_title}.`
      }
    : null

  const graphSummary = graphLoop
    ? {
        key: `graph:${graphLoop.graph_id}`,
        label: 'Current graph',
        title: graphLoop.label,
        description: `Current probe focuses on ${getDisplayLabel(graphLoop.focus)}.`
      }
    : null

  const prompts = candidate
    ? [
        `Why is ${candidate.title} the best minimal sandbox route right now?`,
        `What should I verify next after ${candidate.build_title}?`,
        'Which shared page is the most likely to break this sandbox route first?'
      ]
    : [
        'Which sandbox route should I start with?',
        'How does this sandbox stay facade-only?',
        'What is the smallest useful next validation step?'
      ]

  return {
    candidateSummary,
    graphSummary,
    welcomePanel: {
      title: candidate ? `Continue with ${candidate.title}` : 'Start the sandbox handoff',
      description:
        'This module only carries the minimum context needed for shared pages, agent prompts and graph probes.',
      prompts
    }
  }
}

const createEvidenceRefs = (candidate, graphLoop) => {
  const evidence = []

  if (candidate?.build_card_id) {
    evidence.push({
      id: candidate.build_card_id,
      title: getCardTitleById(candidate.build_card_id),
      type: 'sandbox_card',
      typeLabel: 'Sandbox card',
      summary: 'The primary card that explains the route this branch is following.'
    })
  }

  for (const item of candidate?.next_card_items || []) {
    evidence.push({
      id: item.id,
      title: item.title,
      type: 'next_card',
      typeLabel: 'Next support',
      summary: 'A support item to keep the route readable in ThemeDetail and Workbench.'
    })
  }

  for (const item of graphLoop?.related_cards || []) {
    evidence.push({
      id: item.id,
      title: item.title,
      type: 'graph_support',
      typeLabel: 'Graph support',
      summary: 'A related graph card that keeps the graph probe and branch context aligned.'
    })
  }

  return evidence.slice(0, 6)
}

const createNextActions = (candidate, graphLoop) => [
  {
    id: `${candidate.candidate_id}-continue`,
    label: 'Continue this sandbox route',
    description: 'Keep the current route active and generate the next branch from the same sandbox path.',
    targetType: 'continue',
    emphasis: 'primary'
  },
  {
    id: `${candidate.candidate_id}-chat`,
    label: 'Send this route to agent',
    description: 'Carry the current route and probe into Agent without changing backend behavior.',
    targetType: 'chat',
    emphasis: 'secondary'
  },
  {
    id: `${candidate.candidate_id}-graph`,
    label: 'Open matching graph probe',
    description: graphLoop
      ? `Open ${graphLoop.label} and inspect the matching probe context.`
      : 'Open the graph page and inspect the matching probe context.',
    targetType: 'graph',
    emphasis: 'ghost'
  }
]

const createTreeData = (branches = [], rootQuestion = '') => {
  const rootNode = {
    id: 'root-question',
    type: 'root',
    title: 'Start question',
    subtitle: summarizeQuestion(rootQuestion),
    meta: 'Sandbox input',
    x: 120,
    y: 280,
    radius: 10,
    branchId: ''
  }

  const nodes = [rootNode]
  const edges = []

  branches.forEach((branch, index) => {
    const branchY = 140 + index * 160
    const branchNode = {
      id: branch.id,
      type: 'branch',
      title: branch.title,
      subtitle: branch.subtitle,
      meta: `${branch.branchTone} / ${branch.riskLabel}`,
      x: 420,
      y: branchY,
      radius: 9,
      branchId: branch.id,
      tone: branch.tone
    }

    const nextNode = {
      id: `${branch.id}-next`,
      type: 'next-step',
      title: 'Next validation',
      subtitle: branch.nextStepSubtitle,
      meta: branch.confidenceLabel,
      x: 760,
      y: branchY,
      radius: 8,
      branchId: branch.id,
      tone: branch.tone
    }

    nodes.push(branchNode, nextNode)
    edges.push(
      {
        id: `edge-root-${branch.id}`,
        source: rootNode.id,
        target: branch.id,
        branchId: branch.id,
        kind: index === 0 ? 'primary' : 'secondary',
        label: branch.choiceLabel,
        isHighlighted: index === 0
      },
      {
        id: `edge-next-${branch.id}`,
        source: branch.id,
        target: nextNode.id,
        branchId: branch.id,
        kind: index === 0 ? 'primary' : 'guide',
        label: 'continue',
        isHighlighted: index === 0
      }
    )
  })

  return {
    width: 1080,
    height: Math.max(560, 220 + branches.length * 160),
    nodes,
    edges
  }
}

const buildBaseContext = (candidate, themeContext = {}) => ({
  ...themeContext,
  theme: 'worldline-sandbox',
  module: 'worldline-sandbox',
  scene: candidate.next_scene,
  version: 'phase8-minimal',
  focus: candidate.candidate_id,
  candidate: candidate.candidate_id,
  graph: candidate.graph_loop_id,
  build: candidate.build_card_id,
  entry: 'worldline-base'
})

const buildBranches = (question = '', themeContext = {}) =>
  recommendationCandidates.map((candidate, index) => {
    const graphLoop = getGraphLoopById(candidate.graph_loop_id)
    const tone = index === 0 ? 'calm' : index === 1 ? 'focus' : 'peak'
    const branchTone =
      index === 0 ? 'Contract path' : index === 1 ? 'Demo path' : 'Handoff path'
    const riskLabel = index === 2 ? 'Medium risk' : 'Low risk'
    const costLabel = 'Low cost'
    const confidenceLabel =
      index === 0
        ? 'Best for first verification'
        : index === 1
          ? 'Best for visible demo'
          : 'Best for agent handoff'

    return {
      id: candidate.candidate_id,
      title: candidate.title,
      subtitle: candidate.build_title,
      summary:
        (candidate.why_selected || []).join(' ') ||
        `The sandbox expands ${summarizeQuestion(question)} into a minimal module route.`,
      branchTone,
      riskLabel,
      costLabel,
      confidenceLabel,
      routeTone: 'Keep the route static, readable and fully inside the adapter contract.',
      tone,
      choiceLabel: getDisplayLabel(candidate.next_scene),
      suitability: getCandidateDisplayLabels(candidate),
      focus: candidate.next_scene,
      focusKey: candidate.candidate_id,
      candidateId: candidate.candidate_id,
      graphId: candidate.graph_loop_id,
      buildId: candidate.build_card_id,
      graphLabel: graphLoop?.label || 'Unnamed graph',
      buildLabel: candidate.build_title,
      choiceReason: (candidate.why_selected || [])[0] || 'Start with the safest reusable branch.',
      switchHint: 'Switch routes only if you need a different shared-page proof target.',
      evidenceRefs: createEvidenceRefs(candidate, graphLoop),
      nextStepTitle: 'Continue sandbox generation',
      nextStepSubtitle: `Keep ${candidate.title} and generate the next smallest proof branch.`,
      nextGenerationLabel: 'Generate the next sandbox branch',
      nextActions: createNextActions(candidate, graphLoop),
      context: buildBaseContext(candidate, themeContext)
    }
  })

export const buildWorldlineSandboxWorldline = (question, themeContext = {}, options = {}) => {
  const normalizedQuestion =
    typeof question === 'string' && question.trim() ? question.trim() : defaultQuestion
  const generationMode = options.mode === 'focused' ? 'focused' : 'base'
  const branches = buildBranches(normalizedQuestion, themeContext)
  const activeBranchId = branches[0]?.id || ''

  return {
    themeId: 'worldline-sandbox',
    moduleId: 'worldline-sandbox',
    rootQuestion: normalizedQuestion,
    questionDraft: normalizedQuestion,
    generatedAt: new Date().toISOString(),
    status: 'ready',
    sourceType:
      generationMode === 'focused' ? 'worldline-sandbox-focus-v1' : 'worldline-sandbox-base-v1',
    generationMode,
    generationRound: generationMode === 'focused' ? 2 : 1,
    branches,
    activeBranchId,
    selectedNodeId: activeBranchId,
    tree: createTreeData(branches, normalizedQuestion),
    viewState: {
      lastGeneratedFrom: generationMode === 'focused' ? 'focus-generate' : 'base-generate',
      protocolVersion: 'v1.2-alpha'
    },
    displayMeta: {
      stageLabel: 'Sandbox module',
      stageTitle: 'Prove the third module contract with the smallest useful surface',
      stageSubtitle:
        'This module exists only to validate that discovery, workbench, agent and graph remain facade-only.',
      branchCount: branches.length,
      themeName: 'Worldline Sandbox',
      generationLabel: 'Generate sandbox worldline',
      generationMode,
      workspaceHint: 'Pick a sandbox route first, then carry it into Agent or Graph.'
    }
  }
}

export const worldlineSandboxAdapter = {
  id: 'worldline-sandbox',
  defaultQuestion,
  buildWorldline: buildWorldlineSandboxWorldline,
  getDisplayLabel,
  getCardTitleById,
  getManifestSummary,
  getRecommendationCandidates,
  getRecommendationCandidateById,
  getGraphLoops,
  getGraphLoopById,
  getGraphDefaultKeyword,
  getThemeShowcaseMeta,
  getThemeShowcaseCandidates,
  getThemeShowcaseGraphs,
  getAgentContextView
}
