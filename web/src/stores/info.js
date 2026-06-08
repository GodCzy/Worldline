import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { brandApi, themeModuleApi } from '@/apis/system_api'

export const DEFAULT_INFO_CONFIG = {
  organization: {
    name: 'Worldline',
    logo: '/favicon.svg',
    avatar: '/avatar.jpg'
  },
  branding: {
    name: 'Worldline',
    title: 'Worldline',
    subtitle: 'Evidence-backed LLM Wiki + Temporal Knowledge Graph OS',
    description:
      '把文档、证据、Wiki、图谱、时间事实、MCP 工具和质量门禁编译成一个可验证的知识工作台。'
  },
  features: [
    {
      label: 'Knowledge Compiler',
      value: 'Docs + Evidence',
      description: '解析文档并保留证据锚点，让每个结论都能回到来源。',
      icon: 'docs'
    },
    {
      label: 'LLM Wiki First',
      value: 'Wiki + Graph',
      description: '以结构化 Wiki 与 Temporal Evidence Graph 为主线，RAG 只做辅助召回。',
      icon: 'route'
    },
    {
      label: 'Governed Agents',
      value: 'MCP + Audit',
      description: '通过受控 MCP、权限边界和质量门禁把 Agent 操作纳入审计。',
      icon: 'shield'
    }
  ],
  themes: [],
  actions: [
    {
      name: 'Docs',
      icon: 'docs',
      url: 'http://localhost:5174/'
    },
    {
      name: 'Repository',
      icon: 'github',
      url: 'https://github.com/GodCzy/Worldline'
    }
  ],
  footer: {
    copyright: 'Worldline 2026'
  }
}

const normalizeActionText = (value) => (typeof value === 'string' ? value.trim().toLowerCase() : '')

const normalizeTheme = (item) => {
  const themeId = typeof item?.id === 'string' ? item.id.trim() : ''
  if (!themeId) {
    return null
  }

  const context = item?.context || {}
  return {
    ...item,
    id: themeId,
    name: item?.name || item?.title || themeId,
    subtitle: item?.subtitle || '',
    description: item?.description || '',
    status: item?.status || '',
    featured: Boolean(item?.featured),
    entry_route: item?.entry_route || `/themes/${themeId}`,
    tags: Array.isArray(item?.tags) ? item.tags : [],
    highlights: Array.isArray(item?.highlights) ? item.highlights : [],
    links: item?.links || {},
    entry_points: Array.isArray(item?.entry_points) ? item.entry_points : [],
    context: {
      ...context,
      theme: context.theme || themeId,
      module: context.module || themeId,
      scene: context.scene || 'overview',
      version: context.version || 'worldline-context-v1'
    }
  }
}

const mergeInfoConfig = (value = {}) => ({
  ...DEFAULT_INFO_CONFIG,
  ...value,
  organization: {
    ...DEFAULT_INFO_CONFIG.organization,
    ...(value.organization || {})
  },
  branding: {
    ...DEFAULT_INFO_CONFIG.branding,
    ...(value.branding || {})
  },
  features: Array.isArray(value.features) ? value.features : DEFAULT_INFO_CONFIG.features,
  themes: Array.isArray(value.themes) ? value.themes : DEFAULT_INFO_CONFIG.themes,
  actions: Array.isArray(value.actions) ? value.actions : DEFAULT_INFO_CONFIG.actions,
  footer: {
    ...DEFAULT_INFO_CONFIG.footer,
    ...(value.footer || {})
  }
})

export const useInfoStore = defineStore('info', () => {
  const infoConfig = ref(mergeInfoConfig())
  const isLoading = ref(false)
  const isLoaded = ref(false)
  const debugMode = ref(false)
  const error = ref(null)
  let pendingInfoConfigRequest = null

  const organization = computed(() => infoConfig.value.organization || DEFAULT_INFO_CONFIG.organization)
  const branding = computed(() => infoConfig.value.branding || DEFAULT_INFO_CONFIG.branding)
  const features = computed(() => infoConfig.value.features || [])
  const actions = computed(() => infoConfig.value.actions || [])

  const themes = computed(() => {
    const themeList = Array.isArray(infoConfig.value.themes) ? infoConfig.value.themes : []
    return themeList.map(normalizeTheme).filter(Boolean)
  })

  const primaryTheme = computed(() => themes.value.find((item) => item.featured) || themes.value[0] || null)

  const footer = computed(() => ({
    copyright: '',
    user_agreement_url: '',
    privacy_policy_url: '',
    ...(infoConfig.value.footer || {})
  }))

  function findAction(matcher) {
    const actionList = Array.isArray(infoConfig.value.actions) ? infoConfig.value.actions : []
    return (
      actionList.find((item) => {
        const key = normalizeActionText(item?.icon || item?.type)
        const name = normalizeActionText(item?.name || item?.label)
        return matcher({ item, key, name })
      }) || null
    )
  }

  const docsUrl = computed(() => {
    const action = findAction(
      ({ key, name }) => key === 'docs' || key === 'doc' || name.includes('document') || name.includes('docs')
    )
    return action?.url || action?.link || ''
  })

  const projectRepoUrl = computed(() => {
    const action = findAction(
      ({ key, name }) => key === 'github' || name.includes('github') || name.includes('repo')
    )
    return action?.url || action?.link || ''
  })

  function resolveDocsUrl(path = '') {
    const baseUrl = docsUrl.value
    const normalizedPath = typeof path === 'string' ? path.trim() : ''

    if (!normalizedPath) {
      return baseUrl || ''
    }

    if (!baseUrl) {
      return ''
    }

    const relativePath = normalizedPath.replace(/^\/+/, '')
    return new URL(relativePath, baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`).toString()
  }

  function setInfoConfig(newConfig) {
    infoConfig.value = mergeInfoConfig(newConfig || {})
    isLoaded.value = true
  }

  function useFallbackConfig(requestError = null) {
    if (requestError) {
      error.value = requestError
    }
    setInfoConfig(DEFAULT_INFO_CONFIG)
    return infoConfig.value
  }

  function setDebugMode(enabled) {
    debugMode.value = enabled
  }

  function toggleDebugMode() {
    debugMode.value = !debugMode.value
  }

  async function runInfoConfigRequest(requestFactory) {
    if (pendingInfoConfigRequest) {
      return pendingInfoConfigRequest
    }

    isLoading.value = true
    error.value = null

    pendingInfoConfigRequest = requestFactory()
      .then((response) => {
        if (response.success && response.data) {
          setInfoConfig(response.data)
          return infoConfig.value
        }

        return useFallbackConfig(new Error('System info response did not include a usable config.'))
      })
      .catch((requestError) => {
        console.warn('System info config is unavailable, using local fallback.', requestError)
        return useFallbackConfig(requestError)
      })
      .finally(() => {
        pendingInfoConfigRequest = null
        isLoading.value = false
      })

    return pendingInfoConfigRequest
  }

  async function loadInfoConfig(force = false) {
    if (isLoaded.value && !force) {
      return infoConfig.value
    }

    return runInfoConfigRequest(() => brandApi.getInfoConfig())
  }

  async function reloadInfoConfig() {
    return runInfoConfigRequest(() => brandApi.reloadInfoConfig())
  }

  async function loadThemeModules() {
    const response = await themeModuleApi.list()
    return Array.isArray(response?.themes) ? response.themes : []
  }

  async function createThemeModule(payload) {
    const response = await themeModuleApi.create(payload)
    await loadInfoConfig(true)
    return response?.theme || null
  }

  async function updateThemeModule(themeId, payload) {
    const response = await themeModuleApi.update(themeId, payload)
    await loadInfoConfig(true)
    return response?.theme || null
  }

  async function deleteThemeModule(themeId) {
    const response = await themeModuleApi.remove(themeId)
    await loadInfoConfig(true)
    return response
  }

  function getThemeById(themeId) {
    return themes.value.find((item) => item.id === themeId) || null
  }

  return {
    infoConfig,
    isLoading,
    isLoaded,
    debugMode,
    error,
    organization,
    branding,
    features,
    themes,
    primaryTheme,
    actions,
    docsUrl,
    projectRepoUrl,
    footer,
    loadInfoConfig,
    reloadInfoConfig,
    loadThemeModules,
    createThemeModule,
    updateThemeModule,
    deleteThemeModule,
    setInfoConfig,
    useFallbackConfig,
    setDebugMode,
    toggleDebugMode,
    resolveDocsUrl,
    getThemeById
  }
})
