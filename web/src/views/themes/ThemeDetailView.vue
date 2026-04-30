<template>
  <div class="theme-detail-view">
    <header class="detail-header">
      <router-link to="/themes" class="back-link">返回主题分区</router-link>
      <div class="header-actions">
        <a
          v-if="docsUrl"
          class="header-link"
          :href="docsUrl"
          target="_blank"
          rel="noopener noreferrer"
        >
          文档中心
        </a>
      </div>
    </header>

    <main v-if="theme" class="detail-main">
      <section class="hero-card">
        <div class="hero-copy">
          <p class="eyebrow">{{ theme.status }}</p>
          <h1>{{ theme.name }}</h1>
          <p class="subtitle">{{ themeSummary }}</p>

          <div class="hero-actions">
            <router-link class="action-button secondary" :to="workbenchRoute">
              进入世界线工作台
            </router-link>
            <button class="action-button primary" @click="goToChat()">带当前主题继续深聊</button>
            <a
              v-if="theme.links?.docs"
              class="action-button secondary"
              :href="theme.links.docs"
              target="_blank"
              rel="noopener noreferrer"
            >
              查看模块文档
            </a>
            <router-link class="action-button ghost" to="/themes">返回主题分区</router-link>
          </div>
          <p class="flow-hint">进入下一步时会自动带上当前主题上下文，流程不会中断。</p>

          <details v-if="theme.description" class="summary-expand">
            <summary>查看模块说明</summary>
            <p>{{ theme.description }}</p>
          </details>
        </div>
      </section>

      <section class="detail-grid">
        <article class="info-card">
          <h2>当前模块能力（摘要）</h2>
          <ul>
            <li v-for="item in compactHighlights" :key="item">{{ item }}</li>
          </ul>
          <details v-if="remainingHighlights.length" class="summary-expand">
            <summary>查看更多能力</summary>
            <ul>
              <li v-for="item in remainingHighlights" :key="item">{{ item }}</li>
            </ul>
          </details>
        </article>

        <article class="info-card">
          <h2>主题标签（摘要）</h2>
          <div class="tag-list">
            <span v-for="tag in compactTags" :key="tag">{{ tag }}</span>
          </div>
          <details v-if="remainingTags.length" class="summary-expand">
            <summary>查看全部标签</summary>
            <div class="tag-list">
              <span v-for="tag in remainingTags" :key="tag">{{ tag }}</span>
            </div>
          </details>
        </article>

        <article class="info-card">
          <h2>可用入口</h2>
          <div class="entry-list">
            <button
              v-for="entry in compactEntries"
              :key="entry.name"
              class="entry-item"
              @click="openEntry(entry)"
            >
              <span>{{ entry.name }}</span>
              <small>{{ entry.type === 'route' ? '页面入口' : '外部链接' }}</small>
            </button>
          </div>
          <details v-if="remainingEntries.length" class="summary-expand">
            <summary>查看更多入口</summary>
            <div class="entry-list">
              <button
                v-for="entry in remainingEntries"
                :key="entry.name"
                class="entry-item"
                @click="openEntry(entry)"
              >
                <span>{{ entry.name }}</span>
                <small>{{ entry.type === 'route' ? '页面入口' : '外部链接' }}</small>
              </button>
            </div>
          </details>
        </article>
      </section>

      <section v-if="hasThemeShowcase" class="showcase-section">
        <div class="showcase-header">
          <div>
            <p class="eyebrow showcase-eyebrow">{{ showcaseMeta.eyebrow }}</p>
            <h2>{{ showcaseMeta.title }}</h2>
            <p class="showcase-description">{{ showcaseMeta.description }}</p>
          </div>

          <div class="showcase-stats">
            <div class="stat-chip">
              <strong>{{ manifestSummary.card_count }}</strong>
              <span>{{ showcaseMeta.stats.cards }}</span>
            </div>
            <div class="stat-chip">
              <strong>{{ showcaseCandidates.length }}</strong>
              <span>{{ showcaseMeta.stats.recommendations }}</span>
            </div>
            <div class="stat-chip">
              <strong>{{ showcaseGraphs.length }}</strong>
              <span>{{ showcaseMeta.stats.graphs }}</span>
            </div>
          </div>
        </div>

        <div class="showcase-grid">
          <article class="showcase-card">
            <div class="panel-header">
              <div>
                <h3>{{ showcaseMeta.recommendationTitle }}</h3>
                <p>{{ showcaseMeta.recommendationDescription }}</p>
              </div>
            </div>

            <div class="showcase-list">
              <section
                v-for="candidate in showcaseCandidates"
                :key="candidate.id"
                class="showcase-item"
                :class="{ active: activeCandidateId === candidate.id }"
              >
                <div class="showcase-item-header">
                  <div>
                    <h4>{{ candidate.title }}</h4>
                    <p>{{ candidate.subtitle }}</p>
                  </div>
                  <span class="mini-badge">{{ candidate.badge }}</span>
                </div>

                <div class="mini-tag-list">
                  <span v-for="label in candidate.labels" :key="label">{{ label }}</span>
                </div>

                <details class="summary-expand" v-if="candidate.reasons?.length">
                  <summary>&#26597;&#30475;&#25512;&#33616;&#21407;&#22240;</summary>
                  <ul class="reason-list">
                    <li v-for="reason in candidate.reasons" :key="reason">{{ reason }}</li>
                  </ul>
                </details>

                <div class="related-card-list">
                  <span
                    v-for="item in candidate.relatedItems.slice(0, 2)"
                    :key="item.id"
                    class="related-card-pill"
                  >
                    {{ item.title }}
                  </span>
                </div>
                <details class="summary-expand" v-if="candidate.relatedItems.length > 2">
                  <summary>&#26597;&#30475;&#20840;&#37096;&#20851;&#32852;&#21345;&#29255;</summary>
                  <div class="related-card-list">
                    <span
                      v-for="item in candidate.relatedItems.slice(2)"
                      :key="item.id"
                      class="related-card-pill"
                    >
                      {{ item.title }}
                    </span>
                  </div>
                </details>

                <div class="showcase-actions">
                  <button class="action-button secondary compact" @click="applyCandidateSelection(candidate)">
                    {{ showcaseMeta.recommendationActionLabel }}
                  </button>
                  <button class="action-button primary compact" @click="goToCandidateChat(candidate)">
                    {{ showcaseMeta.recommendationChatLabel }}
                  </button>
                </div>
              </section>
            </div>
          </article>

          <article class="showcase-card">
            <div class="panel-header">
              <div>
                <h3>{{ showcaseMeta.graphTitle }}</h3>
                <p>{{ showcaseMeta.graphDescription }}</p>
              </div>
            </div>

            <div class="showcase-list">
              <section
                v-for="graphEntry in showcaseGraphs"
                :key="graphEntry.id"
                class="showcase-item"
                :class="{ active: activeGraphId === graphEntry.id }"
              >
                <div class="showcase-item-header">
                  <div>
                    <h4>{{ graphEntry.title }}</h4>
                    <p>{{ graphEntry.subtitle }}</p>
                  </div>
                  <span class="mini-badge">{{ graphEntry.badge }}</span>
                </div>

                <p class="graph-focus">&#32858;&#28966;&#22330;&#26223;&#65306;{{ graphEntry.focusLabel }}</p>

                <div class="mini-tag-list">
                  <span v-for="node in graphEntry.nodePreview.slice(0, 2)" :key="node">{{ node }}</span>
                </div>

                <div class="related-card-list">
                  <span
                    v-for="item in graphEntry.relatedItems.slice(0, 2)"
                    :key="item.id"
                    class="related-card-pill"
                  >
                    {{ item.title }}
                  </span>
                </div>
                <details class="summary-expand" v-if="graphEntry.relatedItems.length > 2">
                  <summary>&#26597;&#30475;&#20840;&#37096;&#20851;&#32852;&#21345;&#29255;</summary>
                  <div class="related-card-list">
                    <span
                      v-for="item in graphEntry.relatedItems.slice(2)"
                      :key="item.id"
                      class="related-card-pill"
                    >
                      {{ item.title }}
                    </span>
                  </div>
                </details>

                <div class="showcase-actions">
                  <button class="action-button secondary compact" @click="applyGraphSelection(graphEntry)">
                    {{ showcaseMeta.graphActionLabel }}
                  </button>
                  <button class="action-button primary compact" @click="openGraphEntry(graphEntry)">
                    {{ userStore.isAdmin ? showcaseMeta.graphAdminLabel : showcaseMeta.graphUserLabel }}
                  </button>
                </div>
              </section>
            </div>
          </article>
        </div>
      </section>
    </main>

    <main v-else class="not-found">
      <h1>未找到该主题模块</h1>
      <p>当前只开放已经在平台配置中声明的主题入口。</p>
      <router-link class="action-button ghost" to="/themes">返回主题分区</router-link>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useInfoStore } from '@/stores/info'
import { useUserStore } from '@/stores/user'
import { useAgentStore } from '@/stores/agent'
import { useThemeContextStore } from '@/stores/themeContext'
import {
  getWorldlineManifestSummary,
  getWorldlineThemeShowcaseCandidates,
  getWorldlineThemeShowcaseGraphs,
  getWorldlineThemeShowcaseMeta
} from '@/data/worldline'

const route = useRoute()
const router = useRouter()
const infoStore = useInfoStore()
const userStore = useUserStore()
const agentStore = useAgentStore()
const themeContextStore = useThemeContextStore()
const WORLDLINE_HANDOFF_KEY = 'worldline_agent_handoff'

const theme = computed(() => infoStore.getThemeById(String(route.params.themeId || '')))
const themeId = computed(() => theme.value?.id || String(route.params.themeId || ''))
const docsUrl = computed(() => infoStore.docsUrl || '')
const entryPoints = computed(() => (Array.isArray(theme.value?.entry_points) ? theme.value.entry_points : []))
const themeSummary = computed(() => {
  const subtitle = (theme.value?.subtitle || '').trim()
  const description = (theme.value?.description || '').trim()
  return subtitle || (description ? description.slice(0, 60) : '\u6a21\u5757\u5165\u53e3\u5df2\u51c6\u5907\uff0c\u53ef\u76f4\u63a5\u5f00\u59cb\u4e16\u754c\u7ebf\u3002')
})
const compactHighlights = computed(() => (theme.value?.highlights || []).slice(0, 2))
const remainingHighlights = computed(() => (theme.value?.highlights || []).slice(2))
const compactTags = computed(() => (theme.value?.tags || []).slice(0, 3))
const remainingTags = computed(() => (theme.value?.tags || []).slice(3))
const compactEntries = computed(() => entryPoints.value.slice(0, 2))
const remainingEntries = computed(() => entryPoints.value.slice(2))
const showcaseMeta = computed(() =>
  getWorldlineThemeShowcaseMeta(themeId.value, {
    eyebrow: '\u4e3b\u9898\u63a2\u7d22\u5165\u53e3',
    title: '\u63a8\u8350\u8def\u5f84\u4e0e\u56fe\u8c31\u95ed\u73af\u5165\u53e3',
    description: '\u5148\u770b\u6458\u8981\uff0c\u518d\u6309\u9700\u5c55\u5f00\u7ec6\u8282\u3002',
    stats: {
      cards: '\u6837\u672c\u5361\u7247',
      recommendations: '\u63a8\u8350\u8def\u5f84',
      graphs: '\u56fe\u8c31\u95ed\u73af'
    },
    recommendationTitle: '\u63a8\u8350\u8def\u5f84',
    recommendationDescription: '\u9ed8\u8ba4\u53ea\u5c55\u793a\u5173\u952e\u6458\u8981\u3002',
    graphTitle: '\u56fe\u8c31\u95ed\u73af',
    graphDescription: '\u4e3b\u89c6\u56fe\u4ec5\u4fdd\u7559\u95ed\u73af\u6458\u8981\u3002',
    recommendationActionLabel: '\u5199\u5165\u8def\u5f84\u4e0a\u4e0b\u6587',
    recommendationChatLabel: '\u5e26\u6b64\u8def\u5f84\u53bb\u5bf9\u8bdd',
    graphActionLabel: '\u5199\u5165\u56fe\u8c31\u4e0a\u4e0b\u6587',
    graphAdminLabel: '\u8fdb\u5165\u56fe\u8c31\u9875',
    graphUserLabel: '\u5e26\u6b64\u94fe\u8def\u53bb\u5bf9\u8bdd'
  })
)
const showcaseCandidates = computed(() => getWorldlineThemeShowcaseCandidates(themeId.value))
const showcaseGraphs = computed(() => getWorldlineThemeShowcaseGraphs(themeId.value))
const hasThemeShowcase = computed(() => showcaseCandidates.value.length > 0 || showcaseGraphs.value.length > 0)
const manifestSummary = computed(() =>
  hasThemeShowcase.value ? getWorldlineManifestSummary(themeId.value, { card_count: 0 }) : { card_count: 0 }
)
const activeCandidateId = computed(() => themeContextStore.activeContext?.candidate || '')
const activeGraphId = computed(() => themeContextStore.activeContext?.graph || '')
const workbenchRoute = computed(() => `/worldline/${theme.value?.id || String(route.params.themeId || '')}`)

const buildThemeContext = (overrides = {}) => ({
  ...(theme.value?.context || {}),
  ...overrides
})

const buildThemeQuery = (overrides = {}) => themeContextStore.toRouteQuery(buildThemeContext(overrides))

const applyThemeSelection = (overrides = {}) => themeContextStore.setThemeContext(buildThemeContext(overrides))

const buildAgentLocation = (agentId = '', overrides = {}) => {
  const query = buildThemeQuery(overrides)
  if (agentId) {
    return {
      name: 'AgentCompWithId',
      params: { agent_id: agentId },
      query
    }
  }

  return {
    name: 'AgentComp',
    query
  }
}

const buildGraphLocation = (overrides = {}) => ({
  name: 'GraphComp',
  query: buildThemeQuery(overrides)
})

const getCandidateContext = (candidate) => candidate?.context || { entry: 'recommendation' }

const getGraphContext = (graphEntry) => graphEntry?.context || { entry: 'graph' }

const goToChat = async (overrides = {}) => {
  const context = applyThemeSelection(overrides)
  if (!context) {
    await router.push('/agent')
    return
  }

  sessionStorage.setItem(WORLDLINE_HANDOFF_KEY, '1')

  if (!userStore.isLoggedIn) {
    sessionStorage.setItem('redirect', router.resolve(buildAgentLocation('', overrides)).fullPath)
    await router.push('/login')
    return
  }

  if (!agentStore.isInitialized) {
    await agentStore.initialize()
  }

  if (userStore.isAdmin) {
    await router.push(buildAgentLocation('', overrides))
    return
  }

  const defaultAgent = agentStore.defaultAgent
  if (defaultAgent?.id) {
    await router.push(buildAgentLocation(defaultAgent.id, overrides))
    return
  }

  await router.push(buildAgentLocation('', overrides))
}

const applyCandidateSelection = (candidate) => {
  applyThemeSelection(getCandidateContext(candidate))
}

const applyGraphSelection = (graphEntry) => {
  applyThemeSelection(getGraphContext(graphEntry))
}

const goToCandidateChat = async (candidate) => {
  await goToChat(getCandidateContext(candidate))
}

const openGraphEntry = async (graphEntry) => {
  const overrides = getGraphContext(graphEntry)
  applyThemeSelection(overrides)

  if (!userStore.isLoggedIn) {
    sessionStorage.setItem('redirect', router.resolve(buildGraphLocation(overrides)).fullPath)
    await router.push('/login')
    return
  }

  if (userStore.isAdmin) {
    await router.push(buildGraphLocation(overrides))
    return
  }

  await goToChat(overrides)
}

const openEntry = async (entry) => {
  if (entry?.route === '/agent') {
    await goToChat()
    return
  }

  if (entry?.route) {
    await router.push(entry.route)
    return
  }

  const targetUrl = entry?.url || entry?.link
  if (targetUrl) {
    window.open(targetUrl, '_blank', 'noopener,noreferrer')
  }
}

onMounted(() => {
  infoStore.loadInfoConfig()
})
</script>

<style scoped lang="less">
.theme-detail-view {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, var(--main-50), transparent 36%),
    linear-gradient(180deg, var(--gray-10), var(--gray-0));
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
}

.back-link,
.header-link {
  color: var(--gray-700);
  text-decoration: none;
  font-size: 14px;

  &:hover {
    color: var(--main-600);
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.detail-main {
  max-width: 1180px;
  margin: 0 auto;
  padding: 12px 24px 72px;
}

.hero-card {
  display: block;
  padding: 32px;
  border-radius: 24px;
  border: 1px solid var(--gray-100);
  background: var(--gray-0);
  box-shadow: 0 24px 48px rgba(3, 80, 101, 0.08);
}

.eyebrow {
  margin: 0 0 10px;
  color: var(--main-600);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.showcase-eyebrow {
  margin-bottom: 8px;
}

.hero-copy h1 {
  margin: 0;
  color: var(--main-900);
  font-size: clamp(2rem, 4vw, 3.2rem);
  line-height: 1.08;
}

.subtitle {
  margin: 12px 0 0;
  color: var(--gray-700);
  font-size: 1.1rem;
}

.hero-actions,
.showcase-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hero-actions {
  margin-top: 24px;
}

.flow-hint {
  margin: 12px 0 0;
  color: var(--gray-600);
  font-size: 13px;
  line-height: 1.7;
}

.action-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0 18px;
  border-radius: 999px;
  border: 1px solid transparent;
  text-decoration: none;
  font-weight: 600;
  cursor: pointer;
}

.action-button.compact {
  min-height: 38px;
  padding: 0 16px;
  font-size: 13px;
}

.action-button.primary {
  background: linear-gradient(135deg, var(--main-600), var(--main-500));
  color: var(--gray-0);
}

.action-button.secondary {
  background: var(--gray-0);
  border-color: var(--gray-150);
  color: var(--main-700);
}

.action-button.ghost {
  background: color-mix(in srgb, var(--main-20) 70%, var(--gray-0));
  color: var(--main-700);
}

.info-card,
.showcase-card {
  padding: 24px;
  border-radius: 20px;
  background: var(--gray-0);
  border: 1px solid var(--gray-100);
}

.info-card h2 {
  margin: 0 0 14px;
  color: var(--main-900);
  font-size: 1.1rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 24px;
}

.info-card ul {
  margin: 0;
  padding-left: 18px;
  color: var(--gray-600);
  line-height: 1.8;
}

.tag-list,
.mini-tag-list,
.related-card-list,
.showcase-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-list span,
.mini-tag-list span,
.related-card-pill,
.stat-chip {
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--main-20);
  color: var(--main-700);
  font-size: 12px;
  font-weight: 600;
}

.stat-chip {
  flex-direction: column;
  align-items: flex-start;
  min-width: 92px;
  border-radius: 18px;
  background: linear-gradient(180deg, var(--main-20), var(--gray-0));

  strong {
    font-size: 1.2rem;
    color: var(--main-900);
  }

  span {
    padding: 0;
    background: transparent;
    color: var(--gray-600);
  }
}

.entry-list,
.showcase-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.entry-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid var(--gray-150);
  background: var(--gray-0);
  color: var(--gray-800);
  cursor: pointer;
  text-align: left;

  small {
    color: var(--gray-500);
  }

  &:hover {
    border-color: var(--main-300);
    color: var(--main-700);
  }
}

.showcase-section {
  margin-top: 24px;
}

.showcase-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18px;
  margin-bottom: 16px;

  h2 {
    margin: 0;
    color: var(--main-900);
  }
}

.showcase-description {
  margin: 10px 0 0;
  max-width: 420px;
  color: var(--gray-600);
  line-height: 1.6;
}

.showcase-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.panel-header {
  margin-bottom: 16px;

  h3 {
    margin: 0;
    color: var(--main-900);
    font-size: 1.1rem;
  }

  p {
    margin: 8px 0 0;
    color: var(--gray-600);
    line-height: 1.6;
  }
}

.showcase-item {
  padding: 18px;
  border-radius: 18px;
  border: 1px solid var(--gray-120);
  background: linear-gradient(180deg, var(--gray-0), var(--gray-15));

  &.active {
    border-color: var(--main-300);
    box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--main-300) 45%, transparent);
  }
}

.showcase-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;

  h4 {
    margin: 0;
    color: var(--main-900);
    font-size: 1rem;
  }

  p {
    margin: 6px 0 0;
    color: var(--gray-600);
    line-height: 1.6;
  }
}

.mini-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--main-50) 72%, var(--gray-0));
  color: var(--main-700);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.reason-list {
  margin: 14px 0 0;
  padding-left: 18px;
  color: var(--gray-600);
  line-height: 1.7;
}

.graph-focus {
  margin: 14px 0 0;
  color: var(--gray-600);
  line-height: 1.7;
}

.mini-tag-list,
.related-card-list,
.showcase-actions {
  margin-top: 14px;
}

.summary-expand {
  margin-top: 12px;

  summary {
    cursor: pointer;
    color: var(--main-700);
    font-weight: 600;
    font-size: 13px;
  }

  p,
  ul {
    margin-top: 8px;
    color: var(--gray-600);
    line-height: 1.7;
  }
}

.not-found {
  max-width: 760px;
  margin: 0 auto;
  padding: 96px 24px;
  text-align: center;

  h1 {
    margin-bottom: 12px;
    color: var(--main-900);
  }

  p {
    color: var(--gray-600);
    margin-bottom: 24px;
  }
}

@media (max-width: 1080px) {
  .showcase-grid,
  .hero-card,
  .detail-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .detail-header {
    padding: 18px 16px;
    flex-wrap: wrap;
    gap: 12px;
  }

  .detail-main {
    padding: 8px 16px 56px;
  }

  .hero-card,
  .context-card,
  .info-card,
  .showcase-card {
    padding: 20px;
  }

  .hero-actions,
  .showcase-actions {
    flex-direction: column;
  }

  .action-button {
    width: 100%;
  }

  .showcase-header {
    flex-direction: column;
  }
}
</style>
