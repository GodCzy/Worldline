import {
  getCardTitleById,
  getGraphDefaultKeyword as getPoeGraphDefaultKeyword,
  getPoeDisplayLabel,
  poeManifestSummary,
  poeGraphLoops,
  poeRecommendationCandidates,
  getRecommendationCandidateById as getPoeRecommendationCandidateById
} from '@/data/poePhase1'

const defaultQuestion = '如果我是第一次接触 PoE，预算很低，又想要稳定开荒，我应该先沿哪条世界线开始？'

const baseTonePresets = [
  {
    branchTone: '稳态主线',
    riskLabel: '低风险',
    costLabel: '低投入',
    confidenceLabel: '适合起步',
    tone: 'calm',
    routeTone: '优先保证稳定推进和理解成本，适合把第一条世界线先走顺。'
  },
  {
    branchTone: '效率主线',
    riskLabel: '中风险',
    costLabel: '中投入',
    confidenceLabel: '适合追求节奏',
    tone: 'focus',
    routeTone: '更强调推进速度、清图效率和资源转化，但理解门槛更高。'
  },
  {
    branchTone: '成长主线',
    riskLabel: '中高风险',
    costLabel: '中高投入',
    confidenceLabel: '适合长期投入',
    tone: 'peak',
    routeTone: '把当前选择当作跳板，优先考虑中后期上限和后续转型空间。'
  }
]

const focusedPresets = [
  {
    idSuffix: 'stabilize',
    title: '稳住当前主线',
    branchTone: '稳态延展',
    riskLabel: '低风险',
    costLabel: '低到中投入',
    confidenceLabel: '适合继续铺稳',
    tone: 'calm',
    routeTone: '先补齐当前主线最关键的支撑点，保证节奏和容错。'
  },
  {
    idSuffix: 'accelerate',
    title: '加速当前主线',
    branchTone: '效率延展',
    riskLabel: '中风险',
    costLabel: '中投入',
    confidenceLabel: '适合追求效率',
    tone: 'focus',
    routeTone: '接受更高理解成本，换取更快的推进速度和更强的地图表现。'
  },
  {
    idSuffix: 'convert',
    title: '转向后期主线',
    branchTone: '成长延展',
    riskLabel: '中高风险',
    costLabel: '中高投入',
    confidenceLabel: '适合长线成长',
    tone: 'peak',
    routeTone: '围绕中后期形态提前布局，让当前世界线具备更强的扩展性。'
  }
]

const summarizeQuestion = (question = '') => {
  const normalized = typeof question === 'string' ? question.trim() : ''
  if (!normalized) {
    return defaultQuestion
  }
  return normalized.length > 56 ? `${normalized.slice(0, 55)}…` : normalized
}

export { defaultQuestion as poeWorldlineDefaultQuestion }

const resolveTreeDensity = (branchCount = 0) => {
  if (branchCount >= 8) {
    return { startY: 110, rowGap: 170, canvasBaseHeight: 300, canvasMinHeight: 760 }
  }
  if (branchCount >= 5) {
    return { startY: 115, rowGap: 160, canvasBaseHeight: 260, canvasMinHeight: 660 }
  }
  return { startY: 120, rowGap: 150, canvasBaseHeight: 220, canvasMinHeight: 560 }
}

const getGraphLoopById = (graphId) =>
  poeGraphLoops.find((graphLoop) => graphLoop.graph_id === graphId) || null

const getManifestSummary = () => ({ ...poeManifestSummary })

const getRecommendationCandidates = () => [...poeRecommendationCandidates]

const getGraphLoops = () => [...poeGraphLoops]

const getCandidateDisplayLabels = (candidate) => {
  const filters = candidate?.filters || {}
  return [
    filters.experience_level,
    filters.budget_level,
    ...(filters.playstyle || []).slice(0, 2),
    ...(filters.content_goals || []).slice(0, 1)
  ]
    .filter(Boolean)
    .map((item) => getPoeDisplayLabel(item) || item)
}

const createRecommendationContext = (candidate) => ({
  scene: candidate?.next_scene || 'build_recommend',
  focus: candidate?.candidate_id || '',
  candidate: candidate?.candidate_id || '',
  graph: candidate?.graph_loop_id || '',
  build: candidate?.build_card_id || '',
  entry: 'recommendation'
})

const createGraphContext = (graphLoop) => ({
  scene: 'graph_loop',
  focus: graphLoop?.focus || graphLoop?.graph_id || '',
  graph: graphLoop?.graph_id || '',
  build: graphLoop?.build_card_id || '',
  entry: 'graph'
})

const getThemeShowcaseMeta = () => ({
  eyebrow: '主题探索入口',
  title: '推荐路径与图谱闭环入口',
  description: '先看摘要，再按需展开细节。',
  stats: {
    cards: '样本卡片',
    recommendations: '推荐路径',
    graphs: '图谱闭环'
  },
  recommendationTitle: '推荐路径',
  recommendationDescription: '默认只展示关键摘要。',
  graphTitle: '图谱闭环',
  graphDescription: '主视图仅保留闭环摘要。',
  recommendationActionLabel: '写入路径上下文',
  recommendationChatLabel: '带此路径去对话',
  graphActionLabel: '写入图谱上下文',
  graphAdminLabel: '进入图谱页',
  graphUserLabel: '带此链路去对话'
})

const getThemeShowcaseCandidates = () =>
  poeRecommendationCandidates.map((candidate) => ({
    id: candidate.candidate_id,
    title: candidate.title,
    subtitle: candidate.build_title || getCardTitleById(candidate.build_card_id),
    badge: getPoeDisplayLabel(candidate.next_scene) || '默认场景',
    labels: getCandidateDisplayLabels(candidate),
    reasons: Array.isArray(candidate.why_selected) ? candidate.why_selected : [],
    relatedItems: Array.isArray(candidate.next_card_items) ? candidate.next_card_items : [],
    context: createRecommendationContext(candidate)
  }))

const getThemeShowcaseGraphs = () =>
  poeGraphLoops.map((graphLoop) => ({
    id: graphLoop.graph_id,
    title: graphLoop.label,
    subtitle: getCardTitleById(graphLoop.entry_card_id),
    badge: `${graphLoop.node_count} 节点 / ${graphLoop.edge_count} 边`,
    focusLabel: getPoeDisplayLabel(graphLoop.focus) || graphLoop.focus || '未命名闭环',
    nodePreview: (graphLoop.nodes || []).slice(0, 4).map((node) => `${node.type}: ${node.label}`),
    relatedItems: Array.isArray(graphLoop.related_cards) ? graphLoop.related_cards : [],
    context: createGraphContext(graphLoop)
  }))

const getAgentContextView = (activeContext = {}) => {
  const candidate = getPoeRecommendationCandidateById(activeContext?.candidate || '')
  const graphLoop = getGraphLoopById(activeContext?.graph || '')

  const candidateSummary = candidate
    ? {
        key: `candidate:${candidate.candidate_id}`,
        label: '当前路径',
        title: candidate.title,
        description: `对应方案：${candidate.build_title}，下一场景：${getPoeDisplayLabel(candidate.next_scene)}`
      }
    : null

  const graphSummary = graphLoop
    ? {
        key: `graph:${graphLoop.graph_id}`,
        label: '当前闭环',
        title: graphLoop.label,
        description: `聚焦：${getPoeDisplayLabel(graphLoop.focus)}，建议继续阅读 ${(graphLoop.related_cards || []).length} 张卡片`
      }
    : null

  if (!candidate) {
    return {
      candidateSummary,
      graphSummary,
      welcomePanel: null
    }
  }

  const firstReason = Array.isArray(candidate.why_selected) ? candidate.why_selected[0] : ''
  const nextCards = (candidate.next_card_items || [])
    .slice(0, 2)
    .map((item) => item.title)
    .filter(Boolean)
  const nextCardSummary = nextCards.length ? `建议先读 ${nextCards.join('、')}。` : ''

  return {
    candidateSummary,
    graphSummary,
    welcomePanel: {
      title: `欢迎沿着“${candidate.title}”继续提问`,
      description: `你当前选择的是 ${candidate.build_title}。${firstReason}${nextCardSummary}`,
      prompts: [
        `这条方案为什么适合我？`,
        `如果我按“${candidate.title}”开始，下一步应该先补什么？`,
        nextCards.length
          ? `基于当前路径，先读 ${nextCards.join('、')} 时要重点看什么？`
          : `基于当前路径，我下一张最该读哪张知识卡？`
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
      type: 'build_card',
      typeLabel: '构筑依据',
      summary: '这张构筑卡说明了为什么这条世界线成立，以及这条路线的核心形态是什么。'
    })
  }

  for (const item of candidate?.next_card_items || []) {
    evidence.push({
      id: item.id,
      title: item.title,
      type: 'knowledge_card',
      typeLabel: '知识支撑',
      summary: '这张知识卡解释了继续沿这条世界线推进时最值得先补齐的认知。'
    })
  }

  for (const item of graphLoop?.related_cards || []) {
    evidence.push({
      id: item.id,
      title: item.title,
      type: 'graph_support',
      typeLabel: '图谱支撑',
      summary: '这条图谱关系说明当前世界线背后的结构位置，而不是单点建议。'
    })
  }

  return evidence.slice(0, 6)
}

const buildBaseContext = (candidate, themeContext = {}) => ({
  ...themeContext,
  theme: 'poe',
  module: 'poe',
  scene: 'worldline_base',
  version: 'v1.2',
  focus: candidate.candidate_id,
  candidate: candidate.candidate_id,
  graph: candidate.graph_loop_id || '',
  build: candidate.build_card_id || '',
  entry: 'worldline-base'
})

const buildFocusedContext = (focusBranch, nextBranch, themeContext = {}) => ({
  ...themeContext,
  theme: 'poe',
  module: 'poe',
  scene: 'worldline_focus',
  version: 'v1.2',
  focus: focusBranch.focusKey || focusBranch.id,
  candidate: focusBranch.candidateId || '',
  graph: focusBranch.graphId || '',
  build: focusBranch.buildId || '',
  branch: nextBranch.id,
  entry: 'worldline-focus'
})

const createBaseNextActions = (candidate, graphLoop) => [
  {
    id: `${candidate.candidate_id}-continue`,
    label: '沿这条主线继续生成',
    description: '先锁定这条世界线，再继续展开下一层未来分支，而不是立即跳去对话。',
    targetType: 'continue',
    emphasis: 'primary'
  },
  {
    id: `${candidate.candidate_id}-chat`,
    label: '带着这条线继续对话',
    description: '把当前世界线的上下文带进聊天，继续追问执行细节和风险。',
    targetType: 'chat',
    emphasis: 'secondary'
  },
  {
    id: `${candidate.candidate_id}-graph`,
    label: '查看对应图谱支撑',
    description: graphLoop
      ? `进入 ${graphLoop.label}，查看这条世界线在知识图谱中的结构位置。`
      : '进入知识图谱页，继续追踪这条世界线的结构支撑。',
    targetType: 'graph',
    emphasis: 'ghost'
  }
]

const createFocusedNextActions = (branch, graphLoop) => [
  {
    id: `${branch.id}-continue`,
    label: branch.nextGenerationLabel || '继续生成后续世界线',
    description: '围绕当前主线继续往下展开，看这条世界线之后还能分出哪些未来路径。',
    targetType: 'continue',
    emphasis: 'primary'
  },
  {
    id: `${branch.id}-chat`,
    label: '带着当前主线深入对话',
    description: '把当前主线、节点信息和证据带入对话，深入追问执行细节。',
    targetType: 'chat',
    emphasis: 'secondary'
  },
  {
    id: `${branch.id}-graph`,
    label: '查看图谱支撑',
    description: graphLoop
      ? `进入 ${graphLoop.label}，对照当前主线的图谱结构。`
      : '进入知识图谱页，查看当前主线背后的结构支撑。',
    targetType: 'graph',
    emphasis: 'ghost'
  }
]

const createBaseTreeData = (branches = [], rootQuestion) => {
  const density = resolveTreeDensity(branches.length)

  const rootNode = {
    id: 'root-question',
    type: 'root',
    title: '起始问题',
    subtitle: summarizeQuestion(rootQuestion),
    meta: '基础输入',
    x: 120,
    y: 280,
    radius: 10,
    branchId: ''
  }

  const nodes = [rootNode]
  const edges = []

  branches.forEach((branch, index) => {
    const branchY = density.startY + index * density.rowGap

    const branchNode = {
      id: branch.id,
      type: 'branch',
      title: branch.title,
      subtitle: branch.subtitle,
      meta: `${branch.branchTone} / ${branch.riskLabel}`,
      x: 430,
      y: branchY,
      radius: 9,
      branchId: branch.id,
      badge: branch.choiceLabel,
      tone: branch.tone
    }

    const nextNode = {
      id: `${branch.id}-next`,
      type: 'next-step',
      title: '沿这条线继续生成',
      subtitle: branch.nextStepSubtitle,
      meta: branch.confidenceLabel,
      x: 760,
      y: branchY,
      radius: 8,
      branchId: branch.id,
      badge: '下一步',
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
        isHighlighted: branch.id === branches[0]?.id
      },
      {
        id: `edge-next-${branch.id}`,
        source: branch.id,
        target: nextNode.id,
        branchId: branch.id,
        kind: index === 0 ? 'primary' : 'guide',
        label: '继续生成',
        isHighlighted: branch.id === branches[0]?.id
      }
    )
  })

  return {
    width: 1080,
    height: Math.max(density.canvasMinHeight, density.canvasBaseHeight + branches.length * density.rowGap),
    nodes,
    edges
  }
}

const createFocusedTreeData = (focusBranch, branches = [], rootQuestion) => {
  const density = resolveTreeDensity(branches.length)

  const rootNode = {
    id: 'root-question',
    type: 'root',
    title: '起始问题',
    subtitle: summarizeQuestion(rootQuestion),
    meta: '输入锚点',
    x: 120,
    y: 280,
    radius: 9,
    branchId: ''
  }

  const focusNode = {
    id: `focus-${focusBranch.id}`,
    type: 'focus',
    title: focusBranch.title,
    subtitle: focusBranch.subtitle,
    meta: '当前主线',
    x: 380,
    y: 280,
    radius: 11,
    branchId: focusBranch.id,
    badge: focusBranch.branchTone || '当前主线',
    tone: focusBranch.tone
  }

  const nodes = [rootNode, focusNode]
  const edges = [
    {
      id: `edge-root-focus-${focusBranch.id}`,
      source: rootNode.id,
      target: focusNode.id,
      branchId: focusBranch.id,
      kind: 'primary',
      label: '当前选择',
      isHighlighted: true
    }
  ]

  branches.forEach((branch, index) => {
    const branchY = density.startY + index * density.rowGap

    const branchNode = {
      id: branch.id,
      type: 'branch',
      title: branch.title,
      subtitle: branch.subtitle,
      meta: `${branch.branchTone} / ${branch.riskLabel}`,
      x: 670,
      y: branchY,
      radius: 9,
      branchId: branch.id,
      badge: branch.choiceLabel,
      tone: branch.tone
    }

    const nextNode = {
      id: `${branch.id}-next`,
      type: 'next-step',
      title: '继续生成后续世界线',
      subtitle: branch.nextStepSubtitle,
      meta: branch.confidenceLabel,
      x: 980,
      y: branchY,
      radius: 8,
      branchId: branch.id,
      badge: '下一步',
      tone: branch.tone
    }

    nodes.push(branchNode, nextNode)
    edges.push(
      {
        id: `edge-focus-${branch.id}`,
        source: focusNode.id,
        target: branch.id,
        branchId: branch.id,
        kind: index === 0 ? 'primary' : 'secondary',
        label: branch.choiceLabel,
        isHighlighted: branch.id === branches[0]?.id
      },
      {
        id: `edge-next-${branch.id}`,
        source: branch.id,
        target: nextNode.id,
        branchId: branch.id,
        kind: index === 0 ? 'primary' : 'guide',
        label: '继续推进',
        isHighlighted: branch.id === branches[0]?.id
      }
    )
  })

  return {
    width: 1240,
    height: Math.max(density.canvasMinHeight, density.canvasBaseHeight + branches.length * density.rowGap),
    nodes,
    edges
  }
}

const buildBaseBranches = (question, themeContext = {}) =>
  poeRecommendationCandidates.slice(0, 3).map((candidate, index) => {
    const graphLoop = getGraphLoopById(candidate.graph_loop_id)
    const tone = baseTonePresets[index] || baseTonePresets[baseTonePresets.length - 1]
    const suitability = (candidate.filters?.playstyle || [])
      .map((item) => getPoeDisplayLabel(item))
      .filter(Boolean)

    return {
      id: candidate.candidate_id,
      title: candidate.title,
      subtitle: candidate.build_title || '未命名构筑',
      summary:
        (Array.isArray(candidate?.why_selected) && candidate.why_selected.join(' ')) ||
        `围绕“${summarizeQuestion(question)}”，这条世界线目前最适合作为第一条主线开始推进。`,
      branchTone: tone.branchTone,
      riskLabel: tone.riskLabel,
      costLabel: tone.costLabel,
      confidenceLabel: tone.confidenceLabel,
      routeTone: tone.routeTone,
      tone: tone.tone,
      choiceLabel: getPoeDisplayLabel(candidate.next_scene) || `分支 ${index + 1}`,
      suitability,
      focus: candidate.next_scene || 'build_recommend',
      focusKey: candidate.candidate_id,
      candidateId: candidate.candidate_id,
      graphId: candidate.graph_loop_id || '',
      buildId: candidate.build_card_id || '',
      graphLabel: graphLoop?.label || '未命名闭环',
      buildLabel: candidate.build_title || getCardTitleById(candidate.build_card_id),
      choiceReason:
        (Array.isArray(candidate?.why_selected) && candidate.why_selected[0]) ||
        '它在当前约束下兼顾了理解成本、推进节奏和构筑稳定性。',
      switchHint:
        index === 0
          ? '如果你更想追求清图效率，可以切到效率更强的世界线。'
          : index === 1
            ? '如果你发现当前节奏压力过高，可以切回更稳的世界线。'
            : '如果你想降低早期投入，可以退回更稳或更便宜的世界线。',
      evidenceRefs: createEvidenceRefs(candidate, graphLoop),
      nextStepTitle: '继续沿这条线生成',
      nextStepSubtitle: `先锁定 ${candidate.title}，再让模型围绕它继续展开下一层未来。`,
      nextGenerationLabel: '继续生成后续世界线',
      nextActions: createBaseNextActions(candidate, graphLoop),
      context: buildBaseContext(candidate, themeContext)
    }
  })

const buildFocusedBranches = (question, focusBranch, themeContext = {}) => {
  const graphLoop = getGraphLoopById(focusBranch.graphId)

  return focusedPresets.map((preset, index) => {
    const branchId = `${focusBranch.id}-${preset.idSuffix}`
    return {
      id: branchId,
      title: `${focusBranch.title} · ${preset.title}`,
      subtitle: index === 0 ? '先稳住当前主线' : index === 1 ? '把节奏推起来' : '开始为后期留空间',
      summary: `你已经选择了“${focusBranch.title}”。系统现在围绕它继续展开后续世界线，回答“${summarizeQuestion(question)}”在当前选择下还能如何推进。`,
      branchTone: preset.branchTone,
      riskLabel: preset.riskLabel,
      costLabel: preset.costLabel,
      confidenceLabel: preset.confidenceLabel,
      routeTone: preset.routeTone,
      tone: preset.tone,
      choiceLabel: preset.title,
      suitability: focusBranch.suitability || [],
      focus: focusBranch.focus || focusBranch.choiceLabel,
      focusKey: focusBranch.focusKey || focusBranch.id,
      candidateId: focusBranch.candidateId || '',
      graphId: focusBranch.graphId || '',
      buildId: focusBranch.buildId || '',
      graphLabel: focusBranch.graphLabel || graphLoop?.label || '未命名闭环',
      buildLabel: focusBranch.buildLabel || getCardTitleById(focusBranch.buildId),
      choiceReason: `系统把“${focusBranch.title}”当作当前主线，并生成这条延展世界线来回答下一步如何走。`,
      switchHint: '如果这条后续路径不符合你的资源、预算或风险偏好，可以回到上一层重新选择主线。',
      evidenceRefs: focusBranch.evidenceRefs || [],
      nextStepTitle: '继续生成更深一层世界线',
      nextStepSubtitle: `继续沿“${preset.title}”生成，观察这条未来路径还能怎样分叉。`,
      nextGenerationLabel: '继续生成更深一层世界线',
      nextActions: createFocusedNextActions(
        {
          ...focusBranch,
          id: branchId,
          title: `${focusBranch.title} · ${preset.title}`
        },
        graphLoop
      ),
      context: buildFocusedContext(focusBranch, { id: branchId }, themeContext)
    }
  })
}

const compactText = (value, max = 38) => {
  if (typeof value !== 'string') return value
  const normalized = value.trim()
  if (!normalized) return normalized
  return normalized.length > max ? `${normalized.slice(0, max - 1)}…` : normalized
}

const compactBranch = (branch = {}) => ({
  ...branch,
  subtitle: compactText(branch.subtitle, 18),
  summary: compactText(branch.summary, 50),
  routeTone: compactText(branch.routeTone, 28),
  choiceReason: compactText(branch.choiceReason, 30),
  switchHint: compactText(branch.switchHint, 30),
  nextStepSubtitle: compactText(branch.nextStepSubtitle, 32),
  evidenceRefs: (branch.evidenceRefs || []).map((item) => ({
    ...item,
    summary: compactText(item.summary, 32)
  })),
  nextActions: (branch.nextActions || []).map((action) => ({
    ...action,
    description: compactText(action.description, 30)
  }))
})

export const buildPoeWorldline = (
  question,
  themeContext = {},
  options = {
    mode: 'base',
    focusBranch: null,
    generationRound: 1
  }
) => {
  const normalizedQuestion =
    typeof question === 'string' && question.trim() ? question.trim() : defaultQuestion
  const generationMode = options.mode === 'focused' ? 'focused' : 'base'
  const generationRound = Number(options.generationRound || (generationMode === 'focused' ? 2 : 1))
  const focusBranch = options.focusBranch || null

  const branches =
    generationMode === 'focused' && focusBranch
      ? buildFocusedBranches(normalizedQuestion, focusBranch, themeContext)
      : buildBaseBranches(normalizedQuestion, themeContext)

  const compactBranches = branches.map((branch) => compactBranch(branch))
  const activeBranchId = compactBranches[0]?.id || ''
  const tree =
    generationMode === 'focused' && focusBranch
      ? createFocusedTreeData(focusBranch, compactBranches, normalizedQuestion)
      : createBaseTreeData(compactBranches, normalizedQuestion)

  return {
    themeId: 'poe',
    moduleId: 'poe',
    rootQuestion: normalizedQuestion,
    questionDraft: normalizedQuestion,
    generatedAt: new Date().toISOString(),
    status: 'ready',
    sourceType: generationMode === 'focused' ? 'poe-focus-v1' : 'poe-base-v1',
    generationMode,
    generationRound,
    viewState: {
      lastGeneratedFrom: generationMode === 'focused' ? 'focus-regenerate' : 'base-generate',
      protocolVersion: 'v1.2-alpha'
    },
    branches: compactBranches,
    activeBranchId,
    selectedNodeId: activeBranchId,
    tree,
    displayMeta: {
      stageLabel: generationMode === 'focused' ? '聚焦生成' : '基础生成',
      stageTitle:
        generationMode === 'focused'
          ? '围绕主线继续延展'
          : '先展开基础分支，再选主线',
      stageSubtitle:
        generationMode === 'focused'
          ? `已锁定“${focusBranch?.title || '当前主线'}”，继续生成下一层分支。`
          : '先看多条未来分支，再决定主线走向。',
      branchCount: compactBranches.length,
      themeName: getPoeDisplayLabel(themeContext.theme || 'poe') || 'PoE',
      generationLabel: generationMode === 'focused' ? '继续生成后续世界线' : '生成基础世界线',
      generationMode,
      workspaceHint:
        generationMode === 'focused'
          ? '已聚焦主线，继续生成后续分支。'
          : '先生成基础分支，再选一条主线推进。'
    }
  }
}

export const poeWorldlineAdapter = {
  id: 'poe',
  defaultQuestion,
  buildWorldline: buildPoeWorldline,
  getDisplayLabel: getPoeDisplayLabel,
  getCardTitleById,
  getManifestSummary,
  getRecommendationCandidates,
  getGraphLoops,
  getGraphLoopById,
  getGraphDefaultKeyword: getPoeGraphDefaultKeyword,
  getRecommendationCandidateById: getPoeRecommendationCandidateById,
  getThemeShowcaseMeta,
  getThemeShowcaseCandidates,
  getThemeShowcaseGraphs,
  getAgentContextView
}
