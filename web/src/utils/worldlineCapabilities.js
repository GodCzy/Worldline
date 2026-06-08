export const WORLDLINE_SURFACES = [
  { key: 'wiki', label: 'Wiki' },
  { key: 'graph', label: '图谱' },
  { key: 'timeline', label: '时间线' },
  { key: 'quality_gate', label: '质量门禁' },
  { key: 'mcp', label: 'MCP' },
  { key: 'workflow', label: '工作流' }
]

export const WORLDLINE_CAPABILITY_GROUPS = [
  {
    key: 'overview',
    label: '世界线总览',
    summary: '读取当前知识库的世界线状态、资产和下一步建议。',
    alwaysOn: true,
    endpoints: [{ name: 'overview', method: 'GET', path: '/worldline/overview' }]
  },
  {
    key: 'evidence',
    label: '证据召回',
    summary: '查询证据候选和证据锚点，支撑可验证分支。',
    alwaysOn: true,
    endpoints: [
      { name: 'queryEvidence', method: 'POST', path: '/query-evidence' },
      { name: 'listEvidenceAnchors', method: 'GET', path: '/evidence-anchors' }
    ]
  },
  {
    key: 'wiki',
    label: 'LLM Wiki',
    summary: '读取、发现过期页面，并按模块上下文重建 Wiki。',
    surfaceKey: 'wiki',
    endpoints: [
      { name: 'listWikiPages', method: 'GET', path: '/wiki/pages' },
      { name: 'listStaleWikiPages', method: 'GET', path: '/wiki/stale-pages' },
      { name: 'rebuildWiki', method: 'POST', path: '/wiki/rebuild' }
    ]
  },
  {
    key: 'graph',
    label: 'Temporal Graph',
    summary: '读取实体、关系、冲突和 Neo4j 投影，必要时重建图谱。',
    surfaceKey: 'graph',
    endpoints: [
      { name: 'listGraphEntities', method: 'GET', path: '/graph/entities' },
      { name: 'listGraphRelationships', method: 'GET', path: '/graph/relationships' },
      { name: 'listGraphConflicts', method: 'GET', path: '/graph/conflicts' },
      { name: 'getNeo4jProjection', method: 'GET', path: '/graph/neo4j-projection' },
      { name: 'rebuildGraph', method: 'POST', path: '/graph/rebuild' }
    ]
  },
  {
    key: 'timeline',
    label: '时间线',
    summary: '读取 Temporal Fact，让分支按时间变化展开。',
    surfaceKey: 'timeline',
    endpoints: [{ name: 'listTimeline', method: 'GET', path: '/timeline' }]
  },
  {
    key: 'mcp',
    label: 'MCP 审计',
    summary: '暴露受控工具清单和审计日志，给外部 Agent 安全读取。',
    surfaceKey: 'mcp',
    endpoints: [
      { name: 'getMcpManifest', method: 'GET', path: '/worldline-mcp/manifest' },
      { name: 'listMcpAuditLogs', method: 'GET', path: '/worldline-mcp/audit-logs' }
    ]
  },
  {
    key: 'workflow',
    label: 'Agent 工作流',
    summary: '按模块上下文规划世界线工作流和下一步任务。',
    surfaceKey: 'workflow',
    endpoints: [{ name: 'planWorkflow', method: 'POST', path: '/worldline-workflows/plan' }]
  },
  {
    key: 'quality',
    label: '评估门禁',
    summary: '构建 Golden Set，运行引用覆盖率和一致性检查。',
    surfaceKey: 'quality_gate',
    endpoints: [
      { name: 'buildGoldenSet', method: 'POST', path: '/golden-set/build' },
      { name: 'runQualityGate', method: 'POST', path: '/quality-gates/run' },
      { name: 'getQualityGate', method: 'GET', path: '/quality-gates/{gateId}' }
    ]
  }
]

export const normalizeWorldlineSurfaces = (value = {}) => {
  const source = value?.worldline?.surfaces || value?.surfaces || value || {}
  return WORLDLINE_SURFACES.reduce((result, surface) => {
    result[surface.key] = source[surface.key] !== false
    return result
  }, {})
}

const resolvePath = (path = '', dbId = '') => {
  const prefix = dbId ? `/api/knowledge/databases/${dbId}` : '/api/knowledge/databases/{dbId}'
  return `${prefix}${path}`
}

export const buildWorldlineCapabilityContract = ({ themeId = '', dbId = '', surfaces = {} } = {}) => {
  const normalizedSurfaces = normalizeWorldlineSurfaces(surfaces)
  const hasDb = Boolean(String(dbId || '').trim())
  const groups = WORLDLINE_CAPABILITY_GROUPS.map((group) => {
    const enabled = hasDb && (group.alwaysOn || normalizedSurfaces[group.surfaceKey] !== false)
    return {
      key: group.key,
      label: group.label,
      summary: group.summary,
      enabled,
      surface_key: group.surfaceKey || '',
      endpoints: group.endpoints.map((endpoint) => ({
        ...endpoint,
        route: resolvePath(endpoint.path, dbId)
      }))
    }
  })
  const enabledGroups = groups.filter((group) => group.enabled)

  return {
    version: 'worldline-capability-map-v1',
    theme_id: themeId || '',
    db_id: dbId || '',
    status: hasDb ? 'ready' : 'needs_knowledge_db',
    enabled_surfaces: WORLDLINE_SURFACES.filter((surface) => normalizedSurfaces[surface.key]).map((surface) => surface.key),
    endpoint_count: enabledGroups.reduce((count, group) => count + group.endpoints.length, 0),
    groups,
    entry_routes: {
      workbench: themeId ? `/worldline/${themeId}` : '/worldline/{themeId}',
      database: dbId ? `/database/${dbId}` : '/database',
      graph: dbId ? `/graph?db_id=${dbId}&knowledge_db_id=${dbId}` : '/graph'
    }
  }
}

export const summarizeCapabilityContract = (contract = {}) => {
  const groups = Array.isArray(contract.groups) ? contract.groups : []
  const enabledGroups = groups.filter((group) => group.enabled)
  return {
    enabledGroups,
    enabledGroupCount: enabledGroups.length,
    totalGroupCount: groups.length,
    endpointCount: enabledGroups.reduce((count, group) => count + (group.endpoints?.length || 0), 0),
    surfaceText: (contract.enabled_surfaces || [])
      .map((key) => WORLDLINE_SURFACES.find((surface) => surface.key === key)?.label || key)
      .join(' / ')
  }
}
