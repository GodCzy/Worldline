<script setup>
import { ref, reactive, onMounted, computed, provide } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { GithubOutlined } from '@ant-design/icons-vue'
import {
  House,
  LayoutGrid,
  Bot,
  Waypoints,
  LibraryBig,
  BarChart3,
  CircleCheck,
  Blocks,
  ChevronsLeft,
  ChevronsRight
} from 'lucide-vue-next'

import { useConfigStore } from '@/stores/config'
import { useDatabaseStore } from '@/stores/database'
import { useInfoStore } from '@/stores/info'
import { useTaskerStore } from '@/stores/tasker'
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'
import UserInfoComponent from '@/components/UserInfoComponent.vue'
import DebugComponent from '@/components/DebugComponent.vue'
import TaskCenterDrawer from '@/components/TaskCenterDrawer.vue'
import SettingsModal from '@/components/SettingsModal.vue'

const configStore = useConfigStore()
const databaseStore = useDatabaseStore()
const infoStore = useInfoStore()
const taskerStore = useTaskerStore()
const userStore = useUserStore()
const { activeCount: activeCountRef, isDrawerOpen } = storeToRefs(taskerStore)

const layoutSettings = reactive({
  showDebug: false,
  useTopBar: false // 是否使用顶栏
})

// Add state for GitHub stars
const githubStars = ref(0)
const isLoadingStars = ref(false)

// Add state for debug modal
const showDebugModal = ref(false)

// Add state for settings modal
const showSettingsModal = ref(false)

// Provide settings modal methods to child components
const openSettingsModal = () => {
  showSettingsModal.value = true
}

// Handle debug modal close
const handleDebugModalClose = () => {
  showDebugModal.value = false
}

const getRemoteConfig = async () => {
  if (!userStore.isAdmin) return
  try {
    await configStore.refreshConfig()
  } catch (error) {
    console.warn('加载系统配置失败:', error)
  }
}

const getRemoteDatabase = async () => {
  if (!userStore.isLoggedIn) {
    return
  }
  try {
    await databaseStore.loadDatabases()
  } catch (error) {
    console.warn('加载知识库列表失败:', error)
  }
}

const projectRepoUrl = computed(() => infoStore.projectRepoUrl || '')

const extractGithubRepoPath = (repoUrl) => {
  if (!repoUrl) {
    return ''
  }

  try {
    const parsed = new URL(repoUrl)
    if (parsed.hostname !== 'github.com') {
      return ''
    }

    const segments = parsed.pathname.split('/').filter(Boolean)
    if (segments.length < 2) {
      return ''
    }

    return `${segments[0]}/${segments[1].replace(/\.git$/, '')}`
  } catch (error) {
    console.warn('无法解析项目仓库地址:', error)
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
    // 公共API，可以直接使用fetch
    const response = await fetch(`https://api.github.com/repos/${repoPath}`)
    if (!response.ok) {
      throw new Error(`GitHub API ${response.status}`)
    }
    const data = await response.json()
    githubStars.value = data.stargazers_count
  } catch (error) {
    console.error('获取GitHub stars失败:', error)
  } finally {
    isLoadingStars.value = false
  }
}

onMounted(async () => {
  // 加载信息配置
  await infoStore.loadInfoConfig()
  // 加载知识库数据（普通用户加载可访问知识库）
  await getRemoteDatabase()
  // 仅管理员加载系统配置和任务中心数据
  if (userStore.isAdmin) {
    await getRemoteConfig()
    taskerStore.loadTasks()
    if (projectRepoUrl.value) {
      fetchGithubStars(projectRepoUrl.value)
    }
  }
})

const route = useRoute()
const isEmbed = computed(() => route.query.embed === '1')
const NAV_EXPANDED_STORAGE_KEY = 'worldline_app_nav_expanded'
const isNavExpanded = ref(localStorage.getItem(NAV_EXPANDED_STORAGE_KEY) === '1')
const showNavLabel = computed(() => !layoutSettings.useTopBar && isNavExpanded.value)

const toggleNavExpanded = () => {
  isNavExpanded.value = !isNavExpanded.value
  localStorage.setItem(NAV_EXPANDED_STORAGE_KEY, isNavExpanded.value ? '1' : '0')
}

const activeTaskCount = computed(() => activeCountRef.value || 0)

const isNavItemActive = (path) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

// 下面是导航菜单部分，添加智能体项
const mainList = computed(() => {
  const items = [
    {
      name: '首页',
      path: '/',
      icon: House,
      activeIcon: House
    },
    {
      name: '主题分区',
      path: '/themes',
      icon: LayoutGrid,
      activeIcon: LayoutGrid
    },
    {
      name: '世界线',
      path: '/worldline',
      icon: Waypoints,
      activeIcon: Waypoints
    },
    {
      name: '智能体',
      path: '/agent',
      icon: Bot,
      activeIcon: Bot
    }
  ]

    if (userStore.isAdmin) {
      items.push(
        {
          name: '知识图谱',
          path: '/graph',
        icon: Waypoints,
        activeIcon: Waypoints
      },
      {
        name: '知识库',
        path: '/database',
        icon: LibraryBig,
        activeIcon: LibraryBig
      }
    )

    if (userStore.isSuperAdmin) {
      items.push({
        name: '扩展管理',
        path: '/extensions',
        icon: Blocks,
        activeIcon: Blocks
      })
    }

      items.push({
        name: '运营看板',
        path: '/dashboard',
        icon: BarChart3,
        activeIcon: BarChart3
      })
    }

  return items
})

// Provide settings modal methods to child components
provide('settingsModal', {
  openSettingsModal
})
</script>

<template>
  <div class="app-layout" :class="{ 'use-top-bar': layoutSettings.useTopBar, 'embed-mode': isEmbed }">
    <div
      v-if="!isEmbed"
      class="header"
      :class="{ 'top-bar': layoutSettings.useTopBar, 'is-expanded': showNavLabel }"
    >
      <div class="logo circle">
        <router-link to="/">
          <img v-if="infoStore.organization.avatar" :src="infoStore.organization.avatar" alt="Worldline" />
          <Waypoints v-else class="logo-fallback-icon" size="22" aria-hidden="true" />
        </router-link>
      </div>
      <div class="nav">
        <button
          v-if="!layoutSettings.useTopBar"
          class="nav-item nav-expand-toggle"
          type="button"
          :title="showNavLabel ? '收起导航' : '展开导航'"
          @click="toggleNavExpanded()"
        >
          <component :is="showNavLabel ? ChevronsLeft : ChevronsRight" class="icon" size="20" />
          <span v-if="showNavLabel" class="nav-label">{{ showNavLabel ? '收起导航' : '展开导航' }}</span>
        </button>
        <!-- 使用mainList渲染导航项 -->
        <RouterLink
          v-for="(item, index) in mainList"
          :key="index"
          :to="item.path"
          v-show="!item.hidden"
          class="nav-item"
          active-class="active"
        >
          <a-tooltip :disabled="showNavLabel" placement="right">
            <template #title>{{ item.name }}</template>
            <div class="nav-item-inner">
              <component
                class="icon"
                :is="isNavItemActive(item.path) ? item.activeIcon : item.icon"
                size="22"
              />
              <span v-if="showNavLabel" class="nav-label">{{ item.name }}</span>
            </div>
          </a-tooltip>
        </RouterLink>
        <div
          v-if="userStore.isAdmin"
          class="nav-item task-center"
          :class="{ active: isDrawerOpen }"
          @click="taskerStore.openDrawer()"
        >
          <a-tooltip :disabled="showNavLabel" placement="right">
            <template #title>任务中心</template>
            <div class="nav-item-inner">
              <a-badge
                :count="activeTaskCount"
                :overflow-count="99"
                class="task-center-badge"
                size="small"
              >
                <CircleCheck class="icon" size="22" />
              </a-badge>
              <span v-if="showNavLabel" class="nav-label">任务中心</span>
            </div>
          </a-tooltip>
        </div>
      </div>
      <div class="fill"></div>
      <div v-if="projectRepoUrl" class="github nav-item">
        <a-tooltip placement="right">
          <template #title>项目仓库</template>
          <a :href="projectRepoUrl" target="_blank" rel="noopener noreferrer" class="github-link">
            <GithubOutlined class="icon" />
            <span v-if="githubStars > 0" class="github-stars">
              <span class="star-count">{{ (githubStars / 1000).toFixed(1) }}k</span>
            </span>
          </a>
        </a-tooltip>
      </div>
      <!-- 用户信息组件 -->
      <div class="nav-item user-info">
        <UserInfoComponent />
      </div>
    </div>
    <router-view v-slot="{ Component, route }" id="app-router-view">
      <keep-alive v-if="route.meta.keepAlive !== false">
        <component :is="Component" />
      </keep-alive>
      <component :is="Component" v-else />
    </router-view>

    <!-- Debug Modal -->
    <a-modal
      v-model:open="showDebugModal"
      title="调试面板（非生产环境）"
      width="90%"
      :footer="null"
      @cancel="handleDebugModalClose"
      :maskClosable="true"
      :destroyOnClose="true"
      class="debug-modal"
    >
      <DebugComponent />
    </a-modal>
    <TaskCenterDrawer v-if="userStore.isAdmin" />
    <SettingsModal v-model:visible="showSettingsModal" @close="() => (showSettingsModal = false)" />
  </div>
</template>

<style lang="less" scoped>
// Less 变量定义
@header-width-collapsed: 56px;
@header-width-expanded: 188px;

.app-layout {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 100vh;
  min-width: var(--min-width);
}

.app-layout.embed-mode {
  flex-direction: column;
  min-width: 0;
}

.app-layout.embed-mode #app-router-view {
  height: 100vh;
}

div.header,
#app-router-view {
  height: 100%;
  max-width: 100%;
  user-select: none;
}

#app-router-view {
  flex: 1 1 auto;
  min-width: 0;
  overflow-y: auto;
}

.header {
  display: flex;
  flex-direction: column;
  flex: 0 0 @header-width-collapsed;
  justify-content: flex-start;
  align-items: center;
  background-color: color-mix(in srgb, var(--main-0) 88%, var(--gray-0));
  height: 100%;
  width: @header-width-collapsed;
  border-right: 1px solid var(--gray-100);
  transition:
    width 0.2s ease,
    flex-basis 0.2s ease,
    padding 0.2s ease;
  overflow: hidden;

  .nav {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: stretch;
    position: relative;
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
    margin: 8px 0 18px 0;

    img {
      width: 100%;
      height: 100%;
      border-radius: 8px;
    }

    .logo-fallback-icon {
      color: var(--main-color);
    }

    & > a {
      display: flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
    }
  }

  .nav-item {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 40px;
    padding: 0 10px;
    border: 1px solid transparent;
    border-radius: 12px;
    background-color: transparent;
    color: var(--gray-1000);
    font-size: 14px;
    transition:
      background-color 0.2s ease-in-out,
      color 0.2s ease-in-out;
    margin: 0;
    text-decoration: none;
    cursor: pointer;
    outline: none;
    gap: 10px;
    appearance: none;

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
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      font-weight: 600;
      font-size: 13px;
      color: inherit;
    }

    & > svg:focus,
    .icon:focus {
      outline: none;
    }

    & > svg:focus-visible,
    .icon:focus-visible {
      outline: none;
    }

    &.active {
      background-color: color-mix(in srgb, var(--main-50) 70%, var(--gray-0));
      color: var(--main-color);
    }

    &.warning {
      color: var(--color-error-500);
    }

    &:hover {
      color: var(--main-color);
    }

    &.nav-expand-toggle {
      margin-bottom: 4px;
      border-style: dashed;
      border-color: color-mix(in srgb, var(--gray-180) 88%, transparent);
    }

    &.github {
      padding: 8px 10px;
      margin-bottom: 16px;
      &:hover {
        background-color: transparent;
        border: 1px solid transparent;
      }

      .github-link {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 8px;
        color: inherit;
        width: 100%;
        justify-content: center;
      }

      .github-stars {
        display: flex;
        align-items: center;
        font-size: 12px;
        margin-top: 0;

        .star-icon {
          color: var(--color-warning-500);
          font-size: 12px;
          margin-right: 2px;
        }

        .star-count {
          font-weight: 600;
        }
      }
    }

    &.api-docs {
      padding: 10px 12px;
    }
    &.docs {
      display: none;
    }
    &.task-center {
      .task-center-badge {
        display: flex;
        justify-content: center;
      }
    }

    &.theme-toggle-nav {
      .theme-toggle-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        cursor: pointer;
        color: var(--gray-1000);
        transition: color 0.2s ease-in-out;

        &:hover {
          color: var(--main-color);
        }
      }
    }
    &.user-info {
      margin-bottom: 8px;
    }
  }
}

.header.is-expanded {
  flex-basis: @header-width-expanded;
  width: @header-width-expanded;
  align-items: stretch;

  .logo {
    margin: 8px 0 18px 12px;
  }

  .nav-item {
    justify-content: flex-start;

    .nav-item-inner {
      justify-content: flex-start;
    }

    .nav-label {
      display: inline-flex;
      align-items: center;
    }
  }

  .github.nav-item .github-link {
    justify-content: flex-start;
  }
}

.app-layout.use-top-bar {
  flex-direction: column;
}

.header.top-bar {
  flex-direction: row;
  flex: 0 0 50px;
  width: 100%;
  height: 50px;
  border-right: none;
  border-bottom: 1px solid var(--main-40);
  background-color: var(--main-20);
  padding: 0 20px;
  gap: 24px;

  .logo {
    width: fit-content;
    height: 28px;
    margin-right: 16px;
    display: flex;
    align-items: center;

    a {
      display: flex;
      align-items: center;
      text-decoration: none;
      color: inherit;
    }

    img {
      width: 28px;
      height: 28px;
      margin-right: 8px;
    }
  }

  .nav {
    flex-direction: row;
    height: auto;
    gap: 20px;
  }

  .nav-item {
    flex-direction: row;
    width: auto;
    padding: 4px 16px;
    margin: 0;
    gap: 0;

    .nav-item-inner {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .nav-label {
      display: inline-flex;
      align-items: center;
      font-size: 14px;
    }

    .icon {
      margin-right: 8px;
      font-size: 15px; // 减小图标大小
      border: none;
      outline: none;

      &:focus,
      &:active {
        border: none;
        outline: none;
      }
    }

    .text {
      margin-top: 0;
      font-size: 15px;
    }

    &.github {
      padding: 8px 12px;

      .icon {
        margin-right: 0;
        font-size: 18px;
      }

      &.active {
        color: var(--main-color);
      }

      a {
        display: flex;
        align-items: center;
      }

      .github-stars {
        display: flex;
        align-items: center;
        margin-left: 6px;

        .star-icon {
          color: var(--color-warning-500);
          font-size: 14px;
          margin-right: 2px;
        }
      }
    }

    &.theme-toggle-nav {
      padding: 8px 12px;

      .theme-toggle-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--gray-1000);
        transition: color 0.2s ease-in-out;
        cursor: pointer;

        &:hover {
          color: var(--main-color);
        }
      }

      &.active {
        .theme-toggle-icon {
          color: var(--main-color);
        }
      }
    }
  }
}

@media (max-width: 720px) {
  .app-layout {
    min-width: 0;
  }

  .header.is-expanded {
    flex-basis: @header-width-collapsed;
    width: @header-width-collapsed;
    align-items: center;

    .logo {
      margin: 8px 0 18px;
    }

    .nav-item {
      justify-content: center;

      .nav-item-inner {
        justify-content: center;
      }

      .nav-label {
        display: none;
      }
    }

    .github.nav-item .github-link {
      justify-content: center;
    }
  }
}
</style>
