const defaultQuestion = '如果我要为一次发布前验收建立最小闭环，应该先沿哪条运营世界线开始？'

const manifestSummary = {
  card_count: 6
}

const cardTitleMap = {
  'ops-release-checklist': '发布检查清单',
  'ops-evidence-pack': '证据包收口',
  'ops-runtime-recovery': '运行恢复脚手架',
  'ops-rollout-window': '上线窗口编排',
  'ops-observability-readiness': '可观测性准备',
  'ops-escalation-path': '升级路径与责任人'
}

const labelMap = {
  release_gate: '发布闸门',
  evidence_pack: '证据包',
  runtime_recovery: '运行恢复',
  rollout_window: '上线窗口',
  observability: '可观测性',
  escalation: '升级路径',
  platform_ops: '平台运维',
  low_change: '低扰动',
  traceability: '证据优先',
  stability: '稳定优先',
  recovery_first: '恢复优先',
  release: '发布闭环',
  operations: '运营协同'
}

const recommendationCandidates = [
  {
    candidate_id: 'ops-release-gate',
    title: '发布前总闸门',
    build_title: '发布检查总闸门',
    next_scene: 'release_gate',
    graph_loop_id: 'ops-release-loop',
    build_card_id: 'ops-release-checklist',
    why_selected: [
      '先锁定发布前必须满足的检查项，避免把问题带进上线窗口。',
      '适合需要最小扰动和明确放行门槛的交付场景。'
    ],
    next_card_items: [
      { id: 'ops-release-checklist', title: '发布检查清单' },
      { id: 'ops-rollout-window', title: '上线窗口编排' }
    ],
    filters: {
      experience_level: 'platform_ops',
      budget_level: 'low_change',
      playstyle: ['stability', 'traceability'],
      content_goals: ['release']
    }
  },
  {
    candidate_id: 'ops-evidence-closure',
    title: '证据包收口',
    build_title: '统一证据包',
    next_scene: 'evidence_pack',
    graph_loop_id: 'ops-evidence-loop',
    build_card_id: 'ops-evidence-pack',
    why_selected: [
      '优先保证运行、接口和页面证据都可复放，适合审计和验收交付。',
      '适合需要把多条验证链收敛成单摘要的场景。'
    ],
    next_card_items: [
      { id: 'ops-evidence-pack', title: '证据包收口' },
      { id: 'ops-observability-readiness', title: '可观测性准备' }
    ],
    filters: {
      experience_level: 'platform_ops',
      budget_level: 'low_change',
      playstyle: ['traceability', 'stability'],
      content_goals: ['operations']
    }
  },
  {
    candidate_id: 'ops-recovery-baseline',
    title: '运行恢复基线',
    build_title: '恢复与回退路径',
    next_scene: 'runtime_recovery',
    graph_loop_id: 'ops-recovery-loop',
    build_card_id: 'ops-runtime-recovery',
    why_selected: [
      '先建立恢复顺序和回退边界，适合高风险变更前的准备。',
      '当你更关注故障收敛速度而不是功能扩展时，这条线最稳。'
    ],
    next_card_items: [
      { id: 'ops-runtime-recovery', title: '运行恢复脚手架' },
      { id: 'ops-escalation-path', title: '升级路径与责任人' }
    ],
    filters: {
      experience_level: 'platform_ops',
      budget_level: 'low_change',
      playstyle: ['recovery_first', 'stability'],
      content_goals: ['operations']
    }
  }
]

const graphLoops = [
  {
    graph_id: 'ops-release-loop',
    label: '发布闸门闭环',
    focus: 'release_gate',
    node_count: 5,
    edge_count: 4,
    entry_card_id: 'ops-release-checklist',
    build_card_id: 'ops-release-checklist',
    related_cards: [
      { id: 'ops-release-checklist', title: '发布检查清单' },
      { id: 'ops-rollout-window', title: '上线窗口编排' }
    ],
    nodes: [
      { type: 'check', label: '准入门槛' },
      { type: 'evidence', label: '证据摘要' },
      { type: 'window', label: '上线窗口' }
    ]
  },
  {
    graph_id: 'ops-evidence-loop',
    label: '证据留痕闭环',
    focus: 'evidence_pack',
    node_count: 4,
    edge_count: 3,
    entry_card_id: 'ops-evidence-pack',
    build_card_id: 'ops-evidence-pack',
    related_cards: [
      { id: 'ops-evidence-pack', title: '证据包收口' },
      { id: 'ops-observability-readiness', title: '可观测性准备' }
    ],
    nodes: [
      { type: 'runtime', label: '运行健康' },
      { type: 'api', label: '接口矩阵' },
      { type: 'ui', label: '页面证据' }
    ]
  },
  {
    graph_id: 'ops-recovery-loop',
    label: '恢复回退闭环',
    focus: 'runtime_recovery',
    node_count: 4,
    edge_count: 3,
    entry_card_id: 'ops-runtime-recovery',
    build_card_id: 'ops-runtime-recovery',
    related_cards: [
      { id: 'ops-runtime-recovery', title: '运行恢复脚手架' },
      { id: 'ops-escalation-path', title: '升级路径与责任人' }
    ],
    nodes: [
      { type: 'recover', label: '恢复顺序' },
      { type: 'rollback', label: '回退边界' },
      { type: 'owner', label: '责任升级' }
    ]
  }
]

const summarizeQuestion = (question = '') => {
  const normalized = typeof question === 'string' ? question.trim() : ''
  if (!normalized) {
    return defaultQuestion
  }
  return normalized.length > 56 ? `${normalized.slice(0, 55)}…` : normalized
}

const getDisplayLabel = (value = '') => labelMap[value] || value || ''

const getCardTitleById = (cardId = '') => cardTitleMap[cardId] || cardId || ''

const getManifestSummary = () => ({ ...manifestSummary })

const getRecommendationCandidates = () => recommendationCandidates.map((item) => ({ ...item }))

const getRecommendationCandidateById = (candidateId = '') =>
  recommendationCandidates.find((item) => item.candidate_id === candidateId) || null

const getGraphLoops = () => graphLoops.map((item) => ({ ...item }))

const getGraphLoopById = (graphId = '') => graphLoops.find((item) => item.graph_id === graphId) || null

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
  theme: 'worldline-ops',
  module: 'worldline-ops',
  scene: candidate?.next_scene || 'release_gate',
  version: 'phase6-pilot',
  focus: candidate?.candidate_id || '',
  candidate: candidate?.candidate_id || '',
  graph: candidate?.graph_loop_id || '',
  build: candidate?.build_card_id || '',
  entry: 'recommendation'
})

const createGraphContext = (graphLoop) => ({
  theme: 'worldline-ops',
  module: 'worldline-ops',
  scene: 'graph_loop',
  version: 'phase6-pilot',
  focus: graphLoop?.focus || graphLoop?.graph_id || '',
  graph: graphLoop?.graph_id || '',
  build: graphLoop?.build_card_id || '',
  entry: 'graph'
})

const getThemeShowcaseMeta = () => ({
  eyebrow: '第二模块试点',
  title: '运营世界线与闭环样本',
  description: '先验证模块接入契约，再决定是否继续扩展到更深的运营能力。',
  stats: {
    cards: '样本卡片',
    recommendations: '运营路径',
    graphs: '闭环图谱'
  },
  recommendationTitle: '运营路径',
  recommendationDescription: '保留最小摘要，验证 ThemeDetail 与 Agent handoff 消费链。',
  graphTitle: '闭环图谱',
  graphDescription: '仅提供最小图谱摘要，不引入新的后端图谱协议。',
  recommendationActionLabel: '写入路径上下文',
  recommendationChatLabel: '带此路径去对话',
  graphActionLabel: '写入图谱上下文',
  graphAdminLabel: '进入图谱页',
  graphUserLabel: '带此链路去对话'
})

const getThemeShowcaseCandidates = () =>
  recommendationCandidates.map((candidate) => ({
    id: candidate.candidate_id,
    title: candidate.title,
    subtitle: candidate.build_title,
    badge: getDisplayLabel(candidate.next_scene) || '默认场景',
    labels: getCandidateDisplayLabels(candidate),
    reasons: Array.isArray(candidate.why_selected) ? candidate.why_selected : [],
    relatedItems: Array.isArray(candidate.next_card_items) ? candidate.next_card_items : [],
    context: createRecommendationContext(candidate)
  }))

const getThemeShowcaseGraphs = () =>
  graphLoops.map((graphLoop) => ({
    id: graphLoop.graph_id,
    title: graphLoop.label,
    subtitle: getCardTitleById(graphLoop.entry_card_id),
    badge: `${graphLoop.node_count} 节点 / ${graphLoop.edge_count} 边`,
    focusLabel: getDisplayLabel(graphLoop.focus),
    nodePreview: (graphLoop.nodes || []).slice(0, 4).map((node) => `${node.type}: ${node.label}`),
    relatedItems: Array.isArray(graphLoop.related_cards) ? graphLoop.related_cards : [],
    context: createGraphContext(graphLoop)
  }))

const getAgentContextView = (activeContext = {}) => {
  const candidate = getRecommendationCandidateById(activeContext?.candidate || '')
  const graphLoop = getGraphLoopById(activeContext?.graph || '')

  const candidateSummary = candidate
    ? {
        key: `candidate:${candidate.candidate_id}`,
        label: '当前路径',
        title: candidate.title,
        description: `当前基于 ${candidate.build_title}，下一步聚焦 ${getDisplayLabel(candidate.next_scene)}。`
      }
    : null

  const graphSummary = graphLoop
    ? {
        key: `graph:${graphLoop.graph_id}`,
        label: '当前闭环',
        title: graphLoop.label,
        description: `当前闭环聚焦 ${getDisplayLabel(graphLoop.focus)}，覆盖 ${(graphLoop.related_cards || []).length} 条关联卡片。`
      }
    : null

  if (!candidate) {
    return {
      candidateSummary,
      graphSummary,
      welcomePanel: null
    }
  }

  return {
    candidateSummary,
    graphSummary,
    welcomePanel: {
      title: `继续沿“${candidate.title}”追问`,
      description: `系统已把 ${candidate.build_title} 和相关闭环写入主题上下文，可直接追问执行顺序、放行条件和风险。`,
      prompts: [
        `这条运营路径为什么最适合当前场景？`,
        `如果我沿着“${candidate.title}”推进，下一步先确认什么？`,
        `这条路径对应的回退边界和证据要求分别是什么？`
      ]
    }
  }
}

const createEvidenceRefs = (candidate, graphLoop) => {
  const evidence = []

  if (candidate?.build_card_id) {
    evidence.push({
      id: candidate.build_card_id,
      title: getCardTitleById(candidate.build_card_id),
      type: 'ops_card',
      typeLabel: '样本卡片',
      summary: '这张卡片描述当前运营路径最关键的检查项或执行顺序。'
    })
  }

  for (const item of candidate?.next_card_items || []) {
    evidence.push({
      id: item.id,
      title: item.title,
      type: 'next_card',
      typeLabel: '下一步材料',
      summary: '这张材料用于补齐当前路径继续推进时最关键的上下文。'
    })
  }

  for (const item of graphLoop?.related_cards || []) {
    evidence.push({
      id: item.id,
      title: item.title,
      type: 'graph_support',
      typeLabel: '闭环支撑',
      summary: '这条图谱闭环说明当前路径在运营流程中的结构位置。'
    })
  }

  return evidence.slice(0, 6)
}

const createNextActions = (candidate, graphLoop) => [
  {
    id: `${candidate.candidate_id}-continue`,
    label: '继续沿此路径展开',
    description: '保留当前路径与上下文，再生成下一层分支。',
    targetType: 'continue',
    emphasis: 'primary'
  },
  {
    id: `${candidate.candidate_id}-chat`,
    label: '带着当前路径去对话',
    description: '把当前路径和闭环上下文交给 Agent，继续追问执行细节。',
    targetType: 'chat',
    emphasis: 'secondary'
  },
  {
    id: `${candidate.candidate_id}-graph`,
    label: '查看对应闭环',
    description: graphLoop
      ? `进入 ${graphLoop.label}，检查这条路径的结构支撑。`
      : '进入图谱页，查看当前路径对应的闭环摘要。',
    targetType: 'graph',
    emphasis: 'ghost'
  }
]

const createTreeData = (branches = [], rootQuestion = '') => {
  const rootNode = {
    id: 'root-question',
    type: 'root',
    title: '起始问题',
    subtitle: summarizeQuestion(rootQuestion),
    meta: '运营输入',
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
      title: '继续推进',
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
        label: '继续推进',
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
  theme: 'worldline-ops',
  module: 'worldline-ops',
  scene: candidate.next_scene,
  version: 'phase6-pilot',
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
    const branchTone = index === 0 ? '放行主线' : index === 1 ? '证据主线' : '恢复主线'
    const riskLabel = index === 2 ? '中风险' : '低风险'
    const costLabel = index === 1 ? '中投入' : '低投入'
    const confidenceLabel = index === 0 ? '适合先定闸门' : index === 1 ? '适合先收证据' : '适合先做恢复'

    return {
      id: candidate.candidate_id,
      title: candidate.title,
      subtitle: candidate.build_title,
      summary:
        (candidate.why_selected || []).join(' ') ||
        `围绕“${summarizeQuestion(question)}”，系统给出一条最小运营路径。`,
      branchTone,
      riskLabel,
      costLabel,
      confidenceLabel,
      routeTone: '维持最小扰动，先让检查项和责任边界可执行。',
      tone,
      choiceLabel: getDisplayLabel(candidate.next_scene),
      suitability: getCandidateDisplayLabels(candidate),
      focus: candidate.next_scene,
      focusKey: candidate.candidate_id,
      candidateId: candidate.candidate_id,
      graphId: candidate.graph_loop_id,
      buildId: candidate.build_card_id,
      graphLabel: graphLoop?.label || '未命名闭环',
      buildLabel: candidate.build_title,
      choiceReason: (candidate.why_selected || [])[0] || '优先满足最关键的运营约束。',
      switchHint: '如果当前关注点变化，可以返回上一层重新选主线。',
      evidenceRefs: createEvidenceRefs(candidate, graphLoop),
      nextStepTitle: '继续沿当前路径生成',
      nextStepSubtitle: `先固定 ${candidate.title}，再继续生成更细的执行分支。`,
      nextGenerationLabel: '继续生成下一层世界线',
      nextActions: createNextActions(candidate, graphLoop),
      context: buildBaseContext(candidate, themeContext)
    }
  })

export const buildWorldlineOpsWorldline = (question, themeContext = {}, options = {}) => {
  const normalizedQuestion =
    typeof question === 'string' && question.trim() ? question.trim() : defaultQuestion
  const generationMode = options.mode === 'focused' ? 'focused' : 'base'
  const branches = buildBranches(normalizedQuestion, themeContext)
  const activeBranchId = branches[0]?.id || ''

  return {
    themeId: 'worldline-ops',
    moduleId: 'worldline-ops',
    rootQuestion: normalizedQuestion,
    questionDraft: normalizedQuestion,
    generatedAt: new Date().toISOString(),
    status: 'ready',
    sourceType: generationMode === 'focused' ? 'worldline-ops-focus-v1' : 'worldline-ops-base-v1',
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
      stageLabel: '运营试点',
      stageTitle: '先固定运营主线，再推进下一层分支',
      stageSubtitle: '当前模块只验证第二模块如何被平台发现与消费，不扩到后端能力。',
      branchCount: branches.length,
      themeName: 'Worldline Ops',
      generationLabel: '生成基础世界线',
      generationMode,
      workspaceHint: '先选一条运营主线，再把它带入 Agent 或 Graph。'
    }
  }
}

export const worldlineOpsAdapter = {
  id: 'worldline-ops',
  defaultQuestion,
  buildWorldline: buildWorldlineOpsWorldline,
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
