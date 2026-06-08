<template>
  <div class="graph-section" v-if="isGraphSupported">
    <div class="graph-container-compact">
      <div v-if="!isGraphSupported" class="graph-disabled">
        <div class="disabled-content">
          <h4>知识图谱不可用</h4>
          <p>当前知识库类型 "{{ kbTypeLabel }}" 不支持知识图谱功能。</p>
          <p>只有 LightRAG 类型的知识库支持知识图谱。</p>
        </div>
      </div>
      <div v-else class="graph-wrapper">
        <template v-if="active">
        <GraphCanvas
          ref="graphRef"
          :graph-data="graph.graphData"
          :graph-info="graphInfoForCanvas"
          @node-click="graph.handleNodeClick"
          @edge-click="graph.handleEdgeClick"
          @canvas-click="graph.handleCanvasClick"
        >
          <template #top>
            <div class="compact-actions">
              <div class="actions-left">
                <a-input
                  v-model:value="searchInput"
                  placeholder="搜索实体"
                  style="width: 240px"
                  @keydown.enter="onSearch"
                  allow-clear
                >
                  <template #suffix>
                    <component
                      :is="graph.fetching ? LoadingOutlined : SearchOutlined"
                      @click="onSearch"
                    />
                  </template>
                </a-input>
                <a-button
                  class="action-btn"
                  :icon="h(ReloadOutlined)"
                  :loading="graph.fetching"
                  @click="loadGraph"
                  title="刷新"
                />
              </div>
              <div class="actions-right">
                <a-button
                  class="action-btn"
                  :icon="h(SettingOutlined)"
                  @click="showSettings = true"
                  title="设置"
                />
              </div>
            </div>
            <div class="graph-brief">
              <div class="brief-left">
                <a-tag :color="graphStatusColor">{{ graphStatusText }}</a-tag>
                <span>节点 {{ visibleNodeCount }} / {{ totalNodeCount }}</span>
                <span>关系 {{ visibleEdgeCount }} / {{ totalEdgeCount }}</span>
              </div>
              <div class="brief-right">
                <span>来源：/api/graph/subgraph</span>
                <span v-if="lastLoadedAt">更新：{{ lastLoadedAt }}</span>
              </div>
            </div>
          </template>
          <template #content>
            <div
              v-if="graphState.visible"
              class="graph-state-card"
              :class="graphState.kind"
              data-graph-interactive="true"
            >
              <span class="state-kicker">{{ graphState.kicker }}</span>
              <h4>{{ graphState.title }}</h4>
              <p>{{ graphState.description }}</p>
              <div class="state-actions">
                <a-button
                  v-if="graphState.canRetry"
                  type="primary"
                  size="small"
                  :loading="graph.fetching"
                  @click="loadGraph"
                >
                  重新读取图谱
                </a-button>
                <a-button size="small" @click="showSettings = true">调整范围</a-button>
              </div>
            </div>
          </template>
        </GraphCanvas>

        <!-- 详情浮动卡片 -->
        <GraphDetailPanel
          :visible="graph.showDetailDrawer"
          :item="graph.selectedItem"
          :type="graph.selectedItemType"
          @close="graph.handleCanvasClick"
          style="top: 50px; right: 10px"
        />
        </template>
      </div>
    </div>

    <!-- 设置模态框 -->
    <a-modal v-model:open="showSettings" title="图谱设置" :footer="null" width="300px">
      <div class="settings-form">
        <a-form layout="vertical">
          <a-form-item label="最大节点数 (limit)">
            <a-input-number
              v-model:value="graphLimit"
              :min="10"
              :max="1000"
              :step="10"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="搜索深度 (depth)">
            <a-input-number
              v-model:value="graphDepth"
              :min="1"
              :max="5"
              :step="1"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item>
            <a-button type="primary" @click="applySettings" style="width: 100%"> 应用 </a-button>
          </a-form-item>
        </a-form>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { computed, defineAsyncComponent, h, nextTick, onUnmounted, reactive, ref, watch } from 'vue'
import { useDatabaseStore } from '@/stores/database'
import {
  ReloadOutlined,
  SettingOutlined,
  SearchOutlined,
  LoadingOutlined
} from '@ant-design/icons-vue'
import GraphDetailPanel from '@/components/GraphDetailPanel.vue'
import { getKbTypeLabel } from '@/utils/kb_utils'
import { unifiedApi } from '@/apis/graph_api'
import { useGraph } from '@/composables/useGraph'

const GraphCanvas = defineAsyncComponent(() => import('@/components/GraphCanvas.vue'))

const props = defineProps({
  active: {
    type: Boolean,
    default: false
  }
})

const store = useDatabaseStore()

const databaseId = computed(() => store.databaseId)
const kbType = computed(() => store.database.kb_type)
const kbTypeLabel = computed(() => getKbTypeLabel(kbType.value || 'lightrag'))

const graphRef = ref(null)
const showSettings = ref(false)
const graphLimit = ref(50)
const graphDepth = ref(2)
const searchInput = ref('')
const graphError = ref('')
const graphStats = ref(null)
const hasLoadedGraph = ref(false)
const lastLoadedAt = ref('')

const graph = reactive(useGraph(graphRef))

// 计算属性：是否支持知识图谱
const isGraphSupported = computed(() => {
  const type = kbType.value?.toLowerCase()
  return type === 'lightrag'
})

const visibleNodeCount = computed(() => graph.graphData.nodes.length)
const visibleEdgeCount = computed(() => graph.graphData.edges.length)
const totalNodeCount = computed(() => graphStats.value?.total_nodes ?? visibleNodeCount.value)
const totalEdgeCount = computed(() => graphStats.value?.total_edges ?? visibleEdgeCount.value)

const graphInfoForCanvas = computed(() => ({
  node_count: totalNodeCount.value,
  edge_count: totalEdgeCount.value
}))

const graphStatusText = computed(() => {
  if (graph.fetching) return '加载中'
  if (graphError.value) return '需处理'
  if (!hasLoadedGraph.value) return '待加载'
  if (visibleNodeCount.value === 0) return '暂无节点'
  return '已加载'
})

const graphStatusColor = computed(() => {
  if (graph.fetching) return 'processing'
  if (graphError.value) return 'warning'
  if (!hasLoadedGraph.value || visibleNodeCount.value === 0) return 'default'
  return 'success'
})

const graphState = computed(() => {
  if (!isGraphSupported.value) {
    return {
      visible: true,
      kind: 'disabled',
      kicker: '当前知识库',
      title: '知识图谱不可用',
      description: `当前知识库类型为 ${kbTypeLabel.value}，只有 LightRAG 知识库支持此处的图谱浏览。`,
      canRetry: false
    }
  }

  if (graph.fetching && visibleNodeCount.value === 0) {
    return {
      visible: true,
      kind: 'loading',
      kicker: '正在联通后端',
      title: '正在读取知识图谱',
      description: `正在通过 /api/graph/subgraph 查询 ${graphLimit.value} 个以内的节点。`,
      canRetry: false
    }
  }

  if (graphError.value) {
    return {
      visible: true,
      kind: 'warning',
      kicker: '后端返回',
      title: '图谱服务暂不可用或处于降级状态',
      description: graphError.value,
      canRetry: true
    }
  }

  if (hasLoadedGraph.value && visibleNodeCount.value === 0) {
    return {
      visible: true,
      kind: 'empty',
      kicker: '暂无图谱节点',
      title: '当前范围没有可展示节点',
      description: '请确认文档已经完成解析和入库，或调整搜索关键词、最大节点数和搜索深度后重新读取。',
      canRetry: true
    }
  }

  return { visible: false }
})

let pendingLoadTimer = null

const loadGraph = async () => {
  if (!databaseId.value || !isGraphSupported.value) return

  graph.fetching = true
  graphError.value = ''
  try {
    const res = await unifiedApi.getSubgraph({
      db_id: databaseId.value,
      node_label: searchInput.value || '*',
      max_nodes: graphLimit.value,
      max_depth: graphDepth.value
    })

    if (res.success && res.data) {
      const data = res.data || {}
      graph.updateGraphData(data.nodes || [], data.edges || [])
      const degradedReason = data.degraded_reason || res.message
      if (data.degraded || data.available === false || res.degraded) {
        graphError.value = degradedReason || '后端图谱服务处于降级状态'
      }
      hasLoadedGraph.value = true
      lastLoadedAt.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
      await loadGraphStats()
    } else {
      throw new Error(res.message || '图谱接口没有返回有效数据')
    }
  } catch (e) {
    console.error('Failed to load graph:', e)
    graph.clearGraph()
    graphError.value = e.message || '加载图谱失败'
    hasLoadedGraph.value = true
  } finally {
    graph.fetching = false
  }
}

const loadGraphStats = async () => {
  if (!databaseId.value || !isGraphSupported.value) return

  try {
    const res = await unifiedApi.getStats(databaseId.value)
    if (res.success && res.data) {
      graphStats.value = res.data
      const degradedReason = res.data.degraded_reason || res.message
      if ((res.data.degraded || res.data.available === false || res.degraded) && !graphError.value) {
        graphError.value = degradedReason || '图谱统计服务处于降级状态'
      }
    }
  } catch (e) {
    console.warn('Failed to load graph stats:', e)
  }
}

const applySettings = () => {
  showSettings.value = false
  loadGraph()
}

const onSearch = () => {
  loadGraph()
}

const scheduleGraphLoad = (delay = 200) => {
  // 确保组件激活且数据库支持图谱功能
  if (!props.active || !isGraphSupported.value || !databaseId.value) {
    return
  }

  if (pendingLoadTimer) {
    clearTimeout(pendingLoadTimer)
  }
  pendingLoadTimer = setTimeout(async () => {
    await nextTick()
    if (props.active && isGraphSupported.value && databaseId.value) {
      await loadGraph()
    }
  }, delay)
}

watch(
  () => props.active,
  (active) => {
    if (active) {
      scheduleGraphLoad()
    }
  },
  { immediate: true }
)

watch(databaseId, () => {
  graph.clearGraph()
  graphError.value = ''
  graphStats.value = null
  hasLoadedGraph.value = false
  lastLoadedAt.value = ''
  if (isGraphSupported.value) {
    scheduleGraphLoad(300)
  }
})

watch(isGraphSupported, (supported) => {
  if (!supported) {
    graph.clearGraph()
    graphError.value = ''
    graphStats.value = null
    hasLoadedGraph.value = false
    lastLoadedAt.value = ''
    return
  }
  scheduleGraphLoad(200)
})

onUnmounted(() => {
  if (pendingLoadTimer) {
    clearTimeout(pendingLoadTimer)
    pendingLoadTimer = null
  }
})
</script>

<style scoped lang="less">
.graph-section {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.graph-container-compact {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  position: relative;
}

.graph-wrapper {
  height: 100%;
  width: 100%;
  position: relative;
}

.compact-actions {
  position: absolute;
  top: 10px;
  left: 10px;
  right: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  pointer-events: none; /* Let clicks pass through empty areas */

  .actions-left,
  .actions-right {
    pointer-events: auto; /* Re-enable clicks for buttons/inputs */
    display: flex;
    align-items: center;
    gap: 4px;
    background: var(--color-trans-light);
    backdrop-filter: blur(4px);
    padding: 2px;
    border-radius: 8px;
    box-shadow: 0 0 4px 0px var(--shadow-2);
  }

  :deep(.ant-input-affix-wrapper) {
    padding: 4px 11px;
    border-radius: 6px;
    border-color: transparent;
    box-shadow: none;
    background: var(--color-trans-light);

    &:hover,
    &:focus,
    &-focused {
      background: var(--main-0);
      border-color: var(--primary-color);
    }

    input {
      background: transparent;
    }
  }

  .action-btn {
    width: 32px;
    height: 32px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    background: transparent;
    color: var(--gray-600);
    border-radius: 6px;
    box-shadow: none;

    &:hover {
      background: rgba(0, 0, 0, 0.05);
      color: var(--primary-color);
    }
  }
}

.graph-brief {
  position: absolute;
  top: 56px;
  left: 10px;
  right: 10px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 10px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(2, 5, 10, 0.72);
  color: var(--wl-muted);
  font-size: 12px;
  line-height: 1.5;
  pointer-events: auto;
  backdrop-filter: blur(8px);

  .brief-left,
  .brief-right {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
  }

  .brief-right {
    justify-content: flex-end;
    color: var(--wl-muted-soft);
  }
}

.graph-state-card {
  position: absolute;
  top: 50%;
  left: 50%;
  width: min(520px, calc(100% - 48px));
  transform: translate(-50%, -50%);
  padding: 18px 20px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background: rgba(2, 5, 10, 0.82);
  color: var(--wl-text);
  box-shadow: var(--wl-shadow-soft);
  pointer-events: auto;
  backdrop-filter: blur(12px);

  .state-kicker {
    color: var(--wl-cyan);
    font-size: 12px;
    font-weight: 800;
  }

  h4 {
    margin: 6px 0 8px;
    color: var(--wl-text);
    font-size: 18px;
    font-weight: 900;
  }

  p {
    margin: 0;
    color: var(--wl-muted);
    font-size: 13px;
    line-height: 1.7;
  }

  .state-actions {
    display: flex;
    gap: 8px;
    margin-top: 14px;
  }

  &.warning {
    border-color: rgba(var(--wl-gold-rgb), 0.42);
    background:
      radial-gradient(circle at 18% 0%, rgba(var(--wl-gold-rgb), 0.12), transparent 38%),
      rgba(2, 5, 10, 0.86);
  }
}

.graph-disabled {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.disabled-content {
  text-align: center;
  color: var(--gray-400);

  h4 {
    margin-bottom: 8px;
  }
}
</style>
