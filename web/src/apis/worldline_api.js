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
  theme?.knowledge_db_id ||
  theme?.knowledge?.db_id ||
  theme?.context?.knowledge_db_id ||
  theme?.worldline?.knowledge_db_id ||
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

  rebuildWiki: (dbId, payload = {}) =>
    apiAdminPost(`/api/knowledge/databases/${encodeSegment(dbId)}/wiki/rebuild`, payload),

  listGraphEntities: (dbId, params = {}) =>
    apiAdminGet(`/api/knowledge/databases/${encodeSegment(dbId)}/graph/entities${queryString(params)}`),

  listGraphRelationships: (dbId, params = {}) =>
    apiAdminGet(`/api/knowledge/databases/${encodeSegment(dbId)}/graph/relationships${queryString(params)}`),

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
