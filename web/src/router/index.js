import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import BlankLayout from '@/layouts/BlankLayout.vue'
import { useUserStore } from '@/stores/user'
import { useAgentStore } from '@/stores/agent'

const AUTH_REDIRECT_KEY = 'redirect'

export const normalizeAuthRedirect = (redirectPath) => {
  if (typeof redirectPath !== 'string') {
    return ''
  }

  const normalizedPath = redirectPath.trim()
  if (!normalizedPath || normalizedPath === '/login') {
    return ''
  }

  return normalizedPath
}

export const getStoredRedirect = () => {
  return normalizeAuthRedirect(sessionStorage.getItem(AUTH_REDIRECT_KEY))
}

export const setStoredRedirect = (redirectPath) => {
  const normalizedPath = normalizeAuthRedirect(redirectPath)
  if (normalizedPath) {
    sessionStorage.setItem(AUTH_REDIRECT_KEY, normalizedPath)
  } else {
    sessionStorage.removeItem(AUTH_REDIRECT_KEY)
  }
}

export const consumeStoredRedirect = () => {
  const redirectPath = getStoredRedirect()
  sessionStorage.removeItem(AUTH_REDIRECT_KEY)
  return redirectPath
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'main',
      component: BlankLayout,
      children: [
        {
          path: '',
          name: 'Home',
          component: () => import('../views/HomeView.vue'),
          meta: { keepAlive: true, requiresAuth: false }
        }
      ]
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/themes',
      name: 'themes',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'ThemeHub',
          component: () => import('../views/themes/ThemeHubView.vue'),
          meta: { keepAlive: true, requiresAuth: false }
        },
        {
          path: ':themeId',
          name: 'ThemeDetail',
          component: () => import('../views/themes/ThemeDetailView.vue'),
          meta: {
            keepAlive: true,
            requiresAuth: false,
            themeContext: {
              scene: 'overview',
              version: 'worldline-context-v1'
            }
          }
        },
        {
          path: ':themeId/worldline',
          redirect: (to) => `/worldline/${String(to.params.themeId || '').trim()}`.replace(/\/$/, '')
        }
      ]
    },
    {
      path: '/worldline',
      name: 'worldline',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'WorldlineHub',
          component: () => import('../views/worldline/WorldlineHubView.vue'),
          meta: { keepAlive: true, requiresAuth: false }
        },
        {
          path: ':themeId',
          name: 'WorldlineWorkbench',
          component: () => import('../views/worldline/WorldlineWorkbenchView.vue'),
          meta: {
            keepAlive: false,
            requiresAuth: false,
            themeContext: {
              scene: 'worldline',
              version: 'v1.2',
              entry: 'worldline'
            }
          }
        }
      ]
    },
    {
      path: '/agent',
      name: 'AgentMain',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'AgentComp',
          component: () => import('../views/AgentView.vue'),
          meta: { keepAlive: true, requiresAuth: true }
        },
        {
          path: ':agent_id',
          name: 'AgentCompWithId',
          component: () => import('../views/AgentView.vue'),
          meta: { keepAlive: true, requiresAuth: true }
        }
      ]
    },
    {
      path: '/graph',
      name: 'graph',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'GraphComp',
          component: () => import('../views/GraphView.vue'),
          meta: { keepAlive: false, requiresAuth: true, requiresAdmin: true }
        }
      ]
    },
    {
      path: '/database',
      name: 'database',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'DatabaseComp',
          component: () => import('../views/DataBaseView.vue'),
          meta: { keepAlive: true, requiresAuth: true, requiresAdmin: true }
        },
        {
          path: ':database_id',
          name: 'DatabaseInfoComp',
          component: () => import('../views/DataBaseInfoView.vue'),
          meta: { keepAlive: false, requiresAuth: true, requiresAdmin: true }
        }
      ]
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'DashboardComp',
          component: () => import('../views/DashboardView.vue'),
          meta: { keepAlive: false, requiresAuth: true, requiresAdmin: true }
        }
      ]
    },
    {
      path: '/extensions',
      name: 'extensions',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'ExtensionsComp',
          component: () => import('../views/ExtensionsView.vue'),
          meta: {
            keepAlive: false,
            requiresAuth: true,
            requiresAdmin: true,
            requiresSuperAdmin: true
          }
        }
      ]
    },
    {
      path: '/skills',
      name: 'skills',
      redirect: '/extensions'
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/EmptyView.vue'),
      meta: { requiresAuth: false }
    }
  ]
})

const resolveFallbackAgentId = async () => {
  const agentStore = useAgentStore()
  if (!agentStore.isInitialized) {
    await agentStore.initialize()
  }

  return agentStore.selectedAgentId || agentStore.defaultAgent?.id || agentStore.agents[0]?.id || ''
}

router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth === true)
  const requiresAdmin = to.matched.some((record) => record.meta.requiresAdmin)
  const requiresSuperAdmin = to.matched.some((record) => record.meta.requiresSuperAdmin)

  const userStore = useUserStore()

  if (userStore.token && !userStore.userId) {
    try {
      await userStore.getCurrentUser()
    } catch (error) {
      console.error('获取用户信息失败:', error)
      userStore.logout()
    }
  }

  const isLoggedIn = userStore.isLoggedIn
  const isAdmin = userStore.isAdmin
  const isSuperAdmin = userStore.isSuperAdmin

  if (to.name === 'AgentComp' && isLoggedIn) {
    try {
      const fallbackAgentId = await resolveFallbackAgentId()
      if (fallbackAgentId) {
        next({
          name: 'AgentCompWithId',
          params: { agent_id: fallbackAgentId },
          query: to.query
        })
        return
      }
    } catch (error) {
      console.error('初始化默认智能体失败:', error)
    }
  }

  if (requiresAuth && !isLoggedIn) {
    const redirectPath = normalizeAuthRedirect(to.fullPath)
    setStoredRedirect(redirectPath)
    next({
      name: 'login',
      query: redirectPath ? { redirect: redirectPath } : undefined
    })
    return
  }

  if (requiresAdmin && !isAdmin) {
    try {
      const fallbackAgentId = await resolveFallbackAgentId()
      if (fallbackAgentId) {
        next(`/agent/${fallbackAgentId}`)
      } else {
        next('/agent')
      }
    } catch (error) {
      console.error('获取智能体信息失败:', error)
      next('/agent')
    }
    return
  }

  if (requiresSuperAdmin && !isSuperAdmin) {
    try {
      const fallbackAgentId = await resolveFallbackAgentId()
      if (fallbackAgentId) {
        next(`/agent/${fallbackAgentId}`)
      } else {
        next('/agent')
      }
    } catch (error) {
      console.error('获取智能体信息失败:', error)
      next('/agent')
    }
    return
  }

  if (to.path === '/login' && isLoggedIn) {
    const redirectPath =
      normalizeAuthRedirect(to.query.redirect) || consumeStoredRedirect()
    if (redirectPath) {
      next(redirectPath)
      return
    }

    next('/')
    return
  }

  next()
})

export default router
