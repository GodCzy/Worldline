import { poeWorldlineAdapter } from '@/data/worldline/poeWorldlineAdapter'
import { worldlineOpsAdapter } from '@/data/worldline/worldlineOpsAdapter'
import { worldlineSandboxAdapter } from '@/data/worldline/worldlineSandboxAdapter'

const worldlineAdapters = {
  [poeWorldlineAdapter.id]: poeWorldlineAdapter,
  [worldlineOpsAdapter.id]: worldlineOpsAdapter,
  [worldlineSandboxAdapter.id]: worldlineSandboxAdapter
}

const normalizeThemeId = (value = '') =>
  typeof value === 'string' ? value.trim().toLowerCase() : ''

const getRegisteredAdapters = () => Object.values(worldlineAdapters)

const resolveViewAdapter = (themeId = '') => {
  const normalizedThemeId = normalizeThemeId(themeId)
  if (normalizedThemeId) {
    return worldlineAdapters[normalizedThemeId] || null
  }

  return getRegisteredAdapters()[0] || null
}

const callAdapterMethod = (themeId = '', methodName = '', ...args) => {
  const adapter = resolveViewAdapter(themeId)
  const method = adapter?.[methodName]
  if (typeof method !== 'function') {
    return null
  }

  return method(...args)
}

export const resolveWorldlineAdapter = (themeId = '') =>
  worldlineAdapters[normalizeThemeId(themeId)] || null

export const hasWorldlineAdapter = (themeId = '') => Boolean(resolveWorldlineAdapter(themeId))

export const listWorldlineAdapterIds = () => Object.keys(worldlineAdapters)

export const getWorldlineDefaultQuestion = (
  themeId = '',
  fallback = '请描述你的目标、偏好和限制，让世界线先展开几条未来分支。'
) => resolveViewAdapter(themeId)?.defaultQuestion || fallback

export const getWorldlineDisplayLabel = (themeId = '', value = '') => {
  const label = callAdapterMethod(themeId, 'getDisplayLabel', value)
  return typeof label === 'string' ? label : value || ''
}

export const getWorldlineCardTitleById = (themeId = '', cardId = '') => {
  const title = callAdapterMethod(themeId, 'getCardTitleById', cardId)
  return typeof title === 'string' ? title : cardId || ''
}

export const getWorldlineManifestSummary = (themeId = '', fallback = { card_count: 0 }) => {
  const summary = callAdapterMethod(themeId, 'getManifestSummary')
  return summary && typeof summary === 'object' ? summary : fallback
}

export const getWorldlineRecommendationCandidates = (themeId = '') => {
  const candidates = callAdapterMethod(themeId, 'getRecommendationCandidates')
  return Array.isArray(candidates) ? candidates : []
}

export const getWorldlineGraphLoops = (themeId = '') => {
  const graphLoops = callAdapterMethod(themeId, 'getGraphLoops')
  return Array.isArray(graphLoops) ? graphLoops : []
}

export const getWorldlineGraphLoopById = (themeId = '', graphId = '') =>
  callAdapterMethod(themeId, 'getGraphLoopById', graphId) || null

export const getWorldlineGraphDefaultKeyword = (themeId = '', graphLoopOrGraphId = '') =>
  callAdapterMethod(themeId, 'getGraphDefaultKeyword', graphLoopOrGraphId) || ''

export const getWorldlineRecommendationCandidateById = (themeId = '', candidateId = '') =>
  callAdapterMethod(themeId, 'getRecommendationCandidateById', candidateId) || null

export const getWorldlineThemeShowcaseMeta = (themeId = '', fallback = null) =>
  callAdapterMethod(themeId, 'getThemeShowcaseMeta') || fallback

export const getWorldlineThemeShowcaseCandidates = (themeId = '') => {
  const items = callAdapterMethod(themeId, 'getThemeShowcaseCandidates')
  return Array.isArray(items) ? items : []
}

export const getWorldlineThemeShowcaseGraphs = (themeId = '') => {
  const items = callAdapterMethod(themeId, 'getThemeShowcaseGraphs')
  return Array.isArray(items) ? items : []
}

export const getWorldlineAgentContextView = (themeId = '', activeContext = {}) =>
  callAdapterMethod(themeId, 'getAgentContextView', activeContext) || null
