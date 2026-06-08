<script setup>
import { computed, onMounted, provide, reactive, ref } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { GithubOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import {
  AlertTriangle,
  BarChart3,
  Blocks,
  Bot,
  ChevronsLeft,
  ChevronsRight,
  CircleCheck,
  House,
  LayoutGrid,
  LibraryBig,
  LockKeyhole,
  Waypoints
} from 'lucide-vue-next'
import { storeToRefs } from 'pinia'

import { useConfigStore } from '@/stores/config'
import { useDatabaseStore } from '@/stores/database'
import { useInfoStore } from '@/stores/info'
import { useTaskerStore } from '@/stores/tasker'
import { useUserStore } from '@/stores/user'
import DebugComponent from '@/components/DebugComponent.vue'
import SettingsModal from '@/components/SettingsModal.vue'
import TaskCenterDrawer from '@/components/TaskCenterDrawer.vue'
import UserInfoComponent from '@/components/UserInfoComponent.vue'

const configStore = useConfigStore()
const databaseStore = useDatabaseStore()
const infoStore = useInfoStore()
const taskerStore = useTaskerStore()
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const { activeCount: activeCountRef, isDrawerOpen } = storeToRefs(taskerStore)

const layoutSettings = reactive({
  showDebug: false,
  useTopBar: false
})

const githubStars = ref(0)
const isLoadingStars = ref(false)
const showDebugModal = ref(false)
const showSettingsModal = ref(false)

const openSettingsModal = () => {
  showSettingsModal.value = true
}

const handleDebugModalClose = () => {
  showDebugModal.value = false
}

const getRemoteConfig = async () => {
  if (!userStore.isAdmin) return
  try {
    await configStore.refreshConfig()
  } catch (error) {
    console.warn('Load config failed:', error)
  }
}

const getRemoteDatabase = async () => {
  if (!userStore.isLoggedIn) return
  try {
    await databaseStore.loadDatabases()
  } catch (error) {
    console.warn('Load databases failed:', error)
  }
}

const projectRepoUrl = computed(() => infoStore.projectRepoUrl || '')

const extractGithubRepoPath = (repoUrl) => {
  if (!repoUrl) return ''

  try {
    const parsed = new URL(repoUrl)
    if (parsed.hostname !== 'github.com') return ''

    const segments = parsed.pathname.split('/').filter(Boolean)
    if (segments.length < 2) return ''

    return `${segments[0]}/${segments[1].replace(/\.git$/, '')}`
  } catch (error) {
    console.warn('Cannot parse repository url:', error)
    return ''
  }
}

const fetchGithubStars = async (repoUrl) => {
  const repoPath = extractGithubRepoPath(repoUrl)
  if (!repoPath) {
    githubStars.value = 0
    return
  }

  try {
    isLoadingStars.value = true
    const response = await fetch(`https://api.github.com/repos/${repoPath}`)
    if (!response.ok) throw new Error(`GitHub API ${response.status}`)
    const data = await response.json()
    githubStars.value = data.stargazers_count
  } catch (error) {
    console.warn('Load GitHub stars failed:', error)
  } finally {
    isLoadingStars.value = false
  }
}

onMounted(async () => {
  await infoStore.loadInfoConfig()
  await getRemoteDatabase()

  if (userStore.isAdmin) {
    await getRemoteConfig()
    taskerStore.loadTasks()
    if (projectRepoUrl.value) {
      fetchGithubStars(projectRepoUrl.value)
    }
  }
})

const isEmbed = computed(() => route.query.embed === '1')
const NAV_EXPANDED_STORAGE_KEY = 'worldline_app_nav_expanded'
const isNavExpanded = ref(localStorage.getItem(NAV_EXPANDED_STORAGE_KEY) === '1')
const showNavLabel = computed(() => !layoutSettings.useTopBar && isNavExpanded.value)
const activeTaskCount = computed(() => activeCountRef.value || 0)

const toggleNavExpanded = () => {
  isNavExpanded.value = !isNavExpanded.value
  localStorage.setItem(NAV_EXPANDED_STORAGE_KEY, isNavExpanded.value ? '1' : '0')
}

const isNavItemActive = (path) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

const ACCESS_LABELS = {
  login: '登录后可用',
  admin: '管理员权限',
  superadmin: '最高权限'
}

const runtimeStatus = computed(() => {
  if (infoStore.error) {
    return {
      state: 'fallback',
      label: '本地配置',
      title: '后端暂不可用，当前使用本地配置渲染页面',
      icon: AlertTriangle
    }
  }

  return {
    state: 'ready',
    label: '后端在线',
    title: '后端配置已连接',
    icon: CircleCheck
  }
})

const isNavItemLocked = (item = {}) => {
  if (item.access === 'login') return !userStore.isLoggedIn
  if (item.access === 'admin') return !userStore.isAdmin
  if (item.access === 'superadmin') return !userStore.isSuperAdmin
  return false
}

const navItemTitle = (item = {}) => {
  const accessLabel = ACCESS_LABELS[item.access]
  if (!isNavItemLocked(item) || !accessLabel) return item.name
  return `${item.name} · ${accessLabel}`
}

const handleLockedNavItem = async (item = {}) => {
  if (!item.path) return

  if (!userStore.isLoggedIn) {
    await router.push({
      name: 'Home',
      query: {
        login: '1',
        redirect: item.path
      }
    })
    return
  }

  if (item.access === 'superadmin') {
    message.info(`${item.name}需要最高权限账号`)
    return
  }

  message.info(`${item.name}需要管理员权限`)
}

const mainList = computed(() => {
  const items = [
    {
      name: '首页',
      path: '/',
      icon: House,
      activeIcon: House,
      access: 'public'
    },
    {
      name: '主题分区',
      path: '/themes',
      icon: LayoutGrid,
      activeIcon: LayoutGrid,
      access: 'public'
    },
    {
      name: '世界线',
      path: '/worldline',
      icon: Waypoints,
      activeIcon: Waypoints,
      access: 'public'
    },
    {
      name: 'Agent',
      path: '/agent',
      icon: Bot,
      activeIcon: Bot,
      access: 'login'
    }
  ]

  items.push(
    {
      name: '知识图谱',
      path: '/graph',
      icon: Waypoints,
      activeIcon: Waypoints,
      access: 'admin'
    },
    {
      name: '知识库',
      path: '/database',
      icon: LibraryBig,
      activeIcon: LibraryBig,
      access: 'admin'
    },
    {
      name: '扩展管理',
      path: '/extensions',
      icon: Blocks,
      activeIcon: Blocks,
      access: 'superadmin'
    },
    {
      name: '运营看板',
      path: '/dashboard',
      icon: BarChart3,
      activeIcon: BarChart3,
      access: 'admin'
    }
  )

  return items
})

provide('settingsModal', {
  openSettingsModal
})
</script>

<template>
  <div class="app-layout" :class="{ 'use-top-bar': layoutSettings.useTopBar, 'embed-mode': isEmbed }">
    <aside v-if="!isEmbed" class="header" :class="{ 'top-bar': layoutSettings.useTopBar, 'is-expanded': showNavLabel }">
      <div class="logo">
        <router-link to="/" aria-label="Worldline Home">
          <img v-if="infoStore.organization.avatar" :src="infoStore.organization.avatar" alt="Worldline" />
          <Waypoints v-else class="logo-fallback-icon" size="22" aria-hidden="true" />
        </router-link>
      </div>

      <div class="runtime-status" :class="runtimeStatus.state">
        <a-tooltip :disabled="showNavLabel" placement="right">
          <template #title>{{ runtimeStatus.title }}</template>
          <div class="runtime-status-inner" :title="runtimeStatus.title">
            <component :is="runtimeStatus.icon" size="15" />
            <span v-if="showNavLabel">{{ runtimeStatus.label }}</span>
          </div>
        </a-tooltip>
      </div>

      <nav class="nav" aria-label="Application">
        <button
          v-if="!layoutSettings.useTopBar"
          class="nav-item nav-expand-toggle"
          type="button"
          :title="showNavLabel ? '收起导航' : '展开导航'"
          @click="toggleNavExpanded()"
        >
          <div class="nav-item-inner">
            <component :is="showNavLabel ? ChevronsLeft : ChevronsRight" class="icon" size="20" />
            <span v-if="showNavLabel" class="nav-label">{{ showNavLabel ? '收起导航' : '展开导航' }}</span>
          </div>
        </button>

        <template v-for="item in mainList" :key="item.path">
          <RouterLink
            v-if="!isNavItemLocked(item)"
            :to="item.path"
            class="nav-item"
            active-class="active"
          >
            <a-tooltip :disabled="showNavLabel" placement="right">
              <template #title>{{ navItemTitle(item) }}</template>
              <div class="nav-item-inner">
                <component class="icon" :is="isNavItemActive(item.path) ? item.activeIcon : item.icon" size="22" />
                <span v-if="showNavLabel" class="nav-label">{{ item.name }}</span>
              </div>
            </a-tooltip>
          </RouterLink>

          <button
            v-else
            class="nav-item locked"
            type="button"
            :aria-label="navItemTitle(item)"
            @click="handleLockedNavItem(item)"
          >
            <a-tooltip :disabled="showNavLabel" placement="right">
              <template #title>{{ navItemTitle(item) }}</template>
              <div class="nav-item-inner">
                <component class="icon" :is="item.icon" size="22" />
                <span v-if="showNavLabel" class="nav-label">{{ item.name }}</span>
                <LockKeyhole class="lock-icon" size="12" />
              </div>
            </a-tooltip>
          </button>
        </template>

        <button
          v-if="userStore.isAdmin"
          class="nav-item task-center"
          :class="{ active: isDrawerOpen }"
          type="button"
          @click="taskerStore.openDrawer()"
        >
          <a-tooltip :disabled="showNavLabel" placement="right">
            <template #title>任务中心</template>
            <div class="nav-item-inner">
              <a-badge :count="activeTaskCount" :overflow-count="99" class="task-center-badge" size="small">
                <CircleCheck class="icon" size="22" />
              </a-badge>
              <span v-if="showNavLabel" class="nav-label">任务中心</span>
            </div>
          </a-tooltip>
        </button>
      </nav>

      <div class="fill"></div>

      <div v-if="projectRepoUrl" class="github nav-item">
        <a-tooltip placement="right">
          <template #title>项目仓库</template>
          <a :href="projectRepoUrl" target="_blank" rel="noopener noreferrer" class="github-link">
            <GithubOutlined class="icon" />
            <span v-if="githubStars > 0 && !isLoadingStars" class="github-stars">
              <span class="star-count">{{ (githubStars / 1000).toFixed(1) }}k</span>
            </span>
          </a>
        </a-tooltip>
      </div>

      <div class="nav-item user-info">
        <UserInfoComponent />
      </div>
    </aside>

    <router-view v-slot="{ Component, route }" id="app-router-view">
      <keep-alive v-if="route.meta.keepAlive !== false">
        <component :is="Component" />
      </keep-alive>
      <component :is="Component" v-else />
    </router-view>

    <a-modal
      v-model:open="showDebugModal"
      title="调试面板"
      width="90%"
      :footer="null"
      :mask-closable="true"
      :destroy-on-close="true"
      class="debug-modal"
      @cancel="handleDebugModalClose"
    >
      <DebugComponent />
    </a-modal>
    <TaskCenterDrawer v-if="userStore.isAdmin" />
    <SettingsModal v-model:visible="showSettingsModal" @close="() => (showSettingsModal = false)" />
  </div>
</template>

<style lang="less" scoped>
@header-width-collapsed: 56px;
@header-width-expanded: 188px;

.app-layout {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 100vh;
  min-width: var(--min-width);
  background: var(--wl-bg-0);
  color: var(--wl-text);
}

.app-layout.embed-mode {
  flex-direction: column;
  min-width: 0;
}

.app-layout.embed-mode #app-router-view {
  height: 100vh;
}

.header,
#app-router-view {
  height: 100%;
  max-width: 100%;
  user-select: none;
}

#app-router-view {
  flex: 1 1 auto;
  min-width: 0;
  overflow-y: auto;
  background: var(--wl-bg-0);
}

.header {
  display: flex;
  flex-direction: column;
  flex: 0 0 @header-width-collapsed;
  align-items: center;
  background:
    radial-gradient(circle at 50% 0%, rgba(var(--wl-gold-rgb), 0.12), transparent 32%),
    linear-gradient(180deg, rgba(7, 15, 24, 0.96), rgba(2, 5, 10, 0.98));
  width: @header-width-collapsed;
  border-right: 1px solid var(--wl-border);
  box-shadow: 8px 0 36px rgba(0, 0, 0, 0.28);
  overflow: hidden;
  transition:
    width 0.2s ease,
    flex-basis 0.2s ease;
}

.nav {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 10px;
  width: 100%;
  padding: 0 8px;
}

.fill {
  flex-grow: 1;
}

.logo {
  width: 38px;
  height: 38px;
  margin: 8px 0 18px;
}

.logo img {
  width: 100%;
  height: 100%;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  object-fit: cover;
  box-shadow: 0 0 18px rgba(var(--wl-cyan-rgb), 0.16);
}

.logo a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: var(--wl-cyan);
  text-decoration: none;
}

.runtime-status {
  width: calc(100% - 16px);
  margin: -8px 8px 12px;
}

.runtime-status-inner {
  min-height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.045);
  color: var(--wl-muted);
  font-size: 12px;
  font-weight: 800;
}

.runtime-status.ready .runtime-status-inner {
  color: var(--wl-cyan-soft);
}

.runtime-status.fallback .runtime-status-inner {
  border-color: rgba(var(--wl-gold-rgb), 0.28);
  background: rgba(var(--wl-gold-rgb), 0.08);
  color: var(--wl-gold-soft);
}

.nav-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 40px;
  padding: 0 10px;
  border: 1px solid transparent;
  border-radius: var(--wl-radius-sm);
  background-color: transparent;
  color: var(--wl-muted);
  font-size: 14px;
  text-decoration: none;
  cursor: pointer;
  outline: none;
  gap: 10px;
  appearance: none;
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease,
    box-shadow 0.2s ease;
}

.nav-item-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  min-width: 0;
}

.icon {
  flex: 0 0 auto;
}

.nav-label {
  display: none;
  align-items: center;
  overflow: hidden;
  color: inherit;
  font-size: 13px;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-item.active {
  border-color: var(--wl-border-strong);
  background:
    linear-gradient(90deg, rgba(var(--wl-gold-rgb), 0.14), transparent 34%),
    rgba(var(--wl-cyan-rgb), 0.1);
  color: var(--wl-text);
  box-shadow: inset 2px 0 0 var(--wl-gold);
}

.nav-item:hover {
  border-color: var(--wl-border-strong);
  background: rgba(var(--wl-cyan-rgb), 0.065);
  color: var(--wl-cyan-soft);
}

.nav-item.locked {
  border-color: rgba(var(--wl-cyan-rgb), 0.08);
  color: rgba(148, 172, 184, 0.72);
}

.nav-item.locked:hover {
  border-color: rgba(var(--wl-gold-rgb), 0.35);
  background: rgba(var(--wl-gold-rgb), 0.06);
  color: var(--wl-gold-soft);
}

.lock-icon {
  margin-left: auto;
  color: var(--wl-gold-soft);
  opacity: 0.9;
}

.nav-expand-toggle {
  margin-bottom: 4px;
  border-color: var(--wl-border);
  border-style: dashed;
}

.task-center-badge {
  display: flex;
  justify-content: center;
}

.github.nav-item {
  margin-bottom: 12px;
}

.github-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  color: inherit;
}

.github-stars {
  display: flex;
  align-items: center;
  font-size: 12px;
}

.star-count {
  font-weight: 700;
}

.user-info {
  margin-bottom: 8px;
}

.header.is-expanded {
  flex-basis: @header-width-expanded;
  width: @header-width-expanded;
  align-items: stretch;
}

.header.is-expanded .logo {
  margin-left: 12px;
}

.header.is-expanded .runtime-status-inner {
  justify-content: flex-start;
  padding: 0 10px;
}

.header.is-expanded .nav-item,
.header.is-expanded .nav-item-inner,
.header.is-expanded .github-link {
  justify-content: flex-start;
}

.header.is-expanded .nav-label {
  display: inline-flex;
}

.app-layout.use-top-bar {
  flex-direction: column;
}

.header.top-bar {
  flex-direction: row;
  flex: 0 0 50px;
  width: 100%;
  height: 50px;
  padding: 0 20px;
  gap: 24px;
  border-right: none;
  border-bottom: 1px solid var(--wl-border);
  background:
    radial-gradient(circle at 0% 0%, rgba(var(--wl-gold-rgb), 0.1), transparent 28%),
    linear-gradient(90deg, rgba(7, 15, 24, 0.96), rgba(2, 5, 10, 0.98));
}

.header.top-bar .logo {
  width: 28px;
  height: 28px;
  margin: 0;
}

.header.top-bar .nav {
  flex-direction: row;
  gap: 20px;
  width: auto;
  padding: 0;
}

.header.top-bar .nav-item {
  width: auto;
  padding: 4px 16px;
}

.header.top-bar .nav-label {
  display: inline-flex;
  font-size: 14px;
}

@media (max-width: 720px) {
  .app-layout {
    min-width: 0;
  }

  .header.is-expanded {
    flex-basis: @header-width-collapsed;
    width: @header-width-collapsed;
    align-items: center;
  }

  .header.is-expanded .logo {
    margin: 8px 0 18px;
  }

  .header.is-expanded .runtime-status-inner {
    justify-content: center;
    padding: 0;
  }

  .header.is-expanded .nav-item,
  .header.is-expanded .nav-item-inner,
  .header.is-expanded .github-link {
    justify-content: center;
  }

  .header.is-expanded .nav-label {
    display: none;
  }
}
</style>
