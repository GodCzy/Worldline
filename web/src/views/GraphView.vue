<template>
  <div class="database-empty" v-if="!state.showPage">
    <a-empty>
      <template #description>
      <span>请先在右上角用户菜单中打开“系统设置”，启用知识图谱后再继续浏览。</span>
      </template>
    </a-empty>
  </div>
  <div class="graph-container layout-container" v-else>
    <HeaderComponent
      title="知识图谱"
      description="查看当前知识库中的图谱结构，也可结合主题闭环继续探索。"
    >
      <template #actions>
        <div class="db-selector">
          <div class="status-wrapper">
            <div class="status-indicator" :class="graphStatusClass"></div>
            <span class="status-text">{{ graphStatusText }}</span>
          </div>
          <span class="label">当前知识库：</span>
          <a-select
            v-model:value="state.selectedDbId"
            style="width: 200px"
            :options="state.dbOptions"
            @change="handleDbChange"
            :loading="state.loadingDatabases"
            mode="combobox"
            placeholder="选择或输入知识库编号"
          />
        </div>
        <!-- <a-button type="default" @click="openLink('http://localhost:7474/')" :icon="h(GlobalOutlined)">
          Neo4j 浏览器
        </a-button> -->
        <a-button v-if="isNeo4j" type="primary" :disabled="isGraphDegraded" @click="state.showModal = true"
          ><UploadOutlined /> 上传知识文件</a-button
        >
        <a-button v-else type="primary" @click="state.showUploadTipModal = true"
          ><UploadOutlined /> 上传知识文件</a-button
        >
        <a-button
          v-if="unindexedCount > 0"
          type="primary"
          @click="indexNodes"
          :loading="state.indexing"
        >
          <SyncOutlined v-if="!state.indexing" /> 为 {{ unindexedCount }} 个节点补建索引
        </a-button>
      </template>
    </HeaderComponent>

    <div v-if="graphAvailabilityMessage" class="graph-state-banner" :class="{ warning: isGraphDegraded }">
      <InfoCircleOutlined />
      <span>{{ graphAvailabilityMessage }}</span>
    </div>

    <div v-if="currentGraphLoop" class="theme-graph-banner">
      <div class="theme-graph-copy">
        <span class="theme-graph-label">当前闭环</span>
        <strong>{{ currentGraphLoop.label }}</strong>
        <span class="theme-graph-detail">
          {{ getWorldlineDisplayLabel(activeThemeId, currentGraphLoop.focus) }} / {{ currentGraphLoop.node_count }} 节点 / {{ currentGraphLoop.edge_count }} 边
        </span>
      </div>
    </div>

    <section
      v-if="showWorldlineGraphReview"
      class="worldline-graph-review"
      data-worldline-graph-review="true"
    >
      <div class="review-header">
        <div class="review-copy">
          <span>Worldline Graph Review</span>
          <strong>{{ reviewStatusText }}</strong>
          <small>{{ state.selectedDbId }}</small>
        </div>
        <div class="review-actions">
          <a-button size="small" :loading="temporalReview.loading" @click="loadWorldlineGraphReview">
            Refresh
          </a-button>
          <a-button
            size="small"
            type="primary"
            :loading="temporalReview.rebuilding"
            @click="rebuildWorldlineGraph"
          >
            Rebuild graph
          </a-button>
        </div>
      </div>

      <a-alert
        v-if="temporalReview.error"
        class="review-alert"
        type="warning"
        show-icon
        :message="temporalReview.error"
      />

      <div
        v-if="graphFocus.hasFocus"
        class="review-focus-card"
        data-worldline-graph-focus-result="true"
      >
        <div class="focus-copy">
          <span>Route focus</span>
          <strong>{{ focusTitle }}</strong>
          <small>{{ focusSubtitle }}</small>
          <div v-if="focusMatches.length" class="focus-match-list">
            <span
              v-for="match in focusMatches.slice(0, 4)"
              :key="`${match.kind}-${match.id || match.label}`"
              :class="match.kind"
            >
              {{ match.kind }} / {{ match.label }}
            </span>
          </div>
        </div>
        <div class="focus-chips">
          <code v-if="graphFocus.entityId">entity {{ shortId(graphFocus.entityId) }}</code>
          <code v-if="graphFocus.factId">fact {{ shortId(graphFocus.factId) }}</code>
          <code v-if="graphFocus.evidenceId">evidence {{ shortId(graphFocus.evidenceId) }}</code>
          <code v-if="focusMatches.length">{{ focusMatches.length }} matched</code>
        </div>
      </div>

      <div class="review-metrics">
        <span><strong>{{ temporalReview.entities.length }}</strong> entities</span>
        <span><strong>{{ temporalReview.relationships.length }}</strong> relations</span>
        <span><strong>{{ temporalReview.timeline.length }}</strong> timeline</span>
        <span :class="{ warning: conflictItems.length > 0 }">
          <strong>{{ conflictItems.length }}</strong> conflicts
        </span>
      </div>

      <div class="review-columns">
        <div class="review-card">
          <div class="review-card-title">
            <span>Temporal conflicts</span>
            <a-tag :color="conflictItems.length ? 'warning' : 'success'">
              {{ conflictItems.length ? 'needs_review' : 'clean' }}
            </a-tag>
          </div>
          <div v-if="!conflictItems.length" class="review-empty">
            No temporal conflict detected for the selected knowledge base.
          </div>
          <article
            v-for="conflict in conflictItems.slice(0, 4)"
            v-else
            :key="conflict.conflict_key || `${conflict.subject}-${conflict.occurred_at}`"
            class="conflict-item"
            :class="{ focused: isConflictFocused(conflict) }"
          >
            <strong>{{ conflict.subject }} / {{ conflict.predicate }}</strong>
            <span>{{ conflict.occurred_at }} - {{ conflict.object_count }} object states</span>
            <div class="id-row">
              <code v-for="factId in (conflict.fact_ids || []).slice(0, 4)" :key="factId">
                {{ shortId(factId) }}
              </code>
            </div>
            <div class="id-row">
              <code v-for="evidenceId in (conflict.evidence_ids || []).slice(0, 4)" :key="evidenceId">
                {{ shortId(evidenceId) }}
              </code>
            </div>
          </article>
        </div>

        <div class="review-card">
          <div class="review-card-title">
            <span>Timeline facts</span>
            <a-tag>{{ reviewTimelineStatus }}</a-tag>
          </div>
          <div v-if="!temporalReview.timeline.length" class="review-empty">
            No timeline fact is available yet. Rebuild graph after parsing and indexing documents.
          </div>
          <article
            v-for="fact in temporalReview.timeline.slice(0, 5)"
            v-else
            :key="fact.fact_id"
            class="timeline-item"
            :class="{ warning: fact.conflict_status === 'needs_review', focused: isTimelineFocused(fact) }"
          >
            <strong>{{ fact.subject }}</strong>
            <span>{{ fact.occurred_at?.slice(0, 10) || 'unknown date' }} / {{ fact.conflict_status || 'clean' }}</span>
            <p>{{ fact.object }}</p>
            <div class="id-row">
              <code v-for="evidenceId in (fact.evidence_ids || []).slice(0, 3)" :key="evidenceId">
                {{ shortId(evidenceId) }}
              </code>
            </div>
          </article>
        </div>
      </div>
    </section>

    <div class="container-outter">
      <GraphCanvas
        ref="graphRef"
        :graph-data="graph.graphData"
        :graph-info="formattedGraphInfo"
        :highlight-keywords="focusHighlightKeywords"
        @node-click="graph.handleNodeClick"
        @edge-click="graph.handleEdgeClick"
        @canvas-click="graph.handleCanvasClick"
        @data-rendered="applyRouteFocusToCanvas"
      >
        <template #top>
          <div class="actions">
            <div class="actions-left">
            <a-input
              v-model:value="state.searchInput"
              placeholder="输入要查询的实体，* 表示全部"
              style="width: 300px"
              @keydown.enter="onSearch"
              allow-clear
            >
              <template #suffix>
                <component
                  :is="state.searchLoading ? LoadingOutlined : SearchOutlined"
                  @click="onSearch"
                />
              </template>
            </a-input>
              <a-input
                v-model:value="sampleNodeCount"
                placeholder="查询数量"
                style="width: 100px"
                @keydown.enter="loadSampleNodes"
                :loading="graph.fetching"
              >
                <template #suffix>
                  <component
                    :is="graph.fetching ? LoadingOutlined : ReloadOutlined"
                    @click="loadSampleNodes"
                  />
                </template>
              </a-input>
            </div>
            <div class="actions-right">
              <a-button type="default" @click="exportGraphData" :icon="h(ExportOutlined)">
                导出当前图谱
              </a-button>
            </div>
          </div>
        </template>
        <template #content>
          <a-empty
            v-show="graph.graphData.nodes.length === 0"
            class="graph-empty-state"
            style="padding: 4rem 0"
            data-graph-interactive="true"
          >
            <template #description>
              <span>{{ graphEmptyDescription }}</span>
            </template>
            <div class="graph-empty-actions">
              <a-button :loading="graph.fetching" @click="loadSampleNodes">重新读取图谱</a-button>
              <a-button v-if="!isNeo4j" type="primary" @click="goToDatabasePage">
                前往知识库页面
              </a-button>
              <a-button v-else type="primary" :disabled="isGraphDegraded" @click="state.showModal = true">
                上传 JSONL 图谱文件
              </a-button>
            </div>
          </a-empty>
        </template>
      </GraphCanvas>
      <!-- 详情浮动卡片 -->
      <GraphDetailPanel
        :visible="graph.showDetailDrawer"
        :item="graph.selectedItem"
        :type="graph.selectedItemType"
        :nodes="graph.graphData.nodes"
        @close="graph.handleCanvasClick"
        style="width: 380px"
      />
    </div>

    <a-modal
      :open="state.showModal"
      title="上传知识文件"
      @ok="addDocumentByFile"
      @cancel="handleModalCancel"
      ok-text="添加到知识图谱"
      cancel-text="取消"
      :confirm-loading="state.processing"
      :ok-button-props="{ disabled: !hasValidFile }"
    >
      <div class="upload">
        <div class="note">
          <p>上传的 JSONL 文件需符合知识图谱导入格式，字段结构可参考项目文档中的导入说明。</p>
        </div>
        <div class="upload-config">
          <div class="config-row">
            <label class="config-label">嵌入模型</label>
            <div class="config-field">
              <EmbeddingModelSelector
                v-model:value="state.embedModelName"
                :disabled="!embedModelConfigurable"
                :style="{ width: '100%' }"
              />
            </div>
          </div>
          <div v-if="!embedModelConfigurable" class="config-hint-row">
            * 当前知识库已有数据或已设定模型，不可更改
          </div>
          <div class="config-row">
            <label class="config-label">批处理大小</label>
            <div class="config-field">
              <a-input-number
                v-model:value="state.batchSize"
                :min="1"
                :max="1000"
                style="width: 100%"
              />
            </div>
          </div>
          <div class="config-hint-row">默认值：40，范围：1-1000</div>
        </div>
        <a-upload-dragger
          class="upload-dragger"
          v-model:fileList="fileList"
          name="file"
          :fileList="fileList"
          :max-count="1"
          accept=".jsonl"
          action="/api/knowledge/files/upload?allow_jsonl=true"
          :headers="getAuthHeaders()"
          @change="handleFileUpload"
          @drop="handleDrop"
        >
          <p class="ant-upload-text">点击或者把文件拖拽到这里上传</p>
          <p class="ant-upload-hint">目前仅支持上传 jsonl 文件。</p>
        </a-upload-dragger>
      </div>
    </a-modal>

    <!-- 上传提示弹窗 -->
    <a-modal
      :open="state.showUploadTipModal"
      title="知识图谱上传方式说明"
      @cancel="() => (state.showUploadTipModal = false)"
      :footer="null"
      width="500px"
    >
      <div class="upload-tip-content">
        <a-alert
          :message="getUploadTipMessage()"
          type="info"
          show-icon
          style="margin-bottom: 16px"
        />
        <div v-if="!isNeo4j" class="upload-tip-actions">
          <p>如需把文档上传到当前选中的知识库，请前往对应的知识库详情页面进行操作：</p>
          <div class="action-buttons">
            <a-button type="primary" @click="goToDatabasePage">
              <DatabaseOutlined /> 前往知识库页面
            </a-button>
          </div>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref, h, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { useConfigStore } from '@/stores/config'
import {
  UploadOutlined,
  SyncOutlined,
  GlobalOutlined,
  InfoCircleOutlined,
  SearchOutlined,
  ReloadOutlined,
  LoadingOutlined,
  HighlightOutlined,
  DatabaseOutlined,
  ExportOutlined
} from '@ant-design/icons-vue'
import HeaderComponent from '@/components/HeaderComponent.vue'
import { neo4jApi, unifiedApi } from '@/apis/graph_api'
import { worldlineApi } from '@/apis/worldline_api'
import { useUserStore } from '@/stores/user'
import GraphCanvas from '@/components/GraphCanvas.vue'
import GraphDetailPanel from '@/components/GraphDetailPanel.vue'
import EmbeddingModelSelector from '@/components/EmbeddingModelSelector.vue'
import { useGraph } from '@/composables/useGraph'
import { useThemeContextStore } from '@/stores/themeContext'
import {
  getWorldlineDisplayLabel,
  getWorldlineGraphDefaultKeyword,
  getWorldlineGraphLoopById
} from '@/data/worldline'
import {
  buildGraphFocusMatches,
  findCanvasFocusNodeId as resolveCanvasFocusNodeId,
  focusHighlightKeywords as buildFocusHighlightKeywords,
  getFocusDisplay,
  isConflictFocused as isGraphConflictFocused,
  isEntityFocused as isGraphEntityFocused,
  isTimelineFocused as isGraphTimelineFocused,
  parseGraphFocusQuery,
  queryValue
} from '@/utils/worldlineGraphFocus'

const configStore = useConfigStore()
const cur_embed_model = computed(() => configStore.config?.embed_model)
const modelMatched = computed(
  () =>
    !graphInfo?.value?.embed_model_name ||
    graphInfo.value.embed_model_name === cur_embed_model.value
)

const router = useRouter()
const route = useRoute()
const graphRef = ref(null)
const graphInfo = ref(null)
const fileList = ref([])
const sampleNodeCount = ref(100)
const themeContextStore = useThemeContextStore()
const activeThemeId = computed(() => themeContextStore.activeContext?.theme || '')
const routeDbId = computed(() => {
  return queryValue(route.query.db_id || route.query.knowledge_db_id)
})

const graph = reactive(useGraph(graphRef))

const state = reactive({
  loadingGraphInfo: false,
  loadingDatabases: false,
  searchInput: '',
  searchLoading: false,
  showModal: false,
  showInfoModal: false,
  showUploadTipModal: false,
  processing: false,
  indexing: false,
  showPage: true,
  selectedDbId: 'neo4j',
  dbOptions: [],
  lightragStats: null,
  graphError: '',
  embedModelName: '',
  batchSize: 40
})

const temporalReview = reactive({
  loading: false,
  rebuilding: false,
  error: '',
  entities: [],
  relationships: [],
  timeline: [],
  conflictReport: null
})

const isNeo4j = computed(() => {
  return state.selectedDbId === 'neo4j'
})

const showWorldlineGraphReview = computed(() => Boolean(state.selectedDbId && !isNeo4j.value))

const conflictItems = computed(() => temporalReview.conflictReport?.items || [])

const graphFocus = computed(() => parseGraphFocusQuery(route.query))

const isEntityFocused = (entity = {}) => isGraphEntityFocused(entity, graphFocus.value)
const isTimelineFocused = (fact = {}) => isGraphTimelineFocused(fact, graphFocus.value)
const isConflictFocused = (conflict = {}) => isGraphConflictFocused(conflict, graphFocus.value)

const focusedEntities = computed(() =>
  temporalReview.entities.filter((entity) => isEntityFocused(entity))
)

const focusMatches = computed(() =>
  buildGraphFocusMatches({
    focus: graphFocus.value,
    entities: temporalReview.entities,
    relationships: temporalReview.relationships,
    timeline: temporalReview.timeline,
    conflicts: conflictItems.value
  })
)

const focusDisplay = computed(() => getFocusDisplay(graphFocus.value, focusMatches.value))
const focusTitle = computed(() => focusDisplay.value.title)
const focusSubtitle = computed(() => focusDisplay.value.subtitle)

const focusHighlightKeywords = computed(() =>
  buildFocusHighlightKeywords({
    searchInput: state.searchInput,
    focus: graphFocus.value,
    focusedEntities: focusedEntities.value
  })
)

const reviewStatusText = computed(() => {
  if (temporalReview.loading) return 'Loading graph evidence'
  if (temporalReview.error) return 'Review unavailable'
  if (conflictItems.value.length) return 'Temporal conflicts need review'
  if (temporalReview.timeline.length) return 'Temporal graph is clean'
  return 'Waiting for graph rebuild'
})

const reviewTimelineStatus = computed(() => {
  if (!temporalReview.timeline.length) return 'empty'
  return conflictItems.value.length ? 'needs_review' : 'clean'
})

const selectedGraphOption = computed(() =>
  state.dbOptions.find((db) => db.value === state.selectedDbId)
)

const isGraphDegraded = computed(() => {
  if (state.graphError) return true
  if (selectedGraphOption.value?.degraded || selectedGraphOption.value?.available === false) return true
  if (isNeo4j.value) return graphInfo.value?.degraded || graphInfo.value?.available === false
  return state.lightragStats?.degraded || state.lightragStats?.available === false
})

const graphAvailabilityMessage = computed(() => {
  const reason =
    state.graphError ||
    graphInfo.value?.degraded_reason ||
    state.lightragStats?.degraded_reason ||
    selectedGraphOption.value?.degraded_reason

  if (reason) return reason
  if (isGraphDegraded.value) return '当前图谱服务处于降级状态'
  return ''
})

const graphEmptyDescription = computed(() => {
  if (graph.fetching) return '正在读取图谱节点，请稍候。'
  if (graphAvailabilityMessage.value) return graphAvailabilityMessage.value
  if (state.loadingDatabases) return '正在读取可用图谱列表。'
  if (state.dbOptions.length === 0) return '当前没有可用图谱，请先创建或接入知识库。'
  if (!isNeo4j.value) {
    return '当前知识库暂未生成可展示节点，请先完成文档上传、解析和入库，或调整查询关键词。'
  }
  return '当前没有可展示的图谱节点，可以上传 JSONL 图谱文件或调整查询数量后重新读取。'
})

const currentGraphLoop = computed(() =>
  getWorldlineGraphLoopById(activeThemeId.value, themeContextStore.activeContext?.graph || '')
)
const defaultGraphKeyword = computed(() =>
  getWorldlineGraphDefaultKeyword(activeThemeId.value, currentGraphLoop.value)
)

const embedModelConfigurable = computed(() => {
  return graphInfo.value?.embed_model_configurable ?? true
})

// 检查是否有有效的已上传文件
const hasValidFile = computed(() => {
  return fileList.value.some((file) => file.status === 'done' && file.response?.file_path)
})

// 计算未索引节点数量
const unindexedCount = computed(() => {
  return graphInfo.value?.unindexed_node_count || 0
})

const formattedGraphInfo = computed(() => {
  if (isNeo4j.value) {
    return {
      node_count: graphInfo.value?.entity_count || 0,
      edge_count: graphInfo.value?.relationship_count || 0
    }
  } else {
    return {
      node_count: state.lightragStats?.total_nodes || 0,
      edge_count: state.lightragStats?.total_edges || 0
    }
  }
})

const loadDatabases = async () => {
  state.loadingDatabases = true
  try {
    const res = await unifiedApi.getGraphs()
    if (res.success && res.data) {
      state.dbOptions = res.data.map((db) => ({
        label: `${db.name} (${db.type})`,
        value: db.id,
        type: db.type,
        status: db.status,
        available: db.available,
        degraded: db.degraded,
        degraded_reason: db.degraded_reason
      }))

      if (routeDbId.value && state.dbOptions.find((o) => o.value === routeDbId.value)) {
        state.selectedDbId = routeDbId.value
      }

      // If no selection or invalid selection, select first
      if (!state.selectedDbId || !state.dbOptions.find((o) => o.value === state.selectedDbId)) {
        if (state.dbOptions.length > 0) {
          state.selectedDbId = state.dbOptions[0].value
        }
      }
    }
  } catch (error) {
    console.error('Failed to load databases:', error)
    state.graphError = error.message || '图谱列表加载失败'
  } finally {
    state.loadingDatabases = false
  }
}

const handleDbChange = () => {
  // Clear current data
  graph.clearGraph()
  state.searchInput = ''
  state.lightragStats = null
  state.graphError = ''
  prefillGraphKeyword()

  if (isNeo4j.value) {
    loadGraphInfo()
  } else {
    // Also load stats for LightRAG or KB
    loadLightRAGStats()
  }
  loadWorldlineGraphReview()
  loadSampleNodes()
}

const loadLightRAGStats = () => {
  unifiedApi
    .getStats(state.selectedDbId)
    .then((res) => {
      if (res.success) {
        state.lightragStats = res.data
        state.graphError = res.data?.degraded_reason || ''
      }
    })
    .catch((e) => {
      console.error(e)
      state.graphError = e.message || '图谱统计加载失败'
    })
}

const loadWorldlineGraphReview = async () => {
  if (!showWorldlineGraphReview.value) return

  temporalReview.loading = true
  temporalReview.error = ''
  try {
    const [entities, relationships, conflicts, timeline] = await Promise.all([
      worldlineApi.listGraphEntities(state.selectedDbId, { limit: 80 }),
      worldlineApi.listGraphRelationships(state.selectedDbId, { limit: 120 }),
      worldlineApi.listGraphConflicts(state.selectedDbId, { limit: 80 }),
      worldlineApi.listTimeline(state.selectedDbId, { limit: 80 })
    ])
    temporalReview.entities = entities?.items || []
    temporalReview.relationships = relationships?.items || []
    temporalReview.conflictReport = conflicts || { items: [], conflict_count: 0, status: 'clean' }
    temporalReview.timeline = timeline?.items || []
    await applyRouteFocusToCanvas()
  } catch (error) {
    console.error('Failed to load Worldline graph review:', error)
    temporalReview.entities = []
    temporalReview.relationships = []
    temporalReview.conflictReport = { items: [], conflict_count: 0, status: 'error' }
    temporalReview.timeline = []
    temporalReview.error = error?.response?.data?.detail || error.message || 'Worldline graph review failed'
  } finally {
    temporalReview.loading = false
  }
}

const rebuildWorldlineGraph = async () => {
  if (!showWorldlineGraphReview.value) return

  temporalReview.rebuilding = true
  temporalReview.error = ''
  try {
    await worldlineApi.rebuildGraph(state.selectedDbId, { max_entities: 40 })
    message.success('Worldline graph rebuilt')
    await loadWorldlineGraphReview()
    loadSampleNodes()
  } catch (error) {
    console.error('Failed to rebuild Worldline graph:', error)
    temporalReview.error = error?.response?.data?.detail || error.message || 'Worldline graph rebuild failed'
  } finally {
    temporalReview.rebuilding = false
  }
}

const shortId = (value = '') => {
  const text = String(value || '')
  if (text.length <= 18) return text
  return `${text.slice(0, 8)}...${text.slice(-6)}`
}

const prefillGraphKeyword = () => {
  if (!state.searchInput && defaultGraphKeyword.value) {
    state.searchInput = defaultGraphKeyword.value
  }
}

const loadGraphInfo = () => {
  state.loadingGraphInfo = true
  neo4jApi
    .getInfo()
    .then((data) => {
      console.log(data)
      graphInfo.value = data.data
      state.graphError = graphInfo.value?.degraded_reason || ''
      if (graphInfo.value?.embed_model_name) {
        state.embedModelName = graphInfo.value.embed_model_name
      } else {
        // Default if not set (though backend usually sends default)
        state.embedModelName = cur_embed_model.value
      }
      state.loadingGraphInfo = false
    })
    .catch((error) => {
      console.error(error)
      graphInfo.value = {
        status: 'unavailable',
        available: false,
        degraded: true,
        degraded_reason: error.message || '图数据库信息加载失败'
      }
      state.graphError = graphInfo.value.degraded_reason
      state.loadingGraphInfo = false
    })
}

const addDocumentByFile = () => {
  // 使用计算属性验证文件
  if (!hasValidFile.value) {
    message.error('请先等待文件上传完成')
    return
  }

  if (!state.embedModelName) {
    message.error('请选择嵌入模型')
    return
  }

  state.processing = true

  // 获取已上传的文件路径
  const uploadedFile = fileList.value.find(
    (file) => file.status === 'done' && file.response?.file_path
  )
  const filePath = uploadedFile?.response?.file_path

  // 再次验证文件路径
  if (!filePath) {
    message.error('文件路径获取失败，请重新上传文件')
    state.processing = false
    return
  }

  neo4jApi
    .addEntities(filePath, 'neo4j', state.embedModelName, state.batchSize)
    .then((data) => {
      if (data.status === 'success') {
        message.success(data.message)
        state.showModal = false
        // 清空文件列表
        fileList.value = []
        // 刷新图谱数据
        setTimeout(() => {
          loadGraphInfo()
          loadSampleNodes()
        }, 500)
      } else {
        throw new Error(data.message)
      }
    })
    .catch((error) => {
      console.error(error)
      message.error(error.message || '添加文件失败')
    })
    .finally(() => (state.processing = false))
}

const loadSampleNodes = () => {
  graph.fetching = true
  state.graphError = ''

  return unifiedApi
    .getSubgraph({
      db_id: state.selectedDbId,
      node_label: '*',
      max_nodes: sampleNodeCount.value
    })
    .then((data) => {
      // Normalize data structure if needed
      const result = data.data || {}
      state.graphError = result.degraded_reason || data.message || ''
      graph.updateGraphData(result.nodes || [], result.edges || [])
      console.log(graph.graphData)
    })
    .catch((error) => {
      console.error(error)
      state.graphError = error.message || '图谱节点加载失败'
      graph.updateGraphData([], [])
    })
    .finally(() => (graph.fetching = false))
}

const findCanvasFocusNodeId = () => {
  return resolveCanvasFocusNodeId({
    nodes: graph.graphData.nodes || [],
    focus: graphFocus.value,
    focusedEntities: focusedEntities.value
  })
}

const applyRouteFocusToCanvas = async () => {
  if (!graphRef.value) return
  await nextTick()

  if (!graphFocus.value.hasFocus) {
    if (graphRef.value.clearFocus) await graphRef.value.clearFocus()
    return
  }

  const nodeId = findCanvasFocusNodeId()
  if (graphRef.value.clearFocus) await graphRef.value.clearFocus()
  if (nodeId && graphRef.value.focusNode) {
    await graphRef.value.focusNode(nodeId)
  }
}

const onSearch = () => {
  if (state.searchLoading) {
    message.error('请稍后再试')
    return
  }

  if (isNeo4j.value && graphInfo?.value?.embed_model_name !== cur_embed_model.value) {
    // 可选：提示模型不一致
  }

  state.searchLoading = true
  state.graphError = ''

  return unifiedApi
    .getSubgraph({
      db_id: state.selectedDbId,
      node_label: state.searchInput || '*',
      max_nodes: sampleNodeCount.value
    })
    .then((data) => {
      const result = data.data || {}
      if (!result || !result.nodes || !result.edges) {
        throw new Error('返回数据格式不正确')
      }
      state.graphError = result.degraded_reason || data.message || ''
      graph.updateGraphData(result.nodes, result.edges)
      if (result.degraded) {
        message.warning(result.degraded_reason || '当前图谱服务处于降级状态')
      } else if (graph.graphData.nodes.length === 0) {
        message.info('未找到相关实体')
      }
      console.log(data)
      console.log(graph.graphData)
    })
    .catch((error) => {
      console.error('查询错误:', error)
      state.graphError = error.message || '图谱查询失败'
      message.error(`查询出错：${error.message || '未知错误'}`)
    })
    .finally(() => (state.searchLoading = false))
}

watch(
  () => route.query,
  () => {
    themeContextStore.syncFromRoute(route)
  },
  { immediate: true, deep: true }
)

watch(
  currentGraphLoop,
  () => {
    prefillGraphKeyword()
  },
  { immediate: true }
)

watch(routeDbId, (dbId) => {
  if (!dbId || dbId === state.selectedDbId) return
  state.selectedDbId = dbId
  handleDbChange()
})

watch(
  () => [
    graphFocus.value.entityId,
    graphFocus.value.factId,
    graphFocus.value.evidenceId,
    graphFocus.value.label,
    graphFocus.value.layer
  ],
  () => {
    applyRouteFocusToCanvas()
  }
)

onMounted(async () => {
  await loadDatabases()
  prefillGraphKeyword()
  if (isNeo4j.value) {
    loadGraphInfo()
  } else {
    loadLightRAGStats()
  }
  await loadWorldlineGraphReview()
  loadSampleNodes()
})

const handleFileUpload = ({ file, fileList: newFileList }) => {
  // 更新文件列表
  fileList.value = newFileList

  // 如果上传失败，显示错误信息
  if (file.status === 'error') {
    message.error(`文件上传失败: ${file.name}`)
  }

  // 如果上传成功，显示成功信息
  if (file.status === 'done' && file.response?.file_path) {
    message.success(`文件上传成功: ${file.name}`)
  }

  console.log('File upload status:', file.status, file.name)
  console.log('File list:', fileList.value)
}

const handleDrop = (event) => {
  console.log(event)
  console.log(fileList.value)
}

const handleModalCancel = () => {
  state.showModal = false
  // 重置文件列表
  fileList.value = []
}

const graphStatusClass = computed(() => {
  if (state.loadingGraphInfo) return 'loading'
  if (isGraphDegraded.value) return 'warning'
  if (!isNeo4j.value) return state.lightragStats ? 'open' : 'closed'
  return graphInfo.value?.status === 'open' ? 'open' : 'closed'
})

const graphStatusText = computed(() => {
  if (state.loadingGraphInfo) return '加载中'
  if (isGraphDegraded.value) return '服务降级'
  if (!isNeo4j.value) return state.lightragStats ? '已加载' : '待加载'
  return graphInfo.value?.status === 'open' ? '已连接' : '已关闭'
})

// 为未索引节点添加索引
const indexNodes = () => {
  // 判断 embed_model_name 是否相同
  if (!modelMatched.value) {
    message.error(
      `向量模型不匹配，无法添加索引，当前向量模型为 ${cur_embed_model.value}，图数据库向量模型为 ${graphInfo.value?.embed_model_name}`
    )
    return
  }

  if (state.processing) {
    message.error('后台正在处理，请稍后再试')
    return
  }

  state.indexing = true
  neo4jApi
    .indexEntities('neo4j')
    .then((data) => {
      message.success(data.message || '索引添加成功')
      // 刷新图谱信息
      loadGraphInfo()
    })
    .catch((error) => {
      console.error(error)
      message.error(error.message || '添加索引失败')
    })
    .finally(() => {
      state.indexing = false
    })
}

const exportGraphData = () => {
  const dataStr = JSON.stringify(
    {
      nodes: graph.graphData.nodes,
      edges: graph.graphData.edges,
      graphInfo: isNeo4j.value ? graphInfo.value : state.lightragStats,
      source: state.selectedDbId,
      exportTime: new Date().toISOString()
    },
    null,
    2
  )

  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `graph-data-${state.selectedDbId}-${new Date().toISOString().slice(0, 10)}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  message.success('图谱数据已导出')
}

const getAuthHeaders = () => {
  const userStore = useUserStore()
  return userStore.getAuthHeaders()
}

const openLink = (url) => {
  window.open(url, '_blank')
}

const getDatabaseName = () => {
  const selectedDb = state.dbOptions.find((db) => db.value === state.selectedDbId)
  return selectedDb ? selectedDb.label : state.selectedDbId
}

const getUploadTipMessage = () => {
  if (isNeo4j.value) {
    return 'Neo4j 图数据库支持通过上传 JSONL 文件直接导入实体与关系数据。'
  } else {
    const selectedDb = state.dbOptions.find((db) => db.value === state.selectedDbId)
    const dbType = selectedDb?.type || '未知'
    const dbName = selectedDb?.label || getDatabaseName()
    return `当前选择的是 ${dbType.toUpperCase()} 类型的知识库“${dbName}”。这类知识库需要在文档知识库页面上传文档，系统会自动从中提取知识图谱。`
  }
}

const goToDatabasePage = () => {
  state.showUploadTipModal = false

  // 如果不是 Neo4j，需要找到对应的知识库 ID 并跳转
  if (!isNeo4j.value) {
    const selectedDb = state.dbOptions.find((db) => db.value === state.selectedDbId)
    if (selectedDb && selectedDb.type !== 'neo4j') {
      // 跳转到对应的知识库详情页面
      router.push(`/database/${state.selectedDbId}`)
    } else {
      // 如果找不到对应的数据库，跳转到数据库列表页面
      router.push('/database')
    }
  }
}
</script>

<style lang="less" scoped>
@graph-header-height: 55px;

.database-empty {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 24px;
  background: var(--wl-page-bg);
  color: var(--wl-muted);

  :deep(.ant-empty-description) {
    color: var(--wl-muted);
  }
}

.graph-container {
  padding: 0;
  min-height: 100vh;
  background: var(--wl-page-bg);
  color: var(--wl-text);

  :deep(.header-container) {
    height: @graph-header-height;
  }

  :deep(.header-actions) {
    align-items: center;
    flex-wrap: wrap;
  }

  :deep(.ant-select-selector),
  :deep(.ant-input-affix-wrapper),
  :deep(.ant-input),
  :deep(.ant-input-number) {
    border-color: var(--wl-border) !important;
    border-radius: var(--wl-radius-sm) !important;
    background: rgba(2, 5, 10, 0.74) !important;
    color: var(--wl-text) !important;
    box-shadow: none !important;
  }

  :deep(.ant-select-selection-item),
  :deep(.ant-select-selection-placeholder),
  :deep(.ant-input),
  :deep(.ant-input-number-input) {
    color: var(--wl-text) !important;
  }

  :deep(.ant-select-arrow),
  :deep(.ant-input-suffix) {
    color: var(--wl-cyan);
  }

  :deep(.ant-btn) {
    border-radius: var(--wl-radius-sm);
    font-weight: 800;
    box-shadow: none;
  }

  :deep(.ant-btn-default) {
    border-color: var(--wl-border);
    background: rgba(var(--wl-cyan-rgb), 0.06);
    color: var(--wl-text-soft);
  }

  :deep(.ant-btn-default:hover) {
    border-color: var(--wl-border-strong);
    background: rgba(var(--wl-cyan-rgb), 0.1);
    color: var(--wl-text);
  }

  :deep(.ant-btn-primary) {
    border-color: var(--wl-border-gold);
    background: linear-gradient(135deg, rgba(var(--wl-gold-rgb), 0.92), rgba(var(--wl-cyan-rgb), 0.7));
    color: var(--wl-ink);
  }
}

.theme-graph-banner {
  display: flex;
  align-items: center;
  padding: 14px 24px;
  border-bottom: 1px solid var(--wl-border);
  background:
    radial-gradient(circle at 16% 0%, rgba(var(--wl-gold-rgb), 0.14), transparent 34%),
    linear-gradient(90deg, rgba(7, 15, 24, 0.9), rgba(2, 5, 10, 0.84));
}

.graph-state-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 12px 24px 0;
  padding: 12px 14px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.07);
  color: var(--wl-text-soft);
  font-size: 13px;
  line-height: 1.5;

  &.warning {
    border-color: rgba(var(--wl-gold-rgb), 0.38);
    background: rgba(var(--wl-gold-rgb), 0.1);
    color: var(--wl-gold-soft);
  }
}

.theme-graph-copy {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  color: var(--wl-muted);

  strong {
    color: var(--wl-text);
    font-weight: 900;
  }
}

.theme-graph-label {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.24);
  border-radius: 999px;
  background: rgba(var(--wl-gold-rgb), 0.1);
  color: var(--wl-gold-soft);
  font-size: 12px;
  font-weight: 700;
}

.theme-graph-detail {
  color: var(--wl-muted-soft);
  font-size: 13px;
}

.worldline-graph-review {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 12px 24px 0;
  padding: 14px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background:
    radial-gradient(circle at 12% 0%, rgba(var(--wl-cyan-rgb), 0.12), transparent 32%),
    rgba(2, 5, 10, 0.78);
}

.review-header,
.review-actions,
.review-card-title,
.id-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.review-header {
  justify-content: space-between;
}

.review-copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 3px;

  span {
    color: var(--wl-muted);
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
  }

  strong {
    color: var(--wl-text);
    font-size: 15px;
  }

  small {
    color: var(--wl-muted-soft);
    overflow-wrap: anywhere;
  }
}

.review-actions {
  flex-wrap: wrap;
  justify-content: flex-end;
}

.review-alert {
  border-radius: var(--wl-radius-sm);
}

.review-focus-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.34);
  border-radius: var(--wl-radius-sm);
  background:
    radial-gradient(circle at 0% 0%, rgba(var(--wl-gold-rgb), 0.14), transparent 38%),
    rgba(7, 15, 24, 0.74);
  padding: 10px 12px;
}

.focus-copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 3px;

  span {
    color: var(--wl-gold);
    font-size: 11px;
    font-weight: 900;
    text-transform: uppercase;
  }

  strong {
    color: var(--wl-text);
    font-size: 14px;
    overflow-wrap: anywhere;
  }

  small {
    color: var(--wl-muted-soft);
    overflow-wrap: anywhere;
  }
}

.focus-chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 6px;
  min-width: 0;

  code {
    max-width: 100%;
    border: 1px solid rgba(var(--wl-gold-rgb), 0.24);
    border-radius: 6px;
    padding: 3px 6px;
    background: rgba(2, 5, 10, 0.86);
    color: var(--wl-gold-soft);
    font-size: 11px;
    overflow-wrap: anywhere;
  }
}

.focus-match-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;

  span {
    max-width: 100%;
    border: 1px solid rgba(var(--wl-cyan-rgb), 0.18);
    border-radius: 6px;
    padding: 3px 6px;
    background: rgba(var(--wl-cyan-rgb), 0.07);
    color: var(--wl-text-soft);
    font-size: 11px;
    font-weight: 800;
    overflow-wrap: anywhere;
  }

  .conflict {
    border-color: rgba(var(--wl-gold-rgb), 0.28);
    background: rgba(var(--wl-gold-rgb), 0.08);
    color: var(--wl-gold-soft);
  }

  .relationship {
    border-color: rgba(142, 154, 255, 0.26);
    background: rgba(142, 154, 255, 0.08);
    color: #d7dcff;
  }

  .timeline {
    border-color: rgba(var(--wl-cyan-rgb), 0.24);
    background: rgba(var(--wl-cyan-rgb), 0.1);
  }
}

.review-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;

  span {
    min-width: 0;
    border: 1px solid rgba(var(--wl-cyan-rgb), 0.16);
    border-radius: var(--wl-radius-sm);
    padding: 8px 10px;
    background: rgba(7, 15, 24, 0.72);
    color: var(--wl-muted);
    font-size: 12px;
  }

  strong {
    color: var(--wl-cyan);
    font-size: 16px;
  }

  .warning strong {
    color: var(--wl-amber);
  }
}

.review-columns {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 12px;
}

.review-card {
  min-width: 0;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(7, 15, 24, 0.62);
  padding: 12px;
}

.review-card-title {
  justify-content: space-between;
  margin-bottom: 10px;

  span {
    color: var(--wl-text);
    font-weight: 800;
  }
}

.review-empty,
.conflict-item,
.timeline-item {
  color: var(--wl-muted);
  font-size: 12px;
  line-height: 1.5;
}

.conflict-item,
.timeline-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  border-top: 1px solid rgba(var(--wl-cyan-rgb), 0.1);
  padding-top: 10px;

  & + & {
    margin-top: 10px;
  }

  strong {
    color: var(--wl-text-soft);
    overflow-wrap: anywhere;
  }

  span,
  p {
    margin: 0;
    overflow-wrap: anywhere;
  }

  &.warning strong {
    color: var(--wl-gold-soft);
  }

  &.focused {
    border-top-color: rgba(var(--wl-gold-rgb), 0.42);
    border-radius: 6px;
    background: rgba(var(--wl-gold-rgb), 0.09);
    padding: 10px;
  }
}

.id-row {
  flex-wrap: wrap;

  code {
    max-width: 100%;
    border: 1px solid rgba(var(--wl-cyan-rgb), 0.18);
    border-radius: 6px;
    padding: 2px 5px;
    background: rgba(2, 5, 10, 0.86);
    color: var(--wl-cyan);
    font-size: 11px;
    overflow-wrap: anywhere;
  }
}

.db-selector {
  display: flex;
  align-items: center;

  .label {
    font-size: 14px;
    margin-right: 8px;
    color: var(--wl-muted);
  }
}

.status-wrapper {
  display: flex;
  align-items: center;
  margin-right: 16px;
  font-size: 14px;
  color: var(--wl-muted);
}

.status-text {
  margin-left: 8px;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;

  &.loading {
    background-color: var(--wl-amber);
    animation: pulse 1.5s infinite ease-in-out;
  }

  &.open {
    background-color: var(--wl-green);
    box-shadow: 0 0 12px rgba(112, 240, 187, 0.55);
  }

  &.closed {
    background-color: var(--wl-red);
  }

  &.warning {
    background-color: var(--wl-amber);
    box-shadow: 0 0 12px rgba(255, 207, 103, 0.45);
  }
}

@keyframes pulse {
  0% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.2);
    opacity: 1;
  }
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
}

@media (max-width: 768px) {
  .graph-container {
    :deep(.header-container) {
      height: auto;
      padding: 10px 12px;
    }

    :deep(.header-content) {
      align-items: stretch;
      flex-direction: column;
      gap: 10px;
    }

    :deep(.header-title) {
      min-width: 0;
    }

    :deep(.header-title h1) {
      white-space: nowrap;
    }

    :deep(.header-title p) {
      display: none;
    }

    :deep(.header-actions) {
      width: 100%;
      align-items: stretch;
      flex-direction: column;
    }
  }

  .db-selector {
    width: 100%;
    align-items: stretch;
    flex-direction: column;
    gap: 7px;

    .label {
      margin-right: 0;
    }

    :deep(.ant-select) {
      width: 100% !important;
    }
  }

  .status-wrapper {
    margin-right: 0;
  }

  .theme-graph-banner {
    padding: 12px 16px;
  }

  .theme-graph-copy {
    align-items: flex-start;
    flex-direction: column;
    gap: 8px;
  }

  .worldline-graph-review {
    margin: 10px 12px 0;
    padding: 12px;
  }

  .review-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .review-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .review-focus-card {
    flex-direction: column;
  }

  .focus-chips {
    justify-content: flex-start;
  }

  .review-metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .review-columns {
    grid-template-columns: 1fr;
  }

  .container-outter {
    height: calc(100vh - 210px);
    min-height: 520px;

    .actions {
      align-items: stretch;
      flex-direction: column;
      gap: 10px;
      margin: 12px 0;
      padding: 0 12px;
    }
  }

  .actions {
    .actions-left,
    .actions-right {
      width: 100%;
      align-items: stretch;
      flex-direction: column;
    }

    :deep(.ant-input-affix-wrapper),
    :deep(.ant-input) {
      width: 100% !important;
    }
  }
}

.upload {
  margin-bottom: 20px;

  .upload-dragger {
    margin: 0px;
  }

  .upload-config {
    margin: 24px 0;
    padding: 16px;
    border: 1px solid var(--wl-border);
    background: rgba(2, 5, 10, 0.72);
    border-radius: var(--wl-radius-sm);

    .config-row {
      display: flex;
      align-items: center;
      margin-bottom: 16px;

      &:last-of-type {
        margin-bottom: 0;
      }

      .config-label {
        width: 100px;
        flex-shrink: 0;
        font-size: 14px;
        color: var(--wl-muted);
        text-align: right;
        margin-right: 16px;
      }

      .config-field {
        flex: 1;
        min-width: 0;
      }
    }

    .config-hint-row {
      margin-bottom: 16px;
      padding-left: 116px;
      font-size: 12px;
      color: var(--wl-muted-soft);
      line-height: 1.5;

      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

.container-outter {
  width: 100%;
  height: calc(100vh - @graph-header-height);
  overflow: hidden;
  background:
    linear-gradient(rgba(var(--wl-cyan-rgb), 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(var(--wl-cyan-rgb), 0.035) 1px, transparent 1px),
    radial-gradient(circle at 18% 22%, rgba(var(--wl-gold-rgb), 0.1), transparent 28%),
    radial-gradient(circle at 84% 52%, rgba(var(--wl-cyan-rgb), 0.12), transparent 32%),
    var(--wl-bg-0);
  background-size:
    38px 38px,
    38px 38px,
    auto,
    auto,
    auto;

  .actions {
    display: flex;
    justify-content: space-between;
    margin: 20px 0;
    padding: 0 24px;
    width: 100%;
  }

  .tags {
    display: flex;
    gap: 8px;
  }
}

.actions {
  top: 0;

  .actions-left,
  .actions-right {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  :deep(.ant-input) {
    padding: 2px 0px;
  }

  button {
    height: 37px;
    box-shadow: none;
  }

  :deep(.ant-input),
  :deep(.ant-input-affix-wrapper),
  :deep(.ant-input-number),
  :deep(.ant-select-selector) {
    border-color: var(--wl-border) !important;
    border-radius: var(--wl-radius-sm) !important;
    background: rgba(2, 5, 10, 0.74) !important;
    color: var(--wl-text) !important;
    box-shadow: none !important;
  }

  :deep(.ant-input::placeholder),
  :deep(.ant-input-number-input::placeholder) {
    color: var(--wl-muted-soft);
  }

  :deep(.ant-input-affix-wrapper-focused),
  :deep(.ant-input-affix-wrapper:focus),
  :deep(.ant-input-affix-wrapper:hover),
  :deep(.ant-input:hover),
  :deep(.ant-select-selector:hover) {
    border-color: var(--wl-border-strong) !important;
  }

  :deep(.ant-input-suffix) {
    color: var(--wl-cyan);
  }

  :deep(.ant-btn) {
    border-radius: var(--wl-radius-sm);
    font-weight: 800;
  }

  :deep(.ant-btn-default) {
    border-color: var(--wl-border);
    background: rgba(var(--wl-cyan-rgb), 0.06);
    color: var(--wl-text-soft);
  }

  :deep(.ant-btn-default:hover) {
    border-color: var(--wl-border-strong);
    background: rgba(var(--wl-cyan-rgb), 0.1);
    color: var(--wl-text);
  }

  :deep(.ant-btn-primary) {
    border-color: var(--wl-border-gold);
    background: linear-gradient(135deg, rgba(var(--wl-gold-rgb), 0.92), rgba(var(--wl-cyan-rgb), 0.7));
    color: var(--wl-ink);
  }

  :deep(.ant-empty-description) {
    color: var(--wl-muted);
  }
}

.graph-empty-state {
  pointer-events: auto;

  :deep(.ant-empty-description) {
    max-width: 560px;
    margin: 0 auto;
    color: var(--wl-muted);
    line-height: 1.7;
  }
}

.graph-empty-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 16px;
}

.upload-tip-content {
  .upload-tip-actions {
    p {
      margin-bottom: 16px;
      color: var(--color-text-secondary);
    }
  }

  .action-buttons {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}
</style>
