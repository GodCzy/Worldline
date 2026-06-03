const previewEvidence = [
  {
    id: 'ev-docling-001',
    evidenceId: 'ev-docling-001',
    title: 'Knowledge Compiler 结构化解析记录',
    type: 'document_node',
    typeLabel: 'EvidenceAnchor',
    summary: 'Docling 输出被编译为 SourceAsset、DocumentVersion、DocumentNode 与 EvidenceAnchor。',
    sourceUri: 'worldline://docs/architecture/knowledge-compiler',
    page: 1,
    lineStart: 18,
    lineEnd: 42,
    bbox: [92, 140, 820, 310]
  },
  {
    id: 'ev-wiki-014',
    evidenceId: 'ev-wiki-014',
    title: 'LLM Wiki 引用覆盖记录',
    type: 'wiki_citation',
    typeLabel: 'Wiki Citation',
    summary: 'Wiki 页面必须回链到证据锚点，RAG 仅作为候选上下文和长尾回查。',
    sourceUri: 'worldline://wiki/evidence-backed-llm-wiki',
    page: 2,
    lineStart: 7,
    lineEnd: 23
  },
  {
    id: 'ev-graph-031',
    evidenceId: 'ev-graph-031',
    title: 'Temporal Evidence Graph episode',
    type: 'graph_episode',
    typeLabel: 'Graph Episode',
    summary: '实体、关系和 temporal fact 带有 provenance、validity window 与 episode 归属。',
    sourceUri: 'worldline://graph/temporal-evidence',
    page: 3,
    lineStart: 12,
    lineEnd: 36
  }
]

const previewWikiRefs = [
  {
    id: 'wiki-evidence-backed-llm-wiki',
    title: 'Evidence-backed LLM Wiki',
    slug: 'evidence-backed-llm-wiki',
    status: 'pending_review',
    evidenceCoverage: { status: 'covered', ratio: 1 }
  },
  {
    id: 'wiki-temporal-graph',
    title: 'Temporal Evidence Graph',
    slug: 'temporal-evidence-graph',
    status: 'pending_review',
    evidenceCoverage: { status: 'covered', ratio: 0.86 }
  }
]

const previewEntityRefs = [
  {
    id: 'ent-compiler',
    name: 'Knowledge Compiler',
    type: 'system_layer',
    confidence: 0.94,
    evidenceId: 'ev-docling-001'
  },
  {
    id: 'ent-wiki',
    name: 'LLM Wiki',
    type: 'knowledge_surface',
    confidence: 0.92,
    evidenceId: 'ev-wiki-014'
  },
  {
    id: 'ent-graph',
    name: 'Temporal Evidence Graph',
    type: 'graph_layer',
    confidence: 0.9,
    evidenceId: 'ev-graph-031'
  }
]

const previewTimelineRefs = [
  {
    id: 'tf-source',
    label: 'SourceAsset 入账',
    validFrom: '2026-06-03T08:00:00Z',
    validTo: '',
    status: 'observed',
    evidenceId: 'ev-docling-001'
  },
  {
    id: 'tf-wiki',
    label: 'LLM Wiki 重建',
    validFrom: '2026-06-03T10:00:00Z',
    validTo: '',
    status: 'observed',
    evidenceId: 'ev-wiki-014'
  },
  {
    id: 'tf-gate',
    label: '质量门禁通过',
    validFrom: '2026-06-03T12:00:00Z',
    validTo: '',
    status: 'validated',
    evidenceId: 'ev-graph-031'
  }
]

const previewSnapshots = [
  {
    id: 'source',
    label: 'Source',
    title: '证据入账',
    metric: 3,
    summary: '文档、页面和代码证据被锚定为可回查的 EvidenceAnchor。'
  },
  {
    id: 'wiki',
    label: 'Wiki',
    title: 'LLM Wiki 主线',
    metric: 2,
    summary: 'Wiki 组织知识结构，RAG 只做辅助召回和证据候选。'
  },
  {
    id: 'graph',
    label: 'Graph',
    title: '时间图谱投影',
    metric: 6,
    summary: '实体、关系、episode 和 validity window 组成 Temporal Evidence Graph。'
  },
  {
    id: 'gate',
    label: 'Gate',
    title: '质量门禁',
    metric: 4,
    summary: '引用覆盖率、图谱一致性、时间冲突和 Agent handoff 进入验收。'
  }
]

const branchBase = {
  riskLabel: '可验证',
  costLabel: '低扰动',
  confidenceLabel: '证据覆盖',
  suitability: ['重构规划', '演示验证', '知识库接入'],
  graphId: 'phase5-graph-focus',
  buildId: 'phase5-ui-build',
  graphLabel: 'Phase 5 Evidence Graph',
  buildLabel: 'Worldline UI v1',
  evidenceRefs: previewEvidence,
  wikiRefs: previewWikiRefs,
  entityRefs: previewEntityRefs,
  timelineRefs: previewTimelineRefs,
  quality: {
    status: 'inspectable',
    evidenceCount: previewEvidence.length,
    supportChannels: 4,
    citationCoverage: 1,
    graphSupport: true,
    temporalSupport: true
  }
}

const buildBranches = (question, context = {}) => [
  {
    ...branchBase,
    id: 'wiki-first',
    title: 'LLM Wiki 主导线',
    subtitle: '先把事实编译成可审核页面',
    summary: `围绕「${question}」，先形成带引用、backlinks、staleness 和人工审核状态的 LLM Wiki，再让 RAG 只做证据候选召回。`,
    branchTone: 'Wiki',
    routeTone: '适合把项目从普通聊天知识库提升为可浏览、可引用、可审查的知识 OS。',
    tone: 'calm',
    choiceLabel: 'Wiki First',
    focus: 'wiki-first',
    focusKey: 'wiki-first',
    candidateId: 'wiki-first',
    choiceReason: '用户需要吸引人的界面和实际作用，Wiki 主线能把知识变成可交付资产。',
    switchHint: '如果引用覆盖率下降，先回到 Evidence Ledger 补证据，再继续扩写页面。',
    nextStepTitle: '进入 Wiki 审核',
    nextStepSubtitle: '检查引用覆盖、页面结构和 stale 状态。',
    nextGenerationLabel: '扩展 Wiki 世界线',
    nextActions: [
      {
        id: 'wiki-first-chat',
        label: '带此分支去对话',
        description: '让 Agent 基于当前 Wiki、证据和图谱上下文继续推理。',
        targetType: 'chat',
        emphasis: 'primary'
      },
      {
        id: 'wiki-first-graph',
        label: '查看图谱支撑',
        description: '在图谱页聚焦 LLM Wiki 相关实体和证据关系。',
        targetType: 'graph',
        emphasis: 'secondary'
      }
    ],
    context: {
      ...context,
      theme: 'phase5-preview',
      module: 'phase5-preview',
      scene: 'wiki_first',
      entry: 'worldline-preview',
      focus: 'wiki-first',
      branch: 'wiki-first',
      graph: 'phase5-graph-focus'
    }
  },
  {
    ...branchBase,
    id: 'graph-temporal',
    title: '时间图谱推理线',
    subtitle: '把变化、冲突和 provenance 放到主舞台',
    summary: '该分支把 Graphiti 风格 episode、validity window 和 provenance 用在 Worldline 图谱中，用于观察事实如何随时间变化。',
    branchTone: 'Graph',
    routeTone: '适合做高可信追踪、冲突检测和多版本知识演化。',
    tone: 'focus',
    choiceLabel: 'Temporal Graph',
    focus: 'graph-temporal',
    focusKey: 'graph-temporal',
    candidateId: 'graph-temporal',
    choiceReason: '世界线产品的差异化来自时间变化和可验证的分叉收束。',
    switchHint: '如果实体噪声过高，先收敛 schema 与抽取阈值，再开放大图谱浏览。',
    nextStepTitle: '运行时间冲突检查',
    nextStepSubtitle: '检查 temporal facts 是否存在 validity window 冲突。',
    nextGenerationLabel: '扩展图谱世界线',
    nextActions: [
      {
        id: 'graph-temporal-graph',
        label: '查看图谱支撑',
        description: '进入图谱页查看实体、关系和时间事实。',
        targetType: 'graph',
        emphasis: 'primary'
      },
      {
        id: 'graph-temporal-chat',
        label: '带此分支去对话',
        description: '让 Agent 解释冲突和下一步验证路径。',
        targetType: 'chat',
        emphasis: 'secondary'
      }
    ],
    context: {
      ...context,
      theme: 'phase5-preview',
      module: 'phase5-preview',
      scene: 'graph_timeline',
      entry: 'worldline-preview',
      focus: 'graph-temporal',
      branch: 'graph-temporal',
      graph: 'phase5-graph-focus'
    }
  },
  {
    ...branchBase,
    id: 'agent-gate',
    title: 'Agent 交接与质量门禁线',
    subtitle: '让每次跳转都带着证据上下文',
    summary: '该分支验证 Agent handoff、质量门禁、截图证据和可回放评估，避免世界线只是好看的视觉层。',
    branchTone: 'Gate',
    routeTone: '适合进入公开演示前的验收、成本统计和回放评估。',
    tone: 'peak',
    choiceLabel: 'Quality Gate',
    focus: 'agent-gate',
    focusKey: 'agent-gate',
    candidateId: 'agent-gate',
    choiceReason: '前沿 AI 项目需要可复验的质量证据，而不是只展示一次生成结果。',
    switchHint: '如果截图、质量门禁或引用覆盖任一失败，先修复当前阶段，不叠加新功能。',
    nextStepTitle: '执行验收回放',
    nextStepSubtitle: '收集构建、截图、质量门禁和 Agent handoff 证据。',
    nextGenerationLabel: '扩展验收世界线',
    nextActions: [
      {
        id: 'agent-gate-chat',
        label: '带此分支去对话',
        description: '把验收上下文交给 Agent 生成下一轮执行计划。',
        targetType: 'chat',
        emphasis: 'primary'
      },
      {
        id: 'agent-gate-graph',
        label: '查看图谱支撑',
        description: '检查质量门禁与证据节点的关系。',
        targetType: 'graph',
        emphasis: 'secondary'
      }
    ],
    context: {
      ...context,
      theme: 'phase5-preview',
      module: 'phase5-preview',
      scene: 'quality_gate',
      entry: 'worldline-preview',
      focus: 'agent-gate',
      branch: 'agent-gate',
      graph: 'phase5-graph-focus'
    }
  }
]

const buildTree = (branches, question) => {
  const nodes = [
    {
      id: 'root-question',
      type: 'root',
      title: '起始问题',
      subtitle: question,
      meta: 'Phase 5',
      x: 90,
      y: 300,
      radius: 12,
      branchId: ''
    },
    {
      id: 'convergence',
      type: 'convergence',
      title: '收束验证',
      subtitle: 'Evidence / Graph / Gate',
      meta: 'Worldline OS',
      x: 1120,
      y: 300,
      radius: 13,
      branchId: branches[0]?.id || '',
      tone: 'peak'
    }
  ]
  const edges = []

  branches.forEach((branch, index) => {
    const y = 150 + index * 150
    nodes.push({
      id: branch.id,
      type: 'branch',
      title: branch.title,
      subtitle: branch.subtitle,
      meta: `${branch.choiceLabel} / ${branch.confidenceLabel}`,
      x: 420,
      y,
      radius: 10,
      branchId: branch.id,
      tone: branch.tone
    })
    nodes.push({
      id: `${branch.id}-inspect`,
      type: 'next-step',
      title: branch.nextStepTitle,
      subtitle: branch.nextStepSubtitle,
      meta: 'Inspect',
      x: 780,
      y,
      radius: 8,
      branchId: branch.id,
      tone: branch.tone
    })
    edges.push(
      {
        id: `edge-root-${branch.id}`,
        source: 'root-question',
        target: branch.id,
        branchId: branch.id,
        kind: index === 0 ? 'primary' : 'secondary',
        label: branch.choiceLabel,
        isHighlighted: index === 0
      },
      {
        id: `edge-inspect-${branch.id}`,
        source: branch.id,
        target: `${branch.id}-inspect`,
        branchId: branch.id,
        kind: 'guide',
        label: 'inspect',
        isHighlighted: index === 0
      },
      {
        id: `edge-converge-${branch.id}`,
        source: `${branch.id}-inspect`,
        target: 'convergence',
        branchId: branch.id,
        kind: 'convergence',
        label: 'gate',
        isHighlighted: index === 0
      }
    )
  })

  return {
    width: 1220,
    height: 620,
    nodes,
    edges
  }
}

const phase5PreviewAdapter = {
  defaultQuestion:
    '如何把 Worldline 打造成 Evidence-backed LLM Wiki + Temporal Knowledge Graph OS，并完成可验证前端工作台？',

  buildWorldline(question, context = {}) {
    const normalizedQuestion = question?.trim() || this.defaultQuestion
    const branches = buildBranches(normalizedQuestion, context)

    return {
      themeId: 'phase5-preview',
      moduleId: 'phase5-preview',
      knowledgeDbId: 'phase5-preview',
      knowledgeMode: 'llm_wiki_primary_rag_auxiliary',
      layers: ['evidence_ledger', 'llm_wiki', 'temporal_evidence_graph', 'quality_gate', 'agent_handoff'],
      rootQuestion: normalizedQuestion,
      questionDraft: normalizedQuestion,
      status: 'ready',
      sourceType: 'phase5-preview-adapter',
      generationMode: 'base',
      generationRound: 1,
      branches,
      activeBranchId: branches[0].id,
      selectedNodeId: branches[0].id,
      tree: buildTree(branches, normalizedQuestion),
      snapshots: previewSnapshots,
      quality: {
        status: 'inspectable',
        gateId: 'phase5-preview-gate',
        branchCount: branches.length,
        citationCoverage: 1,
        latestGate: {
          status: 'passed',
          metrics: {
            citation_coverage: 1,
            temporal_conflict_count: 0
          }
        }
      },
      routeTrace: {
        adapter: 'phase5PreviewAdapter',
        deterministic_baseline: true,
        evidence_count: previewEvidence.length,
        wiki_page_count: previewWikiRefs.length,
        entity_count: previewEntityRefs.length,
        timeline_count: previewTimelineRefs.length
      },
      viewState: {
        lastGeneratedFrom: 'phase5-preview',
        protocolVersion: 'worldline-phase5-preview'
      },
      displayMeta: {
        stageLabel: 'Phase 5 Preview',
        stageTitle: 'Worldline 前端工作台',
        stageSubtitle: '黑底青金世界线、证据轨、时间 scrubber、图谱聚焦与 Agent handoff 同屏验证。',
        branchCount: branches.length,
        themeName: 'Phase 5 Preview',
        generationLabel: '生成预览世界线',
        generationMode: 'base',
        workspaceHint: '真实知识库接入后，live facade 会替代本地预览数据。'
      },
      overview: {
        status: 'ready',
        counts: {
          evidence_anchors: previewEvidence.length,
          wiki_pages: previewWikiRefs.length,
          entities: previewEntityRefs.length,
          temporal_facts: previewTimelineRefs.length
        },
        quality_gate: {
          latest: {
            status: 'passed'
          }
        }
      }
    }
  },

  getDisplayLabel(value = '') {
    const labels = {
      'phase5-graph-focus': 'Phase 5 图谱聚焦',
      'wiki-first': 'LLM Wiki 主导线',
      'graph-temporal': '时间图谱推理线',
      'agent-gate': 'Agent 交接与质量门禁线'
    }
    return labels[value] || value
  },

  getGraphLoops() {
    return [
      {
        id: 'phase5-graph-focus',
        label: 'Phase 5 Evidence Graph',
        focus: 'phase5-graph-focus',
        node_count: previewEntityRefs.length,
        edge_count: 4
      }
    ]
  },

  getGraphLoopById(graphId = '') {
    return this.getGraphLoops().find((item) => item.id === graphId || item.focus === graphId) || null
  },

  getGraphDefaultKeyword() {
    return 'Worldline'
  },

  getManifestSummary() {
    return {
      card_count: 3,
      evidence_count: previewEvidence.length,
      graph_count: previewEntityRefs.length
    }
  },

  getThemeShowcaseMeta() {
    return {
      title: 'Phase 5 Preview',
      subtitle: '当前前端验收模块',
      description: '用于展示 Worldline 工作台的阶段 5 视觉与交互目标。'
    }
  },

  getThemeShowcaseCandidates() {
    return buildBranches(this.defaultQuestion)
  },

  getThemeShowcaseGraphs() {
    return this.getGraphLoops()
  },

  getAgentContextView(activeContext = {}) {
    return {
      title: this.getDisplayLabel(activeContext.branch || activeContext.focus || 'phase5-preview'),
      description: '来自 Worldline Phase 5 工作台的证据、图谱与质量门禁上下文。',
      chips: ['Evidence', 'Wiki', 'Graph', 'Gate']
    }
  }
}

export default phase5PreviewAdapter
