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

    <div class="container-outter">
      <GraphCanvas
        ref="graphRef"
        :graph-data="graph.graphData"
        :graph-info="formattedGraphInfo"
        :highlight-keywords="[state.searchInput]"
        @node-click="graph.handleNodeClick"
        @edge-click="graph.handleEdgeClick"
        @canvas-click="graph.handleCanvasClick"
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
import { computed, onMounted, reactive, ref, h, watch } from 'vue'
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
  const value = route.query.db_id || route.query.knowledge_db_id
  return typeof value === 'string' ? value.trim() : ''
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

const isNeo4j = computed(() => {
  return state.selectedDbId === 'neo4j'
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

  unifiedApi
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

  unifiedApi
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

onMounted(async () => {
  await loadDatabases()
  prefillGraphKeyword()
  if (isNeo4j.value) {
    loadGraphInfo()
  } else {
    loadLightRAGStats()
  }
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
