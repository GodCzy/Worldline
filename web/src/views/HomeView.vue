<template>
  <div class="home-container wl-shell">
    <div v-if="isLoading" class="loading-container">
      <a-spin size="large" />
      <p class="loading-text">正在加载 Worldline...</p>
    </div>

    <template v-else>
      <header class="topbar wl-shell-topbar">
        <router-link to="/" class="brand-link wl-brand">
          <img
            v-if="infoStore.organization.logo"
            :src="infoStore.organization.logo"
            :alt="infoStore.organization.name"
            class="brand-logo wl-brand-logo"
            @error="logoFailed = true"
          />
          <span v-if="logoFailed || !infoStore.organization.logo" class="brand-mark">W</span>
          <span class="brand-name wl-brand-text">{{ infoStore.organization.name || 'Worldline' }}</span>
        </router-link>

        <nav class="nav-links wl-nav-pills" aria-label="Primary">
          <router-link to="/worldline" class="nav-link wl-nav-pill">世界线</router-link>
          <router-link to="/themes" class="nav-link wl-nav-pill">模块</router-link>
          <router-link v-if="userStore.isLoggedIn" to="/agent" class="nav-link wl-nav-pill">智能体</router-link>
          <router-link v-if="userStore.isAdmin" to="/graph" class="nav-link wl-nav-pill">图谱</router-link>
          <router-link v-if="userStore.isAdmin" to="/database" class="nav-link wl-nav-pill">知识库</router-link>
        </nav>

        <div class="header-actions">
          <a
            v-if="githubUrl"
            class="icon-link"
            :href="githubUrl"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Repository"
          >
            <Github :size="20" />
          </a>
          <UserInfoComponent :show-button="true" />
        </div>
      </header>

      <main class="home-main">
        <div v-if="backendStatus.state !== 'ready'" class="status-banner" role="status">
          <AlertTriangle :size="18" />
          <span>{{ backendStatus.message }}</span>
          <button type="button" @click="retryLoad">重试连接</button>
        </div>

        <section class="hero-section">
          <div class="hero-copy">
            <p class="eyebrow">LIVING KNOWLEDGE OS</p>
            <h1>{{ infoStore.branding.title || 'Worldline' }}</h1>
            <p class="subtitle">{{ infoStore.branding.subtitle }}</p>
            <p v-if="brandingDescription" class="description">{{ brandingDescription }}</p>

            <div class="hero-actions">
              <button class="primary-button" type="button" @click="openWorldline">
                <Network :size="18" />
                进入世界线
              </button>
              <button class="secondary-button" type="button" @click="openKnowledge">
                <Database :size="18" />
                知识库
              </button>
              <a
                v-if="docsUrl"
                class="secondary-button"
                :href="docsUrl"
                target="_blank"
                rel="noopener noreferrer"
              >
                <BookOpen :size="18" />
                文档
              </a>
            </div>
          </div>

          <div class="signal-panel" aria-label="System surfaces">
            <div v-for="card in featureCards" :key="card.label" class="signal-item">
              <div class="signal-icon">
                <component :is="card.icon" :size="22" />
              </div>
              <div>
                <p class="signal-value">{{ card.value }}</p>
                <h2>{{ card.label }}</h2>
                <p>{{ card.description }}</p>
              </div>
            </div>
          </div>
        </section>

        <section class="module-section">
          <div class="section-header">
            <div>
              <p class="eyebrow">MODULES</p>
              <h2>当前模块</h2>
            </div>
            <span class="module-count">{{ themes.length ? `${themes.length} 个模块` : '等待接入' }}</span>
          </div>

          <div v-if="themes.length" class="theme-grid">
            <article v-for="theme in themes" :key="theme.id" class="theme-card">
              <p class="theme-status">{{ theme.status || 'active' }}</p>
              <h3>{{ theme.name }}</h3>
              <p>{{ theme.description || theme.subtitle }}</p>
              <button type="button" @click="openTheme(theme)">进入模块</button>
            </article>
          </div>

          <div v-else class="empty-module">
            <h3>主题模块已清空</h3>
            <p>旧主题和演示模块已不再作为默认入口。下一步应接入真实知识库、证据、Wiki、图谱和工作流。</p>
            <div class="empty-actions">
              <button type="button" class="secondary-button" @click="openWorldline">查看世界线入口</button>
              <button type="button" class="secondary-button" @click="openKnowledge">查看知识库</button>
            </div>
          </div>
        </section>
      </main>

      <footer class="footer wl-shell-footer">
        <div class="footer-content wl-shell-footer-inner">
          <span>{{ infoStore.footer?.copyright || 'Worldline 2026' }}</span>
        </div>
      </footer>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useInfoStore } from '@/stores/info'
import { healthApi } from '@/apis/system_api'
import UserInfoComponent from '@/components/UserInfoComponent.vue'
import {
  AlertTriangle,
  BookOpen,
  Database,
  FileText,
  Github,
  Network,
  Route,
  ShieldCheck,
  Sparkles
} from 'lucide-vue-next'

const router = useRouter()
const userStore = useUserStore()
const infoStore = useInfoStore()

const isLoading = ref(true)
const logoFailed = ref(false)
const backendStatus = ref({
  state: 'checking',
  message: '正在检查后端服务状态...'
})

const iconKey = (value) => (typeof value === 'string' ? value.toLowerCase() : '')

const featureIconMap = {
  docs: FileText,
  document: FileText,
  route: Route,
  graph: Network,
  shield: ShieldCheck,
  default: Sparkles
}

const withTimeout = (promise, timeoutMs, timeoutMessage) =>
  Promise.race([
    promise,
    new Promise((_, reject) => {
      window.setTimeout(() => reject(new Error(timeoutMessage)), timeoutMs)
    })
  ])

const checkHealth = async () => {
  try {
    const response = await withTimeout(
      healthApi.checkHealth(),
      3500,
      'Backend health check timed out.'
    )
    if (response.status !== 'ok') {
      throw new Error('Backend health response is not ok.')
    }
    backendStatus.value = {
      state: 'ready',
      message: '后端服务已连接。'
    }
  } catch (error) {
    backendStatus.value = {
      state: 'offline',
      message: '后端暂不可用，当前使用本地配置渲染首页。'
    }
    console.warn('Backend health check failed; homepage remains available.', error)
  }
}

const refreshRuntimeStatus = async () => {
  await Promise.allSettled([checkHealth(), infoStore.loadInfoConfig(true)])
}

const loadData = () => {
  isLoading.value = false
  backendStatus.value = {
    state: 'checking',
    message: '正在检查后端服务状态...'
  }
  refreshRuntimeStatus()
}

const retryLoad = () => {
  loadData()
}

const openWorldline = () => {
  router.push('/worldline')
}

const openKnowledge = () => {
  router.push(userStore.isAdmin ? '/database' : '/login')
}

const openTheme = (theme) => {
  router.push(theme.entry_route || `/themes/${theme.id}`)
}

onMounted(() => {
  loadData()
})

const featureCards = computed(() => {
  const list = Array.isArray(infoStore.features) ? infoStore.features : []
  return list
    .map((item) => {
      if (typeof item === 'string') {
        return {
          label: item,
          value: '',
          description: '',
          icon: featureIconMap.default
        }
      }

      const key = iconKey(item.icon || item.type)
      return {
        label: item.label || item.name || '',
        value: item.value || '',
        description: item.description || '',
        icon: featureIconMap[key] || featureIconMap.default
      }
    })
    .filter((item) => item.label || item.value || item.description)
})

const githubUrl = computed(() => infoStore.projectRepoUrl || '')
const docsUrl = computed(() => infoStore.docsUrl || '')
const themes = computed(() => infoStore.themes || [])
const brandingDescription = computed(() => infoStore.branding?.description || '')
</script>

<style lang="less" scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  color: var(--gray-1000);
  background: linear-gradient(180deg, var(--gray-0), var(--main-10));
}

.loading-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
}

.loading-text {
  color: var(--gray-600);
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 18px;
  padding: 14px 28px;
  border-bottom: 1px solid var(--gray-100);
  background: color-mix(in srgb, var(--gray-0) 92%, transparent);
  backdrop-filter: blur(14px);
}

.brand-link,
.nav-link,
.icon-link {
  color: inherit;
  text-decoration: none;
}

.brand-link {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-weight: 800;
}

.brand-logo,
.brand-mark {
  width: 32px;
  height: 32px;
  flex: 0 0 auto;
}

.brand-logo {
  object-fit: contain;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: var(--main-700);
  color: var(--gray-0);
}

.brand-name {
  white-space: nowrap;
}

.nav-links,
.header-actions,
.hero-actions,
.empty-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-links {
  justify-content: center;
  flex-wrap: wrap;
}

.nav-link,
.icon-link {
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  color: var(--gray-700);
  font-weight: 600;
}

.nav-link {
  padding: 0 13px;
}

.icon-link {
  width: 38px;
}

.nav-link:hover,
.icon-link:hover {
  color: var(--main-700);
  background: var(--main-20);
}

.home-main {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding: 28px 0 56px;
}

.status-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding: 12px 14px;
  border: 1px solid var(--main-120);
  border-radius: 8px;
  background: var(--main-20);
  color: var(--main-800);
}

.status-banner button {
  margin-left: auto;
  border: 1px solid var(--main-200);
  background: var(--gray-0);
  color: var(--main-800);
  border-radius: 8px;
  padding: 6px 10px;
  cursor: pointer;
}

.hero-section {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(320px, 0.92fr);
  gap: 28px;
  align-items: center;
  min-height: 520px;
}

.hero-copy {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.eyebrow {
  margin: 0;
  color: var(--main-700);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.hero-copy h1 {
  margin: 0;
  color: var(--gray-1000);
  font-size: clamp(3rem, 6vw, 5rem);
  line-height: 0.98;
  letter-spacing: 0;
}

.subtitle {
  margin: 0;
  color: var(--gray-800);
  font-size: 1.4rem;
  font-weight: 700;
}

.description {
  max-width: 700px;
  margin: 0;
  color: var(--gray-600);
  line-height: 1.7;
}

.primary-button,
.secondary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  padding: 0 16px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
}

.primary-button {
  border: 1px solid var(--main-700);
  background: var(--main-700);
  color: var(--gray-0);
}

.secondary-button {
  border: 1px solid var(--gray-160);
  background: var(--gray-0);
  color: var(--gray-800);
}

.signal-panel {
  display: grid;
  gap: 12px;
}

.signal-item {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr);
  gap: 14px;
  padding: 16px;
  border: 1px solid var(--gray-120);
  border-radius: 8px;
  background: var(--gray-0);
  box-shadow: 0 14px 32px rgba(20, 32, 44, 0.06);
}

.signal-icon {
  width: 48px;
  height: 48px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: var(--main-20);
  color: var(--main-700);
}

.signal-item h2,
.signal-item p {
  margin: 0;
}

.signal-value {
  color: var(--main-700);
  font-size: 12px;
  font-weight: 800;
}

.signal-item h2 {
  margin-top: 3px;
  color: var(--gray-1000);
  font-size: 1.05rem;
}

.signal-item p:last-child {
  margin-top: 6px;
  color: var(--gray-600);
  line-height: 1.6;
}

.module-section {
  margin-top: 18px;
  padding-top: 24px;
  border-top: 1px solid var(--gray-100);
}

.section-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.section-header h2 {
  margin: 6px 0 0;
  color: var(--gray-1000);
}

.module-count {
  border: 1px solid var(--gray-160);
  border-radius: 999px;
  padding: 7px 11px;
  color: var(--gray-700);
  font-size: 13px;
  font-weight: 700;
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px;
}

.theme-card,
.empty-module {
  border: 1px solid var(--gray-120);
  border-radius: 8px;
  background: var(--gray-0);
  padding: 18px;
}

.theme-card h3,
.empty-module h3 {
  margin: 0;
  color: var(--gray-1000);
}

.theme-card p,
.empty-module p {
  color: var(--gray-600);
  line-height: 1.7;
}

.theme-status {
  margin: 0 0 8px;
  color: var(--main-700);
  font-size: 12px;
  font-weight: 800;
}

.theme-card button {
  border: 1px solid var(--main-700);
  border-radius: 8px;
  background: var(--main-700);
  color: var(--gray-0);
  min-height: 38px;
  padding: 0 12px;
  cursor: pointer;
}

.empty-module {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.footer {
  margin-top: auto;
  border-top: 1px solid var(--gray-100);
  background: var(--gray-0);
}

.footer-content {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding: 18px 0;
  color: var(--gray-600);
}

@media (max-width: 900px) {
  .topbar {
    grid-template-columns: 1fr auto;
  }

  .nav-links {
    grid-column: 1 / -1;
    justify-content: flex-start;
  }

  .hero-section {
    grid-template-columns: 1fr;
    min-height: auto;
    padding: 36px 0;
  }
}

@media (max-width: 640px) {
  .topbar {
    padding: 12px 16px;
  }

  .home-main {
    width: min(100% - 24px, 1180px);
  }

  .hero-actions,
  .empty-actions,
  .status-banner {
    align-items: stretch;
    flex-direction: column;
  }

  .primary-button,
  .secondary-button {
    width: 100%;
  }

  .status-banner button {
    margin-left: 0;
  }
}
</style>
