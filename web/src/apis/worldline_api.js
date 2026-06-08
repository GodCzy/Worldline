import { apiAdminGet, apiAdminPost } from './base'

const encodeSegment = (value = '') => encodeURIComponent(String(value || '').trim())

const queryString = (params = {}) => {
  const query = new URLSearchParams()
  Object.entries(params || {}).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return
    query.append(key, String(value))
  })
  const value = query.toString()
  return value ? `?${value}` : ''
}

export const resolveThemeKnowledgeDbId = (theme = {}) =>
  theme?.db_id ||
  theme?.knowledge_db_id ||
  theme?.knowledge?.db_id ||
  theme?.knowledge?.knowledge_db_id ||
  theme?.context?.db_id ||
  theme?.context?.knowledge_db_id ||
  theme?.worldline?.db_id ||
  theme?.worldline?.knowledge_db_id ||
  theme?.metadata?.db_id ||
  theme?.metadata?.knowledge_db_id ||
  ''

export const hasWorldlineLiveBridge = (theme = {}) => Boolean(resolveThemeKnowledgeDbId(theme))

export const worldlineApi = {
  overview: (dbId) => apiAdminGet(`/api/knowledge/databases/${encodeSegment(dbId)}/worldline/overview`),

  generate: ({ dbId, themeId, question, mode = 'base', focusBranchId = '', context = {} } = {}) =>
    apiAdminPost(`/api/knowledge/databases/${encodeSegment(dbId)}/worldline/generate`, {
      theme_id: themeId,
      question,
      mode,
      focus_branch_id: focusBranchId || undefined,
      context
    }),

  queryEvidence: (dbId, { query, meta = {} } = {}) =>
    apiAdminPost(`/api/knowledge/databases/${encodeSegment(dbId)}/query-evidence`, {
      query,
      meta
    }),

  listEvidenceAnchors: (dbId, params = {}) =>
    apiAdminGet(`/api/knowledge/databases/${encodeSegment(dbId)}/evidence-anchors${queryString(params)}`),

  listWikiPages: (dbId, params = {}) =>
    apiAdminGet(`/api/knowledge/databases/${encodeSegment(dbId)}/wiki/pages${queryString(params)}`),

  listStaleWikiPages: (dbId) =>
    apiAdminGet(`/api/knowledge/databases/${encodeSegment(dbId)}/wiki/stale-pages`),

  rebuildWiki: (dbId, payload = {}) =>
    apiAdminPost(`/api/knowledge/databases/${encodeSegment(dbId)}/wiki/rebuild`, payload),

  listGraphEntities: (dbId, params = {}) =>
    apiAdminGet(`/api/knowledge/databases/${encodeSegment(dbId)}/graph/entities${queryString(params)}`),

  listGraphRelationships: (dbId, params = {}) =>
    apiAdminGet(`/api/knowledge/databases/${encodeSegment(dbId)}/graph/relationships${queryString(params)}`),

  listGraphConflicts: (dbId, params = {}) =>
    apiAdminGet(`/api/knowledge/databases/${encodeSegment(dbId)}/graph/conflicts${queryString(params)}`),

  getNeo4jProjection: (dbId, params = {}) =>
    apiAdminGet(`/api/knowledge/databases/${encodeSegment(dbId)}/graph/neo4j-projection${queryString(params)}`),

  rebuildGraph: (dbId, payload = {}) =>
    apiAdminPost(`/api/knowledge/databases/${encodeSegment(dbId)}/graph/rebuild`, payload),

  listTimeline: (dbId, params = {}) =>
    apiAdminGet(`/api/knowledge/databases/${encodeSegment(dbId)}/timeline${queryString(params)}`),

  getMcpManifest: (dbId) =>
    apiAdminGet(`/api/knowledge/databases/${encodeSegment(dbId)}/worldline-mcp/manifest`),

  listMcpAuditLogs: (dbId, params = {}) =>
    apiAdminGet(`/api/knowledge/databases/${encodeSegment(dbId)}/worldline-mcp/audit-logs${queryString(params)}`),

  planWorkflow: (dbId, payload = {}) =>
    apiAdminPost(`/api/knowledge/databases/${encodeSegment(dbId)}/worldline-workflows/plan`, payload),

  buildGoldenSet: (dbId, payload = {}) =>
    apiAdminPost(`/api/knowledge/databases/${encodeSegment(dbId)}/golden-set/build`, payload),

  runQualityGate: (dbId, payload = {}) =>
    apiAdminPost(`/api/knowledge/databases/${encodeSegment(dbId)}/quality-gates/run`, payload),

  getQualityGate: (dbId, gateId) =>
    apiAdminGet(`/api/knowledge/databases/${encodeSegment(dbId)}/quality-gates/${encodeSegment(gateId)}`)
}

export const worldlineRunApi = {
  createRun: (payload = {}) => apiAdminPost('/api/worldline/runs', payload),

  listRuns: (params = {}) => apiAdminGet(`/api/worldline/runs${queryString(params)}`),

  compareRuns: (params = {}) => apiAdminGet(`/api/worldline/runs/compare${queryString(params)}`),

  getRun: (runId) => apiAdminGet(`/api/worldline/runs/${encodeSegment(runId)}`),

  listRunEvents: (runId, params = {}) =>
    apiAdminGet(`/api/worldline/runs/${encodeSegment(runId)}/events${queryString(params)}`),

  listRunArtifacts: (runId, params = {}) =>
    apiAdminGet(`/api/worldline/runs/${encodeSegment(runId)}/artifacts${queryString(params)}`),

  getRunManifest: (runId, params = {}) =>
    apiAdminGet(`/api/worldline/runs/${encodeSegment(runId)}/manifest${queryString(params)}`),

  inspectRunArtifact: (runId, params = {}) =>
    apiAdminGet(`/api/worldline/runs/${encodeSegment(runId)}/artifacts/read${queryString(params)}`),

  inspectRunGates: (runId, params = {}) =>
    apiAdminGet(`/api/worldline/runs/${encodeSegment(runId)}/gates${queryString(params)}`),

  inspectRunEvidence: (runId, params = {}) =>
    apiAdminGet(`/api/worldline/runs/${encodeSegment(runId)}/evidence${queryString(params)}`),

  inspectRunKnowledge: (runId, params = {}) =>
    apiAdminGet(`/api/worldline/runs/${encodeSegment(runId)}/knowledge${queryString(params)}`),

  registerRunArtifact: (runId, payload = {}) =>
    apiAdminPost(`/api/worldline/runs/${encodeSegment(runId)}/artifacts`, payload),

  renameRun: (runId, payload = {}) =>
    apiAdminPost(`/api/worldline/runs/${encodeSegment(runId)}/rename`, payload),

  archiveRun: (runId, payload = {}) =>
    apiAdminPost(`/api/worldline/runs/${encodeSegment(runId)}/archive`, payload),

  restoreRun: (runId, payload = {}) =>
    apiAdminPost(`/api/worldline/runs/${encodeSegment(runId)}/restore`, payload),

  approveBranch: (runId, branchId, payload = {}) =>
    apiAdminPost(
      `/api/worldline/runs/${encodeSegment(runId)}/branches/${encodeSegment(branchId)}/approve`,
      payload
    ),

  rejectBranch: (runId, branchId, payload = {}) =>
    apiAdminPost(
      `/api/worldline/runs/${encodeSegment(runId)}/branches/${encodeSegment(branchId)}/reject`,
      payload
    ),

  proposeSkill: (runId, payload = {}) => apiAdminPost(`/api/worldline/runs/${encodeSegment(runId)}/skills/propose`, payload)
}
