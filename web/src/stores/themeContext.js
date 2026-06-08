import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

const normalizePart = (value) => (typeof value === 'string' ? value.trim() : '')

const normalizeContext = (value = {}) => {
  const theme = normalizePart(value.theme)
  if (!theme) {
    return null
  }

  const moduleId = normalizePart(value.module) || theme
  const scene = normalizePart(value.scene) || 'overview'
  const version = normalizePart(value.version) || 'worldline-context-v1'
  const focus = normalizePart(value.focus)
  const candidate = normalizePart(value.candidate)
  const graph = normalizePart(value.graph)
  const build = normalizePart(value.build)
  const branch = normalizePart(value.branch)
  const entry = normalizePart(value.entry)
  const dbId = normalizePart(value.db_id || value.dbId)
  const knowledgeDbId = normalizePart(value.knowledge_db_id || value.knowledgeDbId || dbId)

  const context = {
    theme,
    module: moduleId,
    scene,
    version
  }

  if (focus) {
    context.focus = focus
  }

  if (candidate) {
    context.candidate = candidate
  }

  if (graph) {
    context.graph = graph
  }

  if (build) {
    context.build = build
  }

  if (branch) {
    context.branch = branch
  }

  if (entry) {
    context.entry = entry
  }

  if (dbId) {
    context.db_id = dbId
  }

  if (knowledgeDbId) {
    context.knowledge_db_id = knowledgeDbId
  }

  return context
}

const toRouteQuery = (value) => {
  const context = normalizeContext(value)
  if (!context) {
    return {}
  }

  return {
    theme: context.theme,
    module: context.module,
    scene: context.scene,
    version: context.version,
    ...(context.focus ? { focus: context.focus } : {}),
    ...(context.candidate ? { candidate: context.candidate } : {}),
    ...(context.graph ? { graph: context.graph } : {}),
    ...(context.build ? { build: context.build } : {}),
    ...(context.branch ? { branch: context.branch } : {}),
    ...(context.entry ? { entry: context.entry } : {}),
    ...(context.db_id ? { db_id: context.db_id } : {}),
    ...(context.knowledge_db_id ? { knowledge_db_id: context.knowledge_db_id } : {})
  }
}

export const useThemeContextStore = defineStore('themeContext', () => {
  const activeContext = ref(null)

  const hasActiveContext = computed(() => Boolean(activeContext.value?.theme))
  const routeQuery = computed(() => toRouteQuery(activeContext.value))
  const summary = computed(() => {
    if (!activeContext.value) {
      return ''
    }

    return `${activeContext.value.theme} / ${activeContext.value.module}`
  })

  const detail = computed(() => {
    if (!activeContext.value) {
      return ''
    }

    const parts = [`scene=${activeContext.value.scene}`, `version=${activeContext.value.version}`]

    if (activeContext.value.entry) {
      parts.push(`entry=${activeContext.value.entry}`)
    }

    if (activeContext.value.candidate) {
      parts.push(`candidate=${activeContext.value.candidate}`)
    }

    if (activeContext.value.graph) {
      parts.push(`graph=${activeContext.value.graph}`)
    }

    if (activeContext.value.build) {
      parts.push(`build=${activeContext.value.build}`)
    }

    if (activeContext.value.branch) {
      parts.push(`branch=${activeContext.value.branch}`)
    }

    if (activeContext.value.focus) {
      parts.push(`focus=${activeContext.value.focus}`)
    }

    if (activeContext.value.knowledge_db_id || activeContext.value.db_id) {
      parts.push(`db=${activeContext.value.knowledge_db_id || activeContext.value.db_id}`)
    }

    return parts.join(', ')
  })

  const setThemeContext = (value) => {
    activeContext.value = normalizeContext(value)
    return activeContext.value
  }

  const syncFromRoute = (route) => {
    const query = route?.query || {}
    activeContext.value = normalizeContext(query)
    return activeContext.value
  }

  const clearThemeContext = () => {
    activeContext.value = null
  }

  return {
    activeContext,
    hasActiveContext,
    routeQuery,
    summary,
    detail,
    setThemeContext,
    syncFromRoute,
    clearThemeContext,
    toRouteQuery
  }
})
