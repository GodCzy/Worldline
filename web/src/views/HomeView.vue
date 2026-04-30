<template>
  <div class="home-container wl-shell">
    <div v-if="isLoading" class="loading-container">
      <a-spin size="large" />
      <p class="loading-text">正在连接服务...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <a-result status="error" :title="error.title" :sub-title="error.message">
        <template #extra>
          <a-button type="primary" @click="retryLoad">重试</a-button>
        </template>
      </a-result>
    </div>

    <template v-else>
      <div class="hero-section">
        <div class="glass-header wl-shell-topbar">
          <div class="logo wl-brand">
            <img
              :src="infoStore.organization.logo"
              :alt="infoStore.organization.name"
              class="logo-img wl-brand-logo"
            />
            <span class="logo-text wl-brand-text">{{ infoStore.organization.name }}</span>
          </div>
          <nav class="nav-links wl-nav-pills">
            <router-link to="/themes" class="nav-link wl-nav-pill">
              <span>主题分区</span>
            </router-link>
            <a
              v-if="docsUrl"
              class="nav-link wl-nav-pill"
              :href="docsUrl"
              target="_blank"
              rel="noopener noreferrer"
            >
              <span>项目文档</span>
            </a>
            <router-link
              v-if="userStore.isLoggedIn && userStore.isAdmin"
              to="/agent"
              class="nav-link wl-nav-pill"
            >
              <span>智能体</span>
            </router-link>
            <router-link
              v-if="userStore.isLoggedIn && userStore.isAdmin"
              to="/graph"
              class="nav-link wl-nav-pill"
            >
              <span>知识图谱</span>
            </router-link>
            <router-link
              v-if="userStore.isLoggedIn && userStore.isAdmin"
              to="/database"
              class="nav-link wl-nav-pill"
            >
              <span>知识库</span>
            </router-link>
          </nav>
          <div class="header-actions">
            <div v-if="githubUrl" class="github-link">
              <a :href="githubUrl" target="_blank" rel="noopener noreferrer">
                <svg height="20" width="20" viewBox="0 0 16 16" version="1.1">
                  <path
                    fill-rule="evenodd"
                    d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"
                  ></path>
                </svg>
              </a>
            </div>
            <UserInfoComponent :show-button="true" />
          </div>
        </div>

        <div class="hero-layout">
          <div class="hero-content">
            <p class="hero-eyebrow">Worldline 平台</p>
            <h1 class="title">{{ infoStore.branding.title }}</h1>
            <p class="subtitle">{{ infoStore.branding.subtitle }}</p>
            <p v-if="brandingDescription" class="description">{{ brandingDescription }}</p>

            <div class="hero-actions">
              <button class="button-base primary" @click="goToFeaturedTheme">
                {{ featuredTheme ? `进入 ${featuredTheme.name}` : '查看主题分区' }}
              </button>
              <button class="button-base secondary" @click="goToChat">进入智能体</button>
            </div>

            <p v-if="featuredTheme" class="featured-chip">
              首期主题 · {{ featuredTheme.name }} / {{ featuredTheme.subtitle }}
            </p>
          </div>

          <div class="insight-panel" v-if="featureCards.length">
            <div class="stat-card" v-for="card in featureCards" :key="card.label">
              <div class="stat-headline">
                <span class="stat-icon" v-if="card.icon">
                  <component :is="card.icon" />
                </span>
                <p class="stat-value">{{ card.value }}</p>
              </div>
              <p class="stat-label">{{ card.label }}</p>
              <p class="stat-description">{{ card.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <section v-if="themes.length" class="section theme-section">
        <div class="section-header">
          <h2>主题分区</h2>
          <p>平台层统一入口，模块层承载主题知识结构与后续问答、图谱和推荐能力。</p>
        </div>

        <div class="theme-grid">
          <article v-for="theme in themes" :key="theme.id" class="theme-card">
            <div class="theme-card-head">
              <div>
                <p class="theme-status">{{ theme.status }}</p>
                <h3>{{ theme.name }}</h3>
                <p class="theme-subtitle">{{ theme.subtitle }}</p>
              </div>
              <button class="theme-entry" @click="openTheme(theme)">进入主题</button>
            </div>

            <p class="theme-description">{{ theme.description }}</p>

            <div v-if="theme.tags.length" class="theme-tags">
              <span v-for="tag in theme.tags" :key="tag">{{ tag }}</span>
            </div>

            <ul v-if="theme.highlights.length" class="theme-highlights">
              <li v-for="item in theme.highlights" :key="item">{{ item }}</li>
            </ul>
          </article>
        </div>
      </section>

      <div class="section action-section" v-if="actionLinks.length">
        <div class="action-grid">
          <a
            v-for="action in actionLinks"
            :key="action.name"
            class="action-card"
            :href="action.url"
            target="_blank"
            rel="noopener noreferrer"
          >
            <span class="action-icon" v-if="action.icon">
              <component :is="action.icon" />
            </span>
            <div class="action-meta">
              <p class="action-title">{{ action.name }}</p>
              <p class="action-url">{{ action.url }}</p>
            </div>
          </a>
        </div>
      </div>

      <footer class="footer wl-shell-footer">
        <div class="footer-content wl-shell-footer-inner">
          <p class="copyright">{{ infoStore.footer?.copyright || '© 2025 All rights reserved' }}</p>
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
  BookText,
  Bug,
  Video,
  Route,
  Github,
  Star,
  CheckCircle2,
  GitCommit,
  ShieldCheck
} from 'lucide-vue-next'

const router = useRouter()
const userStore = useUserStore()
const infoStore = useInfoStore()

const isLoading = ref(true)
const error = ref(null)

const checkHealth = async () => {
  try {
    const response = await healthApi.checkHealth()
    if (response.status !== 'ok') {
      throw new Error('服务不可用')
    }
  } catch (err) {
    error.value = {
      title: '服务连接失败',
      message: '后端服务无法响应，请检查服务是否正常运行'
    }
    throw err
  }
}

const loadData = async () => {
  isLoading.value = true
  error.value = null

  try {
    await checkHealth()
    await infoStore.loadInfoConfig()
  } catch (err) {
    console.error('加载失败:', err)
  } finally {
    isLoading.value = false
  }
}

const retryLoad = () => {
  loadData()
}

const goToChat = async () => {
  await router.push('/agent')
}

const goToFeaturedTheme = () => {
  if (featuredTheme.value?.entry_route) {
    router.push(featuredTheme.value.entry_route)
    return
  }
  router.push('/themes')
}

const openTheme = (theme) => {
  router.push(theme.entry_route || `/themes/${theme.id}`)
}

onMounted(() => {
  loadData()
})

const iconKey = (value) => (typeof value === 'string' ? value.toLowerCase() : '')

const featureIconMap = {
  stars: Star,
  issues: CheckCircle2,
  resolved: CheckCircle2,
  commits: GitCommit,
  license: ShieldCheck,
  default: Star
}

const actionIconMap = {
  doc: BookText,
  docs: BookText,
  document: BookText,
  issue: Bug,
  bug: Bug,
  roadmap: Route,
  plan: Route,
  demo: Video,
  video: Video,
  github: Github,
  default: Github
}

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

const actionLinks = computed(() => {
  const actions = infoStore.actions
  if (!Array.isArray(actions)) {
    return []
  }

  return actions
    .map((item) => {
      const key = iconKey(item?.icon || item?.type)
      return {
        name: item?.name || item?.label || '',
        url: item?.url || item?.link || '',
        icon: actionIconMap[key] || actionIconMap.default
      }
    })
    .filter((item) => item.name && item.url)
})

const githubUrl = computed(() => infoStore.projectRepoUrl || '')
const docsUrl = computed(() => infoStore.docsUrl || '')
const themes = computed(() => infoStore.themes || [])
const featuredTheme = computed(() => infoStore.primaryTheme)
const brandingDescription = computed(() => infoStore.branding?.description || '')
</script>

<style lang="less" scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  color: var(--main-900);
  background: radial-gradient(circle at top right, var(--main-50), transparent 60%), var(--main-5);
  position: relative;
  overflow-x: hidden;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  gap: 1rem;

  .loading-text {
    color: var(--gray-600);
    font-size: 0.95rem;
  }
}

.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
}

.glass-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0.75rem 2.5rem;
  background-color: var(--color-trans-light);
  backdrop-filter: blur(20px);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  box-shadow: 0 6px 25px rgba(3, 80, 101, 0.02);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  text-decoration: none;
  color: var(--gray-800);
  font-weight: 500;
  font-size: 0.95rem;
  transition: color 0.2s ease;
  position: relative;
  overflow: hidden;

  &:hover {
    color: var(--gray-900);
  }

  &.router-link-active {
    background: linear-gradient(135deg, var(--main-600), var(--main-500));
    color: var(--gray-0);
    border-radius: 1.5rem;
  }

  span {
    white-space: nowrap;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 1.4rem;
  font-weight: bold;
  color: var(--main-800);

  .logo-img {
    height: 2rem;
    margin-right: 0.6rem;
  }
}

.logo-text {
  font-size: 1.3rem;
  font-weight: 600;
}

.github-link a {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: var(--gray-600);
  padding: 0.6rem 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.9rem;
  font-weight: 500;

  &:hover {
    color: var(--gray-700);

    svg {
      transform: scale(1.1);
    }
  }

  svg {
    transition: transform 0.3s ease;
    fill: currentColor;
  }
}

.hero-section {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 5rem 2rem 2rem;
}

.hero-layout {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2.5rem;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 4rem;
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.hero-eyebrow {
  color: var(--main-600);
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-size: 0.85rem;
  margin: 0;
}

.title {
  font-size: clamp(2.5rem, 4vw, 4rem);
  font-weight: 800;
  margin: 0;
  background: linear-gradient(135deg, var(--main-900), var(--main-600));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  letter-spacing: -0.02em;
  line-height: 1.1;
}

.subtitle {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--gray-700);
  line-height: 1.4;
  margin: 0;
}

.description {
  color: var(--gray-600);
  line-height: 1.7;
  margin: 0;
  max-width: 620px;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}

.button-base {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.5rem 2.25rem;
  border-radius: 999px;
  font-size: 1.05rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  text-decoration: none;
  transition: all 0.25s ease;
  min-height: 52px;
}

.button-base.primary {
  background: linear-gradient(135deg, var(--main-600), var(--main-500));
  color: var(--gray-0);
  border-color: transparent;

  &:hover {
    background: linear-gradient(135deg, var(--main-700), var(--main-600));
  }
}

.button-base.secondary {
  background: rgba(2, 57, 68, 0.06);
  color: var(--main-700);
  border-color: var(--gray-100);

  &:hover {
    border-color: var(--main-200);
    background: var(--gray-50);
  }
}

.featured-chip {
  margin: 0;
  color: var(--main-700);
  font-weight: 600;
}

.insight-panel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  background: var(--main-0);
  border-radius: 1.5rem;
  padding: 1.5rem;
  border: 1px solid var(--main-40);
  box-shadow: 0 15px 35px rgba(3, 80, 101, 0.08);
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.stat-headline {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: var(--gray-25);
  display: inline-flex;
  align-items: center;
  justify-content: center;

  :deep(svg) {
    width: 24px;
    height: 24px;
    color: var(--main-700);
  }
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--main-800);
  margin: 0;
}

.stat-label {
  margin: 0;
  color: var(--gray-700);
  font-weight: 600;
}

.stat-description {
  margin: 0;
  color: var(--gray-600);
  font-size: 0.9rem;
}

.section {
  width: 100%;
  max-width: 1200px;
  margin: 48px auto 0;
  padding: 0 0 2rem;
}

.section-header {
  margin-bottom: 1.5rem;

  h2 {
    margin: 0 0 0.5rem;
    font-size: 1.8rem;
    color: var(--main-800);
  }

  p {
    margin: 0;
    color: var(--gray-600);
    line-height: 1.7;
  }
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
}

.theme-card {
  padding: 1.4rem;
  border-radius: 1.2rem;
  background: var(--gray-0);
  border: 1px solid var(--gray-100);
  box-shadow: 0 12px 30px rgba(3, 80, 101, 0.06);
}

.theme-card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.theme-status {
  margin: 0 0 0.5rem;
  color: var(--main-600);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.theme-card h3 {
  margin: 0;
  color: var(--main-900);
  font-size: 1.3rem;
}

.theme-subtitle {
  margin: 0.45rem 0 0;
  color: var(--gray-600);
}

.theme-description {
  margin: 1rem 0 0;
  color: var(--gray-700);
  line-height: 1.7;
}

.theme-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;

  span {
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    background: var(--main-20);
    color: var(--main-700);
    font-size: 0.75rem;
    font-weight: 600;
  }
}

.theme-highlights {
  margin: 1rem 0 0;
  padding-left: 1.2rem;
  color: var(--gray-600);
  line-height: 1.7;
}

.theme-entry {
  border: none;
  border-radius: 999px;
  background: var(--gray-25);
  color: var(--main-700);
  padding: 0.7rem 1rem;
  font-weight: 600;
  cursor: pointer;
}

.action-section {
  padding-bottom: 3rem;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 1rem 1.25rem;
  border-radius: 1rem;
  text-decoration: none;
  color: inherit;
  border: 1px solid var(--gray-50);
  background: var(--gray-0);
  transition:
    transform 0.2s ease,
    background 0.2s ease;

  &:hover {
    transform: translateY(-2px);
  }
}

.action-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: var(--gray-50);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  :deep(svg) {
    width: 22px;
    height: 22px;
    color: var(--main-700);
  }
}

.action-meta {
  flex: 1;
  overflow: hidden;
}

.action-title {
  margin: 0;
  font-weight: 600;
  color: var(--main-800);
}

.action-url {
  margin: 0.25rem 0 0;
  font-size: 0.9rem;
  color: var(--gray-600);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.footer {
  margin-top: auto;
  background: var(--main-0);
  border-top: 1px solid var(--main-20);
}

.footer-content {
  text-align: center;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.copyright {
  color: var(--main-700);
  font-size: 0.9rem;
  font-weight: 500;
  margin: 0;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .glass-header {
    padding: 0.8rem 1.25rem;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .nav-links {
    order: 3;
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .nav-link {
    padding: 0.5rem 0.8rem;
    font-size: 0.85rem;
  }

  .logo {
    font-size: 1.1rem;
  }

  .title {
    font-size: 2.4rem;
  }

  .subtitle {
    font-size: 1.2rem;
  }

  .button-base,
  .theme-entry {
    width: 100%;
  }

  .hero-layout,
  .section {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }

  .theme-card-head {
    flex-direction: column;
  }
}
</style>
