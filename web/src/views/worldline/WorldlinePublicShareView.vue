<template>
  <div class="public-share-view" data-worldline-public-share="true">
    <header class="share-header">
      <div>
        <p class="eyebrow">WORLDLINE PUBLIC DEMO</p>
        <h1>{{ headerTitle }}</h1>
        <p>{{ headerSubtitle }}</p>
      </div>
      <nav class="share-actions" aria-label="Public demo actions">
        <router-link class="share-link" to="/worldline">Hub</router-link>
        <button class="share-link" type="button" :disabled="isBusy" @click="downloadBundle('json')">
          JSON Bundle
        </button>
        <button
          class="share-link"
          type="button"
          :disabled="isBusy"
          data-evidence-bundle-export="true"
          @click="downloadBundle('markdown')"
        >
          Markdown
        </button>
      </nav>
    </header>

    <main v-if="isLoading" class="share-state">
      <span class="pulse-dot" />
      <strong>Loading public branch</strong>
    </main>

    <main v-else-if="loadError" class="share-state error">
      <strong>Public share unavailable</strong>
      <span>{{ loadError }}</span>
    </main>

    <main v-else class="share-grid">
      <section class="share-stage">
        <WorldlineBranchCanvas
          :tree="worldline.tree || emptyTree"
          :active-branch-id="branch.id"
          :selected-node-id="branch.id"
          :branch-count="branchCount"
          :display-meta="worldline.displayMeta || {}"
          :active-snapshot="activeSnapshot"
          @select-node="selectNode"
        />
      </section>

      <aside class="share-panel">
        <section class="summary-block" data-public-demo-dataset="true">
          <div class="section-head">
            <p class="eyebrow">READ ONLY SHARE</p>
            <span class="status-pill">{{ payload?.safety?.status || 'pending' }}</span>
          </div>
          <h2>{{ branch.title || branch.id }}</h2>
          <p>{{ branch.hypothesis }}</p>
          <dl class="compact-facts">
            <div>
              <dt>Dataset</dt>
              <dd>{{ dataset.datasetId }}</dd>
            </div>
            <div>
              <dt>Checksum</dt>
              <dd>{{ bundlePreview.checksum }}</dd>
            </div>
            <div>
              <dt>Mode</dt>
              <dd>{{ payload?.mode || 'read_only' }}</dd>
            </div>
          </dl>
        </section>

        <section class="summary-block">
          <div class="section-head">
            <p class="eyebrow">EVIDENCE</p>
            <span>{{ evidenceRefs.length }}</span>
          </div>
          <article v-for="item in evidenceRefs" :key="item.id" class="ref-row">
            <strong>{{ item.title }}</strong>
            <span>{{ item.sourceUri }}:{{ item.lineStart }}</span>
            <p>{{ item.summary }}</p>
          </article>
        </section>

        <section class="summary-block split">
          <div>
            <p class="eyebrow">WIKI</p>
            <strong v-for="item in wikiRefs" :key="item.id">{{ item.title }}</strong>
          </div>
          <div>
            <p class="eyebrow">GRAPH</p>
            <strong v-for="item in entityRefs" :key="item.id">{{ item.name }}</strong>
          </div>
          <div>
            <p class="eyebrow">TIMELINE</p>
            <strong v-for="item in timelineRefs" :key="item.id">{{ item.label }}</strong>
          </div>
        </section>

        <section class="summary-block">
          <div class="section-head">
            <p class="eyebrow">REPLAY CAPSULE</p>
            <span>{{ bundlePreview.replayStepCount || replaySteps.length }} steps</span>
          </div>
          <ol class="replay-list">
            <li v-for="step in replaySteps" :key="step">{{ step }}</li>
          </ol>
          <p v-if="downloadMessage" class="download-message">{{ downloadMessage }}</p>
        </section>
      </aside>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import WorldlineBranchCanvas from '@/components/worldline/WorldlineBranchCanvas.vue'
import { worldlinePublicDemoApi } from '@/apis/worldline_api'

const route = useRoute()
const payload = ref(null)
const selectedNodeId = ref('')
const isLoading = ref(true)
const isBusy = ref(false)
const loadError = ref('')
const downloadMessage = ref('')

const emptyTree = { nodes: [], edges: [], width: 1100, height: 620 }
const shareId = computed(() => String(route.params.shareId || 'demo-branch-evidence').trim())
const worldline = computed(() => payload.value?.worldline || {})
const dataset = computed(() => payload.value?.dataset || {})
const branch = computed(() => payload.value?.branch || {})
const bundlePreview = computed(() => payload.value?.bundlePreview || {})
const branchCount = computed(() => (worldline.value.branches || []).length)
const activeSnapshot = computed(() => ({
  label: payload.value?.readOnly ? 'Read only' : 'Share',
  metric: payload.value?.safety?.status || 'pending'
}))
const evidenceRefs = computed(() => {
  const ids = new Set(branch.value.evidenceIds || [])
  return (worldline.value.evidenceRefs || []).filter((item) => ids.has(item.id) || ids.has(item.evidenceId))
})
const wikiRefs = computed(() => {
  const ids = new Set(branch.value.wikiRefs || [])
  return (worldline.value.wikiRefs || []).filter((item) => ids.has(item.id))
})
const entityRefs = computed(() => {
  const ids = new Set(branch.value.entityRefs || [])
  return (worldline.value.entityRefs || []).filter((item) => ids.has(item.id))
})
const timelineRefs = computed(() => {
  const ids = new Set(branch.value.timelineRefs || [])
  return (worldline.value.timelineRefs || []).filter((item) => ids.has(item.id))
})
const replaySteps = computed(() => payload.value?.worldline?.replayCapsule?.steps || [])
const headerTitle = computed(() => dataset.value.title || 'Worldline Public Share')
const headerSubtitle = computed(
  () => 'Read-only branch share with evidence, graph, timeline, quality gates, and exportable replay capsule.'
)

const selectNode = (nodeId) => {
  selectedNodeId.value = String(nodeId || '')
}

const loadShare = async () => {
  isLoading.value = true
  loadError.value = ''
  try {
    payload.value = await worldlinePublicDemoApi.getBranchShare(shareId.value)
  } catch (error) {
    loadError.value = error?.message || 'Unable to load public branch.'
  } finally {
    isLoading.value = false
  }
}

const saveTextFile = (filename, content, type) => {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

const downloadBundle = async (format) => {
  isBusy.value = true
  downloadMessage.value = ''
  try {
    const result = await worldlinePublicDemoApi.exportEvidenceBundle({ shareId: shareId.value, format })
    if (format === 'markdown') {
      saveTextFile(`worldline-${shareId.value}-evidence-bundle.md`, result, 'text/markdown;charset=utf-8')
    } else {
      saveTextFile(
        `worldline-${shareId.value}-evidence-bundle.json`,
        JSON.stringify(result, null, 2),
        'application/json;charset=utf-8'
      )
    }
    downloadMessage.value = `${format.toUpperCase()} bundle prepared.`
  } catch (error) {
    downloadMessage.value = error?.message || 'Bundle export failed.'
  } finally {
    isBusy.value = false
  }
}

onMounted(loadShare)
watch(shareId, loadShare)
</script>

<style scoped lang="less">
.public-share-view {
  min-height: 100vh;
  padding: 24px;
  color: #e8f8ff;
  background:
    radial-gradient(circle at 14% 18%, rgba(124, 246, 255, 0.14), transparent 26%),
    linear-gradient(135deg, #050b12 0%, #0a121b 48%, #05070b 100%);
}

.share-header,
.share-grid {
  width: min(1480px, 100%);
  margin: 0 auto;
}

.share-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 6px 0 18px;
}

.share-header > div {
  min-width: 0;
}

.eyebrow {
  margin: 0 0 6px;
  color: #ffd98a;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.share-header h1 {
  margin: 0;
  color: #f7fdff;
  font-size: clamp(28px, 4vw, 46px);
  line-height: 1.08;
}

.share-header p {
  max-width: 780px;
  margin: 10px 0 0;
  color: rgba(232, 248, 255, 0.72);
  font-size: 15px;
  line-height: 1.65;
  overflow-wrap: anywhere;
}

.share-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.share-link {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 12px;
  border: 1px solid rgba(124, 246, 255, 0.28);
  border-radius: 8px;
  color: #dffcff;
  background: rgba(9, 18, 28, 0.84);
  font-size: 12px;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
}

.share-link:disabled {
  opacity: 0.55;
  cursor: wait;
}

.share-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 420px);
  gap: 18px;
  align-items: start;
}

.share-stage {
  min-width: 0;
}

.share-panel {
  display: grid;
  gap: 12px;
  min-width: 0;
}

.summary-block,
.share-state {
  border: 1px solid rgba(124, 246, 255, 0.18);
  border-radius: 8px;
  background: rgba(5, 11, 18, 0.78);
  box-shadow: 0 18px 60px rgba(0, 0, 0, 0.28);
}

.summary-block {
  padding: 14px;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.status-pill,
.section-head span {
  color: #081018;
  background: #7cf6ff;
  border-radius: 999px;
  padding: 4px 9px;
  font-size: 11px;
  font-weight: 800;
}

.summary-block h2 {
  margin: 0 0 8px;
  color: #fff7df;
  font-size: 20px;
}

.summary-block p {
  margin: 0;
  color: rgba(232, 248, 255, 0.74);
  line-height: 1.6;
}

.compact-facts {
  display: grid;
  gap: 8px;
  margin: 14px 0 0;
}

.compact-facts div {
  display: grid;
  grid-template-columns: 86px minmax(0, 1fr);
  gap: 8px;
  min-width: 0;
}

.compact-facts dt {
  color: rgba(255, 217, 138, 0.8);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.compact-facts dd {
  min-width: 0;
  margin: 0;
  overflow-wrap: anywhere;
  color: #e8f8ff;
  font-size: 12px;
}

.ref-row {
  padding: 10px 0;
  border-top: 1px solid rgba(124, 246, 255, 0.12);
}

.ref-row:first-of-type {
  border-top: 0;
}

.ref-row strong,
.split strong {
  display: block;
  color: #f7fdff;
  font-size: 13px;
  line-height: 1.45;
}

.ref-row span {
  display: block;
  margin: 4px 0;
  color: rgba(255, 217, 138, 0.82);
  font-size: 11px;
  overflow-wrap: anywhere;
}

.split {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.replay-list {
  display: grid;
  gap: 8px;
  margin: 8px 0 0;
  padding-left: 18px;
  color: rgba(232, 248, 255, 0.78);
  line-height: 1.5;
}

.download-message {
  margin-top: 10px !important;
  color: #7cf6ff !important;
}

.share-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: min(720px, calc(100vw - 32px));
  min-height: 180px;
  margin: 80px auto;
  color: #f7fdff;
}

.share-state.error {
  flex-direction: column;
  color: #ffd7d7;
}

.pulse-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #7cf6ff;
  box-shadow: 0 0 18px rgba(124, 246, 255, 0.8);
}

@media (max-width: 980px) {
  .public-share-view {
    padding: 16px;
  }

  .share-header {
    flex-direction: column;
  }

  .share-actions {
    justify-content: flex-start;
  }

  .share-grid {
    grid-template-columns: 1fr;
  }

  .split {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .public-share-view {
    box-sizing: border-box;
    width: calc(100vw - 56px);
    max-width: calc(100vw - 56px);
    padding: 12px;
    overflow-x: hidden;
  }

  .share-header h1 {
    font-size: 28px;
  }

  .share-header p {
    max-width: 260px;
    font-size: 14px;
  }

  .summary-block p {
    max-width: 250px;
  }

  .share-stage :deep(.stage-subtitle) {
    max-width: 250px;
    font-size: 12px;
    overflow-wrap: anywhere;
  }

  .share-link {
    min-height: 32px;
    padding: 0 10px;
  }

  .compact-facts div {
    grid-template-columns: 1fr;
  }
}
</style>
