const normalizeThemeId = (value = '') =>
  typeof value === 'string' ? value.trim().toLowerCase() : ''

const worldlineAdapters = {}

export const resolveWorldlineAdapter = (themeId = '') =>
  worldlineAdapters[normalizeThemeId(themeId)] || null

export const hasWorldlineAdapter = (themeId = '') => Boolean(resolveWorldlineAdapter(themeId))

export const listWorldlineAdapterIds = () => Object.keys(worldlineAdapters)

export const getWorldlineDefaultQuestion = (
  themeId = '',
  fallback = 'Describe the target, constraints, and evidence you want Worldline to branch from.'
) => resolveWorldlineAdapter(themeId)?.defaultQuestion || fallback

export const getWorldlineDisplayLabel = (themeId = '', value = '') => {
  const label = resolveWorldlineAdapter(themeId)?.getDisplayLabel?.(value)
  return typeof label === 'string' ? label : value || ''
}

export const getWorldlineCardTitleById = (themeId = '', cardId = '') => {
  const title = resolveWorldlineAdapter(themeId)?.getCardTitleById?.(cardId)
  return typeof title === 'string' ? title : cardId || ''
}

export const getWorldlineManifestSummary = (themeId = '', fallback = { card_count: 0 }) =>
  resolveWorldlineAdapter(themeId)?.getManifestSummary?.() || fallback

export const getWorldlineRecommendationCandidates = (themeId = '') => {
  const candidates = resolveWorldlineAdapter(themeId)?.getRecommendationCandidates?.()
  return Array.isArray(candidates) ? candidates : []
}

export const getWorldlineGraphLoops = (themeId = '') => {
  const graphLoops = resolveWorldlineAdapter(themeId)?.getGraphLoops?.()
  return Array.isArray(graphLoops) ? graphLoops : []
}

export const getWorldlineGraphLoopById = (themeId = '', graphId = '') =>
  resolveWorldlineAdapter(themeId)?.getGraphLoopById?.(graphId) || null

export const getWorldlineGraphDefaultKeyword = (themeId = '', graphLoopOrGraphId = '') =>
  resolveWorldlineAdapter(themeId)?.getGraphDefaultKeyword?.(graphLoopOrGraphId) || ''

export const getWorldlineRecommendationCandidateById = (themeId = '', candidateId = '') =>
  resolveWorldlineAdapter(themeId)?.getRecommendationCandidateById?.(candidateId) || null

export const getWorldlineThemeShowcaseMeta = (themeId = '', fallback = null) =>
  resolveWorldlineAdapter(themeId)?.getThemeShowcaseMeta?.() || fallback

export const getWorldlineThemeShowcaseCandidates = (themeId = '') => {
  const items = resolveWorldlineAdapter(themeId)?.getThemeShowcaseCandidates?.()
  return Array.isArray(items) ? items : []
}

export const getWorldlineThemeShowcaseGraphs = (themeId = '') => {
  const items = resolveWorldlineAdapter(themeId)?.getThemeShowcaseGraphs?.()
  return Array.isArray(items) ? items : []
}

export const getWorldlineAgentContextView = (themeId = '', activeContext = {}) =>
  resolveWorldlineAdapter(themeId)?.getAgentContextView?.(activeContext) || null
