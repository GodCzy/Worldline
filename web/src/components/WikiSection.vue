<template>
  <section class="wiki-section">
    <header class="wiki-toolbar">
      <div>
        <p>LLM Wiki</p>
        <h3>证据化页面</h3>
      </div>
      <div class="wiki-actions">
        <a-button size="small" :loading="loading" @click="loadWiki">
          <template #icon><RefreshCw :size="14" /></template>
          刷新
        </a-button>
        <a-button size="small" type="primary" :loading="rebuilding" @click="rebuildWiki">
          <template #icon><BookOpen :size="14" /></template>
          重建
        </a-button>
      </div>
    </header>

    <div class="wiki-stats">
      <span><strong>{{ pages.length }}</strong> 页面</span>
      <span><strong>{{ supportedClaimCount }}</strong> 支持主张</span>
      <span><strong>{{ citationCount }}</strong> 引用</span>
      <span :class="{ warn: staleCount > 0 }"><strong>{{ staleCount }}</strong> stale</span>
    </div>

    <a-alert
      v-if="error"
      class="wiki-alert"
      type="warning"
      show-icon
      :message="error"
    />

    <a-spin :spinning="loading">
      <a-empty v-if="!pages.length && !loading" description="当前知识库还没有 Wiki 页面">
        <a-button type="primary" :loading="rebuilding" @click="rebuildWiki">生成 Wiki</a-button>
      </a-empty>

      <div v-else class="wiki-content">
        <nav class="wiki-list" aria-label="Wiki pages">
          <button
            v-for="page in pages"
            :key="page.page_id"
            type="button"
            class="wiki-page-item"
            :class="{ active: page.page_id === selectedPageId }"
            @click="selectPage(page)"
          >
            <span>{{ page.title }}</span>
            <small>{{ pageTypeLabel(page.page_type) }} / {{ reviewStatus(page) }}</small>
          </button>
        </nav>

        <article v-if="selectedPage" class="wiki-detail">
          <div class="wiki-detail-head">
            <div>
              <p>{{ pageTypeLabel(selectedPage.page_type) }}</p>
              <h4>{{ selectedPage.title }}</h4>
            </div>
            <a-button size="small" @click="detailDrawerOpen = true">详情</a-button>
          </div>

          <div class="wiki-badges">
            <span>{{ reviewStatus(selectedPage) }}</span>
            <span>{{ coverageStatus(selectedPage) }}</span>
            <span>{{ freshnessStatus(selectedPage) }}</span>
          </div>

          <section class="wiki-block">
            <h5>主张</h5>
            <ul v-if="selectedClaims.length">
              <li v-for="claim in selectedClaims" :key="claim.id || claim.text">
                <ShieldCheck :size="14" />
                <span>{{ claim.text || claim.claim || claim.summary }}</span>
              </li>
            </ul>
            <p v-else>暂无主张。</p>
          </section>

          <section class="wiki-block">
            <h5>引用</h5>
            <ul v-if="selectedCitations.length">
              <li v-for="citation in selectedCitations" :key="citation.evidence_id || citation.id">
                <Link2 :size="14" />
                <span>{{ citation.evidence_id || citation.id || citation.source }}</span>
              </li>
            </ul>
            <p v-else>暂无引用。</p>
          </section>

          <section class="wiki-block">
            <h5>待审问题</h5>
            <ul v-if="selectedQuestions.length">
              <li v-for="question in selectedQuestions" :key="question.question || question.id">
                <AlertTriangle :size="14" />
                <span>{{ question.question || question.text }}</span>
              </li>
            </ul>
            <p v-else>暂无待审问题。</p>
          </section>
        </article>
      </div>
    </a-spin>

    <a-drawer
      :open="detailDrawerOpen"
      class="wiki-detail-drawer wl-ant-dark"
      title="Wiki 页面详情"
      width="min(560px, 100vw)"
      @close="detailDrawerOpen = false"
    >
      <div v-if="selectedPage" class="wiki-drawer-body">
        <div class="drawer-metadata">
          <span>{{ reviewStatus(selectedPage) }}</span>
          <span>{{ coverageStatus(selectedPage) }}</span>
          <span>{{ freshnessStatus(selectedPage) }}</span>
        </div>
        <pre class="wiki-markdown">{{ selectedPage.markdown || selectedPage.markdown_preview || '暂无 Markdown 内容。' }}</pre>
      </div>
    </a-drawer>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { message } from 'ant-design-vue'
import { AlertTriangle, BookOpen, Link2, RefreshCw, ShieldCheck } from 'lucide-vue-next'
import { worldlineApi } from '@/apis/worldline_api'

const props = defineProps({
  databaseId: {
    type: String,
    required: true
  },
  active: {
    type: Boolean,
    default: false
  }
})

const loading = ref(false)
const rebuilding = ref(false)
const error = ref('')
const pages = ref([])
const stale = ref({})
const selectedPageId = ref('')
const selectedPageDetail = ref(null)
const detailDrawerOpen = ref(false)
const loadedForDb = ref('')

const selectedPage = computed(() => {
  const listed = pages.value.find((page) => page.page_id === selectedPageId.value) || pages.value[0] || null
  return selectedPageDetail.value?.page_id === listed?.page_id ? selectedPageDetail.value : listed
})

const selectedClaims = computed(() => (selectedPage.value?.claims || []).slice(0, 5))
const selectedCitations = computed(() => (selectedPage.value?.citations || []).slice(0, 5))
const selectedQuestions = computed(() => (selectedPage.value?.open_questions || []).slice(0, 4))
const staleCount = computed(() => stale.value?.stale_count || stale.value?.items?.length || 0)
const citationCount = computed(() => pages.value.reduce((total, page) => total + (page.citations?.length || 0), 0))
const supportedClaimCount = computed(() =>
  pages.value.reduce(
    (total, page) => total + (page.claims || []).filter((claim) => claim.status !== 'unsupported').length,
    0
  )
)

const pageTypeLabel = (type = '') =>
  ({
    home: '首页',
    document: '文档',
    topic: '主题',
    glossary: '术语'
  })[type] || type || '页面'

const reviewStatus = (page = {}) => page.review?.status || page.status || 'pending'
const coverageStatus = (page = {}) => page.evidence_coverage?.status || 'coverage unknown'
const freshnessStatus = (page = {}) => page.freshness?.status || 'freshness unknown'

const loadWiki = async () => {
  if (!props.databaseId) return
  loading.value = true
  error.value = ''
  try {
    const [pageResult, staleResult] = await Promise.all([
      worldlineApi.listWikiPages(props.databaseId, { limit: 80 }),
      worldlineApi.listStaleWikiPages(props.databaseId)
    ])
    pages.value = pageResult?.items || []
    stale.value = staleResult || {}
    selectedPageId.value = selectedPageId.value || pages.value[0]?.page_id || ''
    if (selectedPageId.value) await loadPageDetail(selectedPageId.value)
    loadedForDb.value = props.databaseId
  } catch (err) {
    error.value = err?.response?.data?.detail || err?.message || 'Wiki 页面读取失败'
  } finally {
    loading.value = false
  }
}

const loadPageDetail = async (pageId) => {
  if (!props.databaseId || !pageId) return
  try {
    selectedPageDetail.value = await worldlineApi.getWikiPage(props.databaseId, pageId)
  } catch (err) {
    message.warning(err?.response?.data?.detail || 'Wiki 详情读取失败')
  }
}

const selectPage = async (page) => {
  selectedPageId.value = page.page_id
  await loadPageDetail(page.page_id)
}

const rebuildWiki = async () => {
  if (!props.databaseId) return
  rebuilding.value = true
  error.value = ''
  try {
    await worldlineApi.rebuildWiki(props.databaseId, { max_topics: 8 })
    message.success('Wiki 已重建')
    selectedPageId.value = ''
    selectedPageDetail.value = null
    await loadWiki()
  } catch (err) {
    error.value = err?.response?.data?.detail || err?.message || 'Wiki 重建失败'
  } finally {
    rebuilding.value = false
  }
}

watch(
  () => [props.databaseId, props.active],
  ([dbId, active]) => {
    if (dbId && active && loadedForDb.value !== dbId) {
      loadWiki()
    }
  },
  { immediate: true }
)
</script>

<style lang="less" scoped>
.wiki-section {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 14px;
  overflow: hidden;
  color: #dbeafe;
}

.wiki-toolbar,
.wiki-detail-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.wiki-toolbar p,
.wiki-detail-head p {
  margin: 0 0 4px;
  color: rgba(148, 163, 184, 0.9);
  font-size: 12px;
}

.wiki-toolbar h3,
.wiki-detail-head h4 {
  margin: 0;
  color: #f8fafc;
}

.wiki-actions,
.wiki-badges,
.drawer-metadata {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.wiki-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.wiki-stats span,
.wiki-badges span,
.drawer-metadata span {
  border: 1px solid rgba(125, 211, 252, 0.18);
  border-radius: 8px;
  padding: 6px 8px;
  background: rgba(15, 23, 42, 0.72);
  color: #cbd5e1;
  font-size: 12px;
}

.wiki-stats strong {
  color: #67e8f9;
}

.wiki-stats .warn strong {
  color: #facc15;
}

.wiki-alert {
  flex-shrink: 0;
}

.wiki-content {
  min-height: 0;
  flex: 1;
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  gap: 12px;
  overflow: hidden;
}

.wiki-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: auto;
  padding-right: 4px;
}

.wiki-page-item {
  width: 100%;
  text-align: left;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.68);
  color: #e2e8f0;
  padding: 10px;
  cursor: pointer;
}

.wiki-page-item.active {
  border-color: rgba(34, 211, 238, 0.72);
  background: rgba(8, 47, 73, 0.66);
}

.wiki-page-item span,
.wiki-page-item small {
  display: block;
  overflow-wrap: anywhere;
}

.wiki-page-item small {
  margin-top: 4px;
  color: rgba(203, 213, 225, 0.72);
}

.wiki-detail {
  min-width: 0;
  overflow: auto;
  border: 1px solid rgba(125, 211, 252, 0.18);
  border-radius: 8px;
  background: rgba(2, 6, 23, 0.48);
  padding: 14px;
}

.wiki-block {
  margin-top: 14px;
}

.wiki-block h5 {
  margin: 0 0 8px;
  color: #bfdbfe;
}

.wiki-block ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0;
  margin: 0;
}

.wiki-block li {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  color: #e2e8f0;
}

.wiki-block li span {
  min-width: 0;
  overflow-wrap: anywhere;
}

.wiki-block p {
  color: rgba(203, 213, 225, 0.72);
  margin: 0;
}

.wiki-drawer-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.wiki-markdown {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  color: #e2e8f0;
  background: rgba(2, 6, 23, 0.88);
  border: 1px solid rgba(125, 211, 252, 0.18);
  border-radius: 8px;
  padding: 12px;
  max-height: 70vh;
  overflow: auto;
}

:global(.wiki-detail-drawer .ant-drawer-content),
:global(.wiki-detail-drawer .ant-drawer-header),
:global(.wiki-detail-drawer .ant-drawer-body) {
  background: #020617;
  color: #e2e8f0;
}

:global(.wiki-detail-drawer .ant-drawer-title),
:global(.wiki-detail-drawer .ant-drawer-close) {
  color: #f8fafc;
}

@media (max-width: 900px) {
  .wiki-content {
    grid-template-columns: 1fr;
  }

  .wiki-list {
    max-height: 180px;
  }
}

@media (max-width: 560px) {
  .wiki-section {
    padding: 10px;
  }

  .wiki-toolbar,
  .wiki-detail-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .wiki-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
