const nowIso = () => new Date().toISOString()

export const AGENT_WORKBENCH_PROTOCOL = 'worldline-agent-workbench-v0.1'

export const agentRunContract = {
  WorldlineRun: [
    'id',
    'title',
    'goal',
    'status',
    'createdBy',
    'budget',
    'qualitySummary'
  ],
  WorldlineBranch: [
    'id',
    'parentId',
    'branchType',
    'hypothesis',
    'action',
    'result',
    'evidenceIds',
    'toolCallIds',
    'temporalFactIds',
    'gateResultIds',
    'status',
    'score'
  ],
  AgentEpisode: [
    'runId',
    'branchId',
    'actor',
    'input',
    'output',
    'toolCalls',
    'diffs',
    'screenshots',
    'cost',
    'gateResults',
    'artifactIds'
  ],
  ToolTrace: [
    'id',
    'branchId',
    'name',
    'status',
    'permission',
    'summary',
    'result',
    'artifactIds',
    'artifacts',
    'failureReason'
  ],
  QualityGateResult: [
    'id',
    'label',
    'status',
    'value',
    'summary',
    'branchId',
    'threshold',
    'input',
    'toolCallIds',
    'artifactIds',
    'failureReason',
    'remediation'
  ],
  ArtifactRef: [
    'id',
    'label',
    'type',
    'path',
    'summary',
    'toolCallId'
  ],
  SourceAsset: [
    'id',
    'sourceUri',
    'kind',
    'label',
    'lineStart',
    'lineEnd',
    'evidenceId'
  ],
  DocumentNode: [
    'id',
    'sourceAssetId',
    'nodeKind',
    'title',
    'lineStart',
    'lineEnd',
    'evidenceId'
  ],
  SkillProposal: [
    'name',
    'trigger',
    'steps',
    'requiredPermissions',
    'evidenceRunIds',
    'evalScore',
    'status'
  ]
}

const evidenceRefs = [
  {
    id: 'ev-worldline-contract',
    evidenceId: 'ev-worldline-contract',
    title: 'Worldline backend contract',
    type: 'contract',
    typeLabel: 'EvidenceAnchor',
    summary: 'Existing Worldline routes expose wiki, graph, temporal timeline, MCP audit, workflow planning, golden set, and quality gate surfaces.',
    sourceUri: 'server/routers/knowledge_router.py',
    lineStart: 1284,
    lineEnd: 1443,
    sourceRef: {
      id: 'source-worldline-knowledge-router',
      kind: 'FastAPI router',
      label: 'Worldline knowledge router endpoints',
      documentNodeId: 'docnode-worldline-api-surface',
      documentNodeLabel: 'Worldline API surface',
      role: 'Defines controlled backend routes consumed by the Worldline frontend and MCP boundary.',
      capability: 'MCP manifest, overview, generate, workflow planning, golden set, quality gate'
    }
  },
  {
    id: 'ev-agent-workflow',
    evidenceId: 'ev-agent-workflow',
    title: 'Controlled Agent workflow lanes',
    type: 'service',
    typeLabel: 'WorldlineAgentWorkflowService',
    summary: 'Subagent lanes are split into research reviewer, knowledge operator, frontend QA, and release auditor with controlled write scopes.',
    sourceUri: 'src/services/worldline_agent_workflow_service.py',
    lineStart: 10,
    lineEnd: 122,
    sourceRef: {
      id: 'source-agent-workflow-service',
      kind: 'Python service',
      label: 'WorldlineAgentWorkflowService',
      documentNodeId: 'docnode-agent-workflow-lanes',
      documentNodeLabel: 'Controlled subagent lane manifest',
      role: 'Defines controlled agent lanes, write scopes, tool permissions, and handoff requirements.',
      capability: 'research_reviewer, knowledge_operator, frontend_qa, release_auditor'
    }
  },
  {
    id: 'ev-workbench-facade',
    evidenceId: 'ev-workbench-facade',
    title: 'Live workbench facade',
    type: 'service',
    typeLabel: 'WorldlineWorkbenchService',
    summary: 'The current facade already composes evidence, wiki, graph, timeline, MCP, and quality gate data into a frontend-friendly Worldline payload.',
    sourceUri: 'src/services/worldline_workbench_service.py',
    lineStart: 22,
    lineEnd: 190,
    sourceRef: {
      id: 'source-worldline-workbench-facade',
      kind: 'Python service',
      label: 'WorldlineWorkbenchService facade',
      documentNodeId: 'docnode-workbench-live-payload',
      documentNodeLabel: 'Live workbench payload composer',
      role: 'Composes SourceAsset, DocumentVersion, EvidenceAnchor, Wiki, graph, timeline, MCP, and gate data.',
      capability: 'live overview, generate_worldline, branch hydration, route trace'
    }
  }
]

const wikiRefs = [
  {
    id: 'wiki-agent-os',
    title: 'Agent Worldline OS',
    slug: 'agent-worldline-os',
    status: 'draft',
    evidenceCoverage: 0.86,
    summary: 'A task is represented as a branching, replayable, evidence-bound worldline instead of a hidden chat transcript.'
  },
  {
    id: 'wiki-skill-genome',
    title: 'Skill Genome',
    slug: 'skill-genome',
    status: 'candidate',
    evidenceCoverage: 0.74,
    summary: 'Successful agent paths can become versioned skill proposals after gate approval.'
  }
]

const entityRefs = [
  {
    id: 'entity-worldline-run',
    name: 'WorldlineRun',
    type: 'agent_runtime',
    confidence: 0.94,
    evidenceId: 'ev-worldline-contract'
  },
  {
    id: 'entity-evidence-anchor',
    name: 'EvidenceAnchor',
    type: 'knowledge_asset',
    confidence: 0.92,
    evidenceId: 'ev-workbench-facade'
  },
  {
    id: 'entity-skill-proposal',
    name: 'SkillProposal',
    type: 'self_evolving_skill',
    confidence: 0.88,
    evidenceId: 'ev-agent-workflow'
  }
]

const timelineRefs = [
  {
    id: 'tf-stage1',
    label: 'Local preview remains available as fallback',
    validFrom: '2026-06-04',
    validTo: 'present',
    status: 'observed',
    evidenceId: 'ev-workbench-facade'
  },
  {
    id: 'tf-stage2',
    label: 'Persistent run ledger API is available',
    validFrom: '2026-06-08',
    validTo: 'present',
    status: 'observed',
    evidenceId: 'ev-worldline-contract'
  }
]

const makeQuality = (coverage, status = 'inspectable') => ({
  status,
  evidenceCount: evidenceRefs.length,
  supportChannels: 4,
  citationCoverage: coverage,
  graphSupport: true,
  temporalSupport: true
})

const branchTemplates = [
  {
    id: 'branch-plan',
    title: '规划分支',
    subtitle: '先把目标拆成可验证 Agent 路线',
    branchType: 'plan',
    tone: 'focus',
    choiceLabel: 'Plan',
    stageLabel: 'planner',
    summary: '把“世界线”升级为 Agent 工作台：任务先进入计划分支，确定约束、证据源、可执行动作和质量门，再决定是否进入工具执行。',
    choiceReason: '避免把 Agent 行为隐藏在聊天流里；先暴露计划、假设和审批点，再执行。',
    nextStepTitle: '审批执行分支',
    score: 0.91,
    quality: makeQuality(0.82),
    toolCallIds: [],
    evidenceIds: ['ev-worldline-contract'],
    temporalFactIds: ['tf-stage1'],
    gateResultIds: ['gate-evidence']
  },
  {
    id: 'branch-evidence',
    title: '证据分支',
    subtitle: '每个结论先绑定 EvidenceAnchor',
    branchType: 'evidence',
    tone: 'calm',
    choiceLabel: 'Evidence',
    stageLabel: 'auditor',
    summary: '将任务中的关键判断绑定到 EvidenceAnchor、Wiki refs、实体和 temporal facts，缺证据的结论不能进入通过状态。',
    choiceReason: 'Worldline 的差异点是证据优先，而不是更长的上下文窗口。',
    nextStepTitle: '运行证据覆盖检查',
    score: 0.94,
    quality: makeQuality(0.9),
    toolCallIds: ['tool-query-evidence'],
    evidenceIds: ['ev-worldline-contract', 'ev-workbench-facade'],
    temporalFactIds: ['tf-stage1'],
    gateResultIds: ['gate-evidence', 'gate-conflict']
  },
  {
    id: 'branch-tool',
    title: '工具执行分支',
    subtitle: '工具调用必须显示权限和审计边界',
    branchType: 'tool_action',
    tone: 'peak',
    choiceLabel: 'Tool',
    stageLabel: 'executor',
    summary: '将 MCP、浏览器、构建、质量门等动作呈现为可审批节点。写操作只能经过 Worldline service/MCP 边界。',
    choiceReason: '参考本地 Agent 与 Codex 的执行闭环，但把权限、工具调用和结果证据外显。',
    nextStepTitle: '审批或拒绝工具调用',
    score: 0.87,
    quality: makeQuality(0.78, 'needs_approval'),
    toolCallIds: ['tool-plan-workflow', 'tool-run-quality-gate'],
    evidenceIds: ['ev-agent-workflow'],
    temporalFactIds: ['tf-stage1', 'tf-stage2'],
    gateResultIds: ['gate-permission', 'gate-conflict']
  },
  {
    id: 'branch-skill',
    title: '技能进化分支',
    subtitle: '成功路径沉淀为 SkillProposal',
    branchType: 'skill_proposal',
    tone: 'focus',
    choiceLabel: 'Skill',
    stageLabel: 'evolution',
    summary: '当任务路径通过质量门后，系统生成可审查的技能候选：触发条件、步骤、所需权限、评估分数和回滚方式都可见。',
    choiceReason: '把一次成功的工作流变成可复用能力，而不是散落在对话历史里。',
    nextStepTitle: '生成技能候选',
    score: 0.84,
    quality: makeQuality(0.76, 'candidate'),
    toolCallIds: ['tool-propose-skill'],
    evidenceIds: ['ev-agent-workflow', 'ev-workbench-facade'],
    temporalFactIds: ['tf-stage2'],
    gateResultIds: ['gate-skill']
  }
]

const makeBranch = (template) => ({
  ...template,
  riskLabel: template.branchType === 'tool_action' ? '需审批' : '可验证',
  costLabel: template.branchType === 'skill_proposal' ? '中等成本' : '低成本',
  confidenceLabel: `${Math.round(template.score * 100)}%`,
  routeTone: '先证明，再执行；先留痕，再复用。',
  suitability: ['Agent 工作台', '证据优先', '可回放'],
  focus: template.branchType,
  focusKey: template.id,
  candidateId: template.id,
  graphId: 'agent-worldline-preview',
  buildId: 'agent-workbench-stage1',
  graphLabel: 'Agent Worldline Graph',
  buildLabel: 'Stage 2 Ledger',
  switchHint: '如果证据覆盖不足、权限风险过高或质量门失败，应回到计划分支重新拆解。',
  evidenceRefs,
  wikiRefs,
  entityRefs,
  timelineRefs,
  nextGenerationLabel: '沿此分支继续生成',
  nextActions: [
    {
      id: `${template.id}-approve`,
      label: '批准此分支',
      description: '将此分支作为当前采纳世界线。',
      targetType: 'approve',
      emphasis: 'primary'
    },
    {
      id: `${template.id}-trace`,
      label: '查看执行轨迹',
      description: '检查该分支关联的工具调用、证据和质量门。',
      targetType: 'trace',
      emphasis: 'secondary'
    },
    {
      id: `${template.id}-reject`,
      label: '拒绝并回滚',
      description: '记录拒绝原因，并回到计划分支重新拆解。',
      targetType: 'reject',
      emphasis: 'danger'
    }
  ],
  context: {
    theme: 'agent-workbench',
    module: 'agent-workbench',
    scene: 'agent_worldline',
    entry: 'worldline-agent',
    branch: template.id,
    focus: template.branchType,
    evidence_ids: template.evidenceIds,
    tool_call_ids: template.toolCallIds,
    temporal_fact_ids: template.temporalFactIds,
    gate_result_ids: template.gateResultIds
  }
})

const buildTree = (branches) => {
  const nodes = [
    {
      id: 'root-agent-goal',
      type: 'root',
      title: '任务目标',
      subtitle: 'Agent Run',
      meta: 'WorldlineRun',
      x: 120,
      y: 330,
      radius: 11,
      branchId: ''
    }
  ]
  const edges = []

  branches.forEach((branch, index) => {
    const y = 120 + index * 145
    nodes.push({
      id: branch.id,
      type: 'branch',
      title: branch.title,
      subtitle: branch.subtitle,
      meta: `${branch.choiceLabel} / ${branch.stageLabel}`,
      x: 390,
      y,
      radius: 9,
      branchId: branch.id,
      tone: branch.tone
    })
    nodes.push({
      id: `${branch.id}-gate`,
      type: 'next-step',
      title: '质量门',
      subtitle: branch.quality.status,
      meta: `${Math.round(branch.quality.citationCoverage * 100)}% coverage`,
      x: 700,
      y,
      radius: 8,
      branchId: branch.id,
      tone: branch.tone
    })
    edges.push({
      id: `edge-root-${branch.id}`,
      source: 'root-agent-goal',
      target: branch.id,
      branchId: branch.id,
      kind: index === 0 ? 'primary' : 'secondary',
      label: branch.choiceLabel,
      isHighlighted: index === 0
    })
    edges.push({
      id: `edge-gate-${branch.id}`,
      source: branch.id,
      target: `${branch.id}-gate`,
      branchId: branch.id,
      kind: 'guide',
      label: 'gate',
      isHighlighted: index === 0
    })
  })

  nodes.push({
    id: 'convergence-skill',
    type: 'convergence',
    title: '技能候选',
    subtitle: 'SkillProposal',
    meta: 'Reusable path',
    x: 1010,
    y: 330,
    radius: 11,
    branchId: branches[0]?.id || '',
    tone: 'peak'
  })

  branches.forEach((branch, index) => {
    edges.push({
      id: `edge-converge-${branch.id}`,
      source: `${branch.id}-gate`,
      target: 'convergence-skill',
      branchId: branch.id,
      kind: 'convergence',
      label: 'skill',
      isHighlighted: index === 0
    })
  })

  return {
    width: 1160,
    height: 700,
    nodes,
    edges
  }
}

const toolTraces = [
  {
    id: 'tool-query-evidence',
    branchId: 'branch-evidence',
    name: 'worldline.query_evidence',
    status: 'ready',
    permission: 'read',
    summary: 'Read evidence anchors and attach them to the active branch.',
    result: '3 evidence anchors linked',
    artifactIds: ['artifact-evidence-dossier'],
    artifacts: [
      {
        id: 'artifact-evidence-dossier',
        label: 'Evidence dossier',
        type: 'markdown',
        path: '.ai/tasks/agent-workbench/evidence-dossier.md',
        summary: 'A compact evidence map for branch claims and source anchors.'
      }
    ],
    failureReason: ''
  },
  {
    id: 'tool-plan-workflow',
    branchId: 'branch-tool',
    name: 'worldline.plan_workflow',
    status: 'approval_required',
    permission: 'worldline_service_boundary',
    summary: 'Plan compile, wiki rebuild, graph update, and quality gate steps.',
    result: 'Pending human approval',
    artifactIds: ['artifact-workflow-plan'],
    artifacts: [
      {
        id: 'artifact-workflow-plan',
        label: 'Workflow plan',
        type: 'json',
        path: '.ai/tasks/agent-workbench/workflow-plan.json',
        summary: 'Structured plan for compile, wiki rebuild, graph update, and deterministic gates.'
      }
    ],
    failureReason: ''
  },
  {
    id: 'tool-run-quality-gate',
    branchId: 'branch-tool',
    name: 'worldline.run_quality_gate',
    status: 'approval_required',
    permission: 'worldline_service_boundary',
    summary: 'Run deterministic gate against evidence coverage, conflicts, and stale facts.',
    result: 'Pending human approval',
    artifactIds: ['artifact-quality-gate-report'],
    artifacts: [
      {
        id: 'artifact-quality-gate-report',
        label: 'Quality gate report',
        type: 'json',
        path: '.ai/tasks/agent-workbench/quality-gate-report.json',
        summary: 'Deterministic quality gate output covering evidence, permission, and temporal conflict checks.'
      }
    ],
    failureReason: ''
  },
  {
    id: 'tool-propose-skill',
    branchId: 'branch-skill',
    name: 'worldline.propose_skill',
    status: 'candidate',
    permission: 'review_required',
    summary: 'Turn the accepted run path into a versioned SkillProposal.',
    result: '1 proposal available',
    artifactIds: ['artifact-skill-genome'],
    artifacts: [
      {
        id: 'artifact-skill-genome',
        label: 'Skill genome draft',
        type: 'json',
        path: '.ai/tasks/agent-workbench/skill-genome.json',
        summary: 'Candidate skill metadata with trigger, steps, permission scope, and evaluation score.'
      }
    ],
    failureReason: ''
  }
]

const gateResults = [
  {
    id: 'gate-evidence',
    label: 'Evidence coverage',
    status: 'passed',
    value: '90%',
    summary: 'Branch claims have enough linked EvidenceAnchor coverage to continue.',
    branchId: 'branch-evidence',
    threshold: '>= 80% cited claims',
    input: '3 evidence anchors / 2 wiki refs / 3 graph entities',
    toolCallIds: ['tool-query-evidence'],
    artifactIds: ['artifact-evidence-dossier'],
    failureReason: '',
    remediation: 'Keep adding source anchors when new branch claims are introduced.'
  },
  {
    id: 'gate-permission',
    label: 'Permission risk',
    status: 'review',
    value: '2 approvals',
    summary: 'Write-like workflow actions must stay behind Worldline service boundaries and human approval.',
    branchId: 'branch-tool',
    threshold: '0 unapproved write-like actions',
    input: '2 worldline_service_boundary tool calls pending approval',
    toolCallIds: ['tool-plan-workflow', 'tool-run-quality-gate'],
    artifactIds: ['artifact-workflow-plan'],
    failureReason: 'Workflow execution is planned but still requires human approval.',
    remediation: 'Approve the branch, reject the action, or split the write step into a narrower branch.'
  },
  {
    id: 'gate-conflict',
    label: 'Temporal conflict',
    status: 'passed',
    value: '0 open',
    summary: 'No open temporal contradictions were found for the active branch facts.',
    branchId: 'branch-tool',
    threshold: '0 blocking temporal conflicts',
    input: '2 temporal facts checked against active branch evidence',
    toolCallIds: ['tool-run-quality-gate'],
    artifactIds: ['artifact-quality-gate-report'],
    failureReason: '',
    remediation: 'Re-run this gate after wiki rebuilds or graph projections change.'
  },
  {
    id: 'gate-skill',
    label: 'Skill readiness',
    status: 'candidate',
    value: '76%',
    summary: 'The accepted path is close to reusable, but still needs reviewer approval before becoming a skill.',
    branchId: 'branch-skill',
    threshold: '>= 85% evaluation score for automatic promotion',
    input: '2 candidate skills / 4 reusable workflow steps',
    toolCallIds: ['tool-propose-skill'],
    artifactIds: ['artifact-skill-genome'],
    failureReason: 'Skill score is below automatic promotion threshold.',
    remediation: 'Collect one more successful run and attach screenshot QA evidence before promotion.'
  }
]

const skillProposals = [
  {
    id: 'skill-agent-ledger-review',
    name: 'Agent Ledger Review',
    trigger: 'When a WorldlineRun has multiple branches and at least one pending tool action.',
    steps: [
      'Read branch evidence and quality gates',
      'Check tool permissions and audit scope',
      'Recommend approve, reject, or split into a new branch'
    ],
    requiredPermissions: ['worldline:read', 'worldline:audit_log:write'],
    evidenceRunIds: ['run-agent-workbench-preview'],
    sourceBranchId: 'branch-tool',
    gateResultIds: ['gate-permission', 'gate-conflict'],
    artifactIds: ['artifact-workflow-plan', 'artifact-quality-gate-report'],
    episodeIds: ['episode-tool'],
    version: '0.1.0-candidate',
    promotion: {
      status: 'review_required',
      threshold: '>= 85% eval score + 1 accepted run',
      blocker: 'Needs one more accepted tool branch replay before promotion.'
    },
    acceptanceCriteria: [
      'All write-like tools stay behind Worldline service boundaries',
      'Rejected branches keep rollback evidence',
      'Quality gate artifacts are linked to the run ledger'
    ],
    evalScore: 0.81,
    status: 'candidate'
  },
  {
    id: 'skill-worldline-screenshot-qa',
    name: 'Worldline Screenshot QA',
    trigger: 'After frontend workbench layout changes.',
    steps: [
      'Open desktop and mobile viewports',
      'Verify nonblank canvas and no overlapping controls',
      'Attach screenshots to task evidence'
    ],
    requiredPermissions: ['browser:localhost', 'artifact:write'],
    evidenceRunIds: ['run-agent-workbench-preview'],
    sourceBranchId: 'branch-skill',
    gateResultIds: ['gate-skill'],
    artifactIds: ['artifact-skill-genome'],
    episodeIds: [],
    version: '0.1.0-candidate',
    promotion: {
      status: 'needs_evidence',
      threshold: '>= 85% eval score + desktop/mobile screenshots',
      blocker: 'Attach one more mobile screenshot QA run before automatic promotion.'
    },
    acceptanceCriteria: [
      'Desktop and mobile viewports are captured',
      'Canvas is nonblank and focused target is visible',
      'Screenshot artifact paths are attached to task evidence'
    ],
    evalScore: 0.78,
    status: 'candidate'
  }
]

const episodes = [
  {
    id: 'episode-plan',
    runId: 'run-agent-workbench-preview',
    branchId: 'branch-plan',
    actor: 'planner',
    input: 'Amplify Worldline as Agent Workbench.',
    output: 'Split the goal into branches, evidence, tool actions, quality gates, and skill proposals.',
    toolCalls: [],
    diffs: [
      {
        path: 'web/src/data/worldline/agentWorkbench.js',
        status: 'preview',
        summary: 'Declared replayable AgentEpisode metadata for planning, gates, tools, artifacts, and evidence links.'
      }
    ],
    screenshots: [],
    cost: { tokens: 0, ms: 0 },
    gateResults: ['gate-evidence'],
    artifactIds: []
  },
  {
    id: 'episode-tool',
    runId: 'run-agent-workbench-preview',
    branchId: 'branch-tool',
    actor: 'executor',
    input: 'Prepare controlled action plan.',
    output: 'Tool actions require approval and remain behind Worldline service boundaries.',
    toolCalls: ['tool-plan-workflow', 'tool-run-quality-gate'],
    diffs: [
      {
        path: 'web/src/views/worldline/WorldlineAgentWorkbenchView.vue',
        status: 'pending-review',
        summary: 'Connect episode replay metadata into the inspector dossier and branch replay surface.'
      }
    ],
    screenshots: [
      {
        path: '.ai/tasks/2026-06-05-agent-episode-replay/screenshots/episode-replay-dossier.png',
        viewport: '1600x1000',
        summary: 'Episode Replay dossier showing linked tools, gates, artifacts, diffs, and QA screenshot metadata.'
      }
    ],
    cost: { tokens: 0, ms: 0 },
    gateResults: ['gate-permission'],
    artifactIds: ['artifact-workflow-plan', 'artifact-quality-gate-report']
  }
]

export const createAgentWorkbenchRun = ({
  question = '把 Worldline 升级成证据驱动的 Agent 工作台，并让每一次任务都成为可回放的世界线。',
  activeBranchId = 'branch-tool'
} = {}) => {
  const branches = branchTemplates.map(makeBranch)
  const activeBranch = branches.find((branch) => branch.id === activeBranchId) || branches[0]

  return {
    run: {
      id: 'run-agent-workbench-preview',
      title: 'Agent Workbench Stage 2',
      goal: question,
      status: 'preview',
      createdBy: 'codex',
      createdAt: nowIso(),
      budget: {
        mode: 'stage_based',
        tokenBudget: null,
        toolApprovalRequired: true
      },
      qualitySummary: {
        status: 'inspectable',
        branchCount: branches.length,
        approvalQueue: 2,
        skillProposalCount: skillProposals.length,
        artifactCount: toolTraces.reduce((count, trace) => count + (trace.artifactIds?.length || 0), 0)
      }
    },
    themeId: 'agent-workbench',
    moduleId: 'agent-workbench',
    knowledgeDbId: '',
    knowledgeMode: 'llm_wiki_primary_rag_auxiliary',
    layers: [
      'worldline_run_ledger',
      'evidence_ledger',
      'temporal_agent_memory',
      'tool_trace',
      'artifact_rail',
      'quality_gate',
      'skill_genome'
    ],
    rootQuestion: question,
    questionDraft: question,
    status: 'preview',
    sourceType: 'local-agent-workbench-stage1',
    generationMode: 'agent_workbench',
    generationRound: 1,
    branches,
    activeBranchId: activeBranch.id,
    selectedNodeId: activeBranch.id,
    tree: buildTree(branches),
    snapshots: [
      {
        id: 'run',
        label: 'Run',
        title: 'WorldlineRun',
        metric: branches.length,
        summary: 'A task enters the ledger as a replayable worldline run.'
      },
      {
        id: 'episode',
        label: 'Episode',
        title: 'AgentEpisode',
        metric: episodes.length,
        summary: 'Planner, executor, reviewer, and auditor actions are stored as episodes.'
      },
      {
        id: 'gate',
        label: 'Gate',
        title: 'QualityGate',
        metric: gateResults.length,
        summary: 'Evidence, permission, conflict, and skill readiness gates decide branch state.'
      },
      {
        id: 'skill',
        label: 'Skill',
        title: 'SkillProposal',
        metric: skillProposals.length,
        summary: 'Accepted paths can become versioned skills after review.'
      }
    ],
    quality: {
      status: 'inspectable',
      gateId: 'agent-stage1-preview',
      branchCount: branches.length,
      citationCoverage: 0.84,
      latestGate: {
        gate_id: 'agent-stage1-preview',
        status: 'preview',
        result: gateResults
      }
    },
    routeTrace: {
      facade: 'local-agent-workbench',
      protocol: AGENT_WORKBENCH_PROTOCOL,
      backend_api: '/api/worldline/runs',
      backend_available: true,
      preview_fallback: true
    },
    overview: {
      status: 'preview',
      counts: {
        worldline_runs: 1,
        branches: branches.length,
        episodes: episodes.length,
        tool_traces: toolTraces.length,
        artifacts: toolTraces.reduce((count, trace) => count + (trace.artifactIds?.length || 0), 0),
        skill_proposals: skillProposals.length
      }
    },
    viewState: {
      lastGeneratedFrom: 'local-agent-workbench',
      protocolVersion: AGENT_WORKBENCH_PROTOCOL
    },
    displayMeta: {
      stageLabel: 'AGENT WORLDLINE',
      stageTitle: '任务、工具、证据与技能的可回放世界线',
      stageSubtitle: '每条分支都显示假设、证据、工具权限、质量门和后续技能候选，后端不可用时也能预览完整交互。',
      branchCount: branches.length,
      themeName: 'Agent Workbench',
      generationLabel: '重建任务世界线',
      generationMode: 'agent_workbench',
      workspaceHint: '当前可保存到 /api/worldline/runs；未登录或后端不可用时保留本地预览。'
    },
    episodes,
    toolTraces,
    gateResults,
    skillProposals,
    contract: agentRunContract
  }
}
