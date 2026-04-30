import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { brandApi } from '@/apis/system_api'

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
      theme: context.theme || themeId,
      module: context.module || themeId,
      scene: context.scene || 'overview',
      version: context.version || 'phase2'
    }
  }
}

export const useInfoStore = defineStore('info', () => {
  const infoConfig = ref({})
  const isLoading = ref(false)
  const isLoaded = ref(false)
  const debugMode = ref(false)
  const error = ref(null)
  let pendingInfoConfigRequest = null

  const organization = computed(
    () =>
      infoConfig.value.organization || {
        name: '',
        logo: '',
        avatar: ''
      }
  )

  const branding = computed(
    () =>
      infoConfig.value.branding || {
        name: '',
        title: '',
        subtitle: '',
        description: ''
      }
  )

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
      ({ key, name }) =>
        key === 'docs' || key === 'doc' || name.includes('文档') || name.includes('docs')
    )
    return action?.url || action?.link || ''
  })

  const projectRepoUrl = computed(() => {
    const action = findAction(
      ({ key, name }) =>
        key === 'github' || name.includes('github') || name.includes('repo') || name.includes('仓库')
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
    infoConfig.value = newConfig
    isLoaded.value = true
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
          return response.data
        }

        return null
      })
      .catch((requestError) => {
        error.value = requestError
        console.error('加载信息配置时发生错误:', requestError)
        return null
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

    const config = await runInfoConfigRequest(() => brandApi.getInfoConfig())
    if (config) {
      console.debug('信息配置加载成功:', config)
      return config
    }

    console.warn('信息配置加载失败，使用默认配置')
    return null
  }

  async function reloadInfoConfig() {
    const config = await runInfoConfigRequest(() => brandApi.reloadInfoConfig())
    if (config) {
      console.debug('信息配置重新加载成功:', config)
      return config
    }

    console.warn('信息配置重新加载失败')
    return null
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
    footer,
    actions,
    themes,
    primaryTheme,
    docsUrl,
    projectRepoUrl,
    setInfoConfig,
    setDebugMode,
    toggleDebugMode,
    loadInfoConfig,
    reloadInfoConfig,
    findAction,
    getThemeById,
    resolveDocsUrl
  }
})
