<template>
  <div class="dashboard-container layout-container wl-ant-dark">
    <!-- 顶部状态条 -->

    <!-- 现代化顶部统计栏 -->
    <div class="modern-stats-header">
      <StatusBar />
      <StatsOverviewComponent :basic-stats="basicStats" />
    </div>

    <div class="dashboard-intro">
      <strong>运营总览</strong>
      <p>这里集中展示平台运行、智能体使用、知识库使用和近期对话概况。</p>
    </div>

    <!-- Grid布局的主要内容区域 -->
    <div class="dashboard-grid">
      <!-- 调用统计模块 - 占据2x1网格 -->
      <CallStatsComponent :loading="loading" ref="callStatsRef" />

      <!-- 用户活跃度分析 - 占据1x1网格 -->
      <div class="grid-item user-stats">
        <UserStatsComponent
          :user-stats="allStatsData?.users"
          :loading="loading"
          ref="userStatsRef"
        />
      </div>

      <!-- 智能体使用情况 - 占据1x1网格 -->
      <div class="grid-item agent-stats">
        <AgentStatsComponent
          :agent-stats="allStatsData?.agents"
          :loading="loading"
          ref="agentStatsRef"
        />
      </div>

      <!-- 工具使用情况 - 占据1x1网格 -->
      <div class="grid-item tool-stats">
        <ToolStatsComponent
          :tool-stats="allStatsData?.tools"
          :loading="loading"
          ref="toolStatsRef"
        />
      </div>

      <!-- 知识库使用情况 - 占据1x1网格 -->
      <div class="grid-item knowledge-stats">
        <KnowledgeStatsComponent
          :knowledge-stats="allStatsData?.knowledge"
          :loading="loading"
          ref="knowledgeStatsRef"
        />
      </div>

      <!-- 近期对话 - 占据1x1网格 -->
      <div class="grid-item conversations">
        <a-card class="conversations-section" title="近期对话" :loading="loading">
          <template #extra>
            <a-space>
              <a-input
                v-model:value="filters.user_id"
                placeholder="输入用户编号"
                size="small"
                style="width: 120px"
                @change="handleFilterChange"
              />
              <a-select
                v-model:value="filters.status"
                placeholder="选择状态"
                size="small"
                style="width: 100px"
                @change="handleFilterChange"
              >
                <a-select-option value="active">活跃</a-select-option>
                <a-select-option value="deleted">已删除</a-select-option>
                <a-select-option value="all">全部</a-select-option>
              </a-select>
              <a-button size="small" @click="loadConversations" :loading="loading"> 重新加载 </a-button>
              <a-button size="small" @click="feedbackModal.show()"> 查看反馈 </a-button>
            </a-space>
          </template>

          <a-table
            :columns="conversationColumns"
            :data-source="conversations"
            :loading="loading"
            :pagination="conversationPagination"
            @change="handleTableChange"
            row-key="thread_id"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'title'">
                <a
                  @click="handleViewDetail(record)"
                  class="conversation-title"
                  :class="{ loading: loadingDetail }"
                  >{{ record.title || '未命名对话' }}</a
                >
              </template>
              <template v-if="column.key === 'status'">
                <a-tag :color="record.status === 'active' ? 'green' : 'red'" size="small">
                  {{ record.status === 'active' ? '活跃' : '已删除' }}
                </a-tag>
              </template>
              <template v-if="column.key === 'updated_at'">
                <span class="time-text">{{ formatDate(record.updated_at) }}</span>
              </template>
              <template v-if="column.key === 'actions'">
                <a-button
                  type="link"
                  size="small"
                  @click="handleViewDetail(record)"
                  :loading="loadingDetail"
                >
                  详情
                </a-button>
              </template>
            </template>
          </a-table>
        </a-card>
      </div>
    </div>

    <!-- 反馈模态框 -->
    <FeedbackModalComponent ref="feedbackModal" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { message } from 'ant-design-vue'
import { dashboardApi } from '@/apis/dashboard_api'
import dayjs, { parseToShanghai } from '@/utils/time'

// 导入子组件
import StatusBar from '@/components/StatusBar.vue'
import UserStatsComponent from '@/components/dashboard/UserStatsComponent.vue'
import ToolStatsComponent from '@/components/dashboard/ToolStatsComponent.vue'
import KnowledgeStatsComponent from '@/components/dashboard/KnowledgeStatsComponent.vue'
import AgentStatsComponent from '@/components/dashboard/AgentStatsComponent.vue'
import CallStatsComponent from '@/components/dashboard/CallStatsComponent.vue'
import StatsOverviewComponent from '@/components/dashboard/StatsOverviewComponent.vue'
import FeedbackModalComponent from '@/components/dashboard/FeedbackModalComponent.vue'

// 组件引用
const feedbackModal = ref(null)

// 统计数据 - 使用新的响应式结构
const basicStats = ref({})
const allStatsData = ref({
  users: null,
  tools: null,
  knowledge: null,
  agents: null
})

// 过滤器
const filters = reactive({
  user_id: '',
  agent_id: '',
  status: 'active'
})

// 对话列表
const conversations = ref([])
const loading = ref(false)
const loadingDetail = ref(false)

// 调用统计子组件引用
const callStatsRef = ref(null)

// 分页
const conversationPagination = reactive({
  current: 1,
  pageSize: 8,
  total: 0,
  showSizeChanger: false,
  showQuickJumper: false,
  showTotal: (total, range) => `${range[0]}-${range[1]} / ${total}`
})

// 表格列定义
const conversationColumns = [
  {
    title: '对话标题',
    dataIndex: 'title',
    key: 'title',
    ellipsis: true
  },
  {
    title: '用户编号',
    dataIndex: 'user_id',
    key: 'user_id',
    width: '80px',
    ellipsis: true
  },
  {
    title: '消息数',
    dataIndex: 'message_count',
    key: 'message_count',
    width: '60px',
    align: 'center'
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: '70px',
    align: 'center'
  },
  {
    title: '更新时间',
    dataIndex: 'updated_at',
    key: 'updated_at',
    width: '120px'
  },
  {
    title: '操作',
    key: 'actions',
    width: '60px',
    align: 'center'
  }
]

// 子组件引用
const userStatsRef = ref(null)
const toolStatsRef = ref(null)
const knowledgeStatsRef = ref(null)
const agentStatsRef = ref(null)

// 加载统计数据 - 使用并行API调用
const loadAllStats = async () => {
  loading.value = true
  try {
    // 使用并行API调用获取所有统计数据
    const response = await dashboardApi.getAllStats()

    // 更新基础统计数据
    basicStats.value = response.basic

    // 更新详细统计数据
    allStatsData.value = {
      users: response.users,
      tools: response.tools,
      knowledge: response.knowledge,
      agents: response.agents
    }

    console.log('Dashboard 数据加载完成:', response)
  } catch (error) {
    console.error('加载统计数据失败:', error)
    message.error('加载统计数据失败')

    // 如果并行请求失败，尝试单独加载基础数据
    try {
      const basicResponse = await dashboardApi.getStats()
      basicStats.value = basicResponse
      message.warning('详细数据加载失败，仅显示基础统计')
    } catch (basicError) {
      console.error('加载基础统计数据也失败:', basicError)
      message.error('无法加载任何统计数据')
    }
  } finally {
    loading.value = false
  }
}

// 保留原有的loadStats函数以兼容旧代码
const loadStats = loadAllStats

// 加载对话列表
const loadConversations = async () => {
  try {
    const params = {
      user_id: filters.user_id || undefined,
      agent_id: filters.agent_id || undefined,
      status: filters.status,
      limit: conversationPagination.pageSize,
      offset: (conversationPagination.current - 1) * conversationPagination.pageSize
    }

    const response = await dashboardApi.getConversations(params)
    conversations.value = response
    // Note: 由于后端没有返回总数，这里暂时设置为当前数据长度
    conversationPagination.total = response.length
  } catch (error) {
    console.error('加载对话列表失败:', error)
    message.error('加载对话列表失败')
  }
}

// 日期格式化
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const parsed = parseToShanghai(dateString)
  if (!parsed) return '-'
  const now = dayjs().tz('Asia/Shanghai')
  const diffDays = now.startOf('day').diff(parsed.startOf('day'), 'day')

  if (diffDays === 0) {
    return parsed.format('HH:mm')
  }
  if (diffDays === 1) {
    return '昨天'
  }
  if (diffDays < 7) {
    return `${diffDays}天前`
  }
  return parsed.format('MM-DD')
}

// 查看对话详情
const handleViewDetail = async (record) => {
  try {
    loadingDetail.value = true
    const detail = await dashboardApi.getConversationDetail(record.thread_id)
    console.log(detail)
  } catch (error) {
    console.error('获取对话详情失败:', error)
    message.error('获取对话详情失败')
  } finally {
    loadingDetail.value = false
  }
}

// 处理过滤器变化
const handleFilterChange = () => {
  conversationPagination.current = 1
  loadConversations()
}

// 处理表格变化
const handleTableChange = (pag) => {
  conversationPagination.current = pag.current
  conversationPagination.pageSize = pag.pageSize
  loadConversations()
}

// 清理函数 - 清理所有子组件的图表实例
const cleanupCharts = () => {
  if (userStatsRef.value?.cleanup) userStatsRef.value.cleanup()
  if (toolStatsRef.value?.cleanup) toolStatsRef.value.cleanup()
  if (knowledgeStatsRef.value?.cleanup) knowledgeStatsRef.value.cleanup()
  if (agentStatsRef.value?.cleanup) agentStatsRef.value.cleanup()
  if (callStatsRef.value?.cleanup) callStatsRef.value.cleanup()
}

// 初始化
onMounted(() => {
  loadAllStats()
  loadConversations()
})

// 组件卸载时清理图表
onUnmounted(() => {
  cleanupCharts()
})
</script>

<style scoped lang="less">
.dashboard-container {
  // padding: 0 24px 24px 24px;
  --gray-0: #061017;
  --gray-10: #08131c;
  --gray-15: #091822;
  --gray-25: #061017;
  --gray-50: #0a1a24;
  --gray-100: rgba(124, 246, 255, 0.1);
  --gray-120: rgba(124, 246, 255, 0.12);
  --gray-150: rgba(124, 246, 255, 0.15);
  --gray-200: rgba(124, 246, 255, 0.2);
  --gray-500: #7f9aa6;
  --gray-600: var(--wl-muted);
  --gray-700: var(--wl-text-soft);
  --gray-800: var(--wl-text);
  --gray-900: var(--wl-text);
  --gray-1000: var(--wl-text);
  --main-color: var(--wl-cyan);
  --main-0: rgba(var(--wl-cyan-rgb), 0.02);
  --main-20: rgba(var(--wl-cyan-rgb), 0.08);
  --main-50: rgba(var(--wl-cyan-rgb), 0.14);
  --main-300: rgba(var(--wl-cyan-rgb), 0.35);
  --main-500: var(--wl-cyan);
  --main-600: var(--wl-cyan);
  --main-700: var(--wl-text);
  --main-900: var(--wl-text);
  background-color: var(--wl-page-bg);
  color: var(--wl-text);
  min-height: calc(100vh - 64px);
  overflow-x: hidden;
}

.dashboard-intro {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0 16px 4px;

  strong {
    color: var(--gray-900);
    font-size: 16px;
    font-weight: 600;
  }

  p {
    margin: 0;
    color: var(--gray-600);
    font-size: 13px;
    line-height: 1.6;
  }
}

.dashboard-container :deep(.ant-card),
.dashboard-container :deep(.dashboard-card),
.conversations-section,
.call-stats-section {
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background: var(--wl-panel);
  color: var(--wl-text);
  box-shadow: var(--wl-shadow-soft);
}

.dashboard-container :deep(.ant-card-head),
.conversations-section :deep(.ant-card-head),
.call-stats-section :deep(.ant-card-head) {
  border-bottom-color: var(--wl-border);
  background: rgba(var(--wl-cyan-rgb), 0.035);
}

.dashboard-container :deep(.ant-card-head-title),
.dashboard-container :deep(.ant-card-body),
.dashboard-container :deep(.ant-table),
.dashboard-container :deep(.ant-table-cell),
.dashboard-container :deep(.ant-empty-description) {
  color: var(--wl-text);
  background: transparent;
}

.dashboard-container :deep(.stat-card),
.dashboard-container :deep(.mini-stat-card),
.dashboard-container :deep(.summary-card) {
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background:
    linear-gradient(145deg, rgba(var(--wl-cyan-rgb), 0.07), rgba(var(--wl-gold-rgb), 0.035)),
    var(--wl-panel);
  color: var(--wl-text);
  box-shadow: none;
}

.dashboard-container :deep(.stat-icon),
.dashboard-container :deep(.placeholder-icon) {
  border: 1px solid var(--wl-border);
  background: rgba(var(--wl-cyan-rgb), 0.08) !important;
  color: var(--wl-cyan) !important;
}

.dashboard-container :deep(.stat-value),
.dashboard-container :deep(.mini-stat-value),
.dashboard-container :deep(.summary-value),
.dashboard-container :deep(.chart-title),
.dashboard-container :deep(.placeholder-text) {
  color: var(--wl-text);
}

.dashboard-container :deep(.stat-label),
.dashboard-container :deep(.mini-stat-label),
.dashboard-container :deep(.summary-label),
.dashboard-container :deep(.chart-subtitle),
.dashboard-container :deep(.placeholder-subtitle),
.dashboard-container :deep(.time-text) {
  color: var(--wl-muted);
}

.dashboard-container :deep(.compact-chart-container),
.dashboard-container :deep(.chart-container) {
  border-color: var(--wl-border);
  background: rgba(var(--wl-cyan-rgb), 0.025);
}

.dashboard-container :deep(.stats-overview) {
  color: var(--wl-text);
}

.dashboard-container :deep(.ant-statistic-title) {
  color: var(--wl-muted);
  font-size: 13px;
  font-weight: 700;
}

.dashboard-container :deep(.ant-statistic-content) {
  color: var(--wl-text);
}

.dashboard-container :deep(.ant-divider) {
  border-color: var(--wl-border);
}

.dashboard-container :deep(.ant-table-wrapper),
.dashboard-container :deep(.ant-table-container),
.dashboard-container :deep(.ant-table-content),
.dashboard-container :deep(.ant-table-thead > tr > th),
.dashboard-container :deep(.ant-table-tbody > tr > td) {
  background: transparent;
  color: var(--wl-text-soft);
  border-color: var(--wl-border);
}

.dashboard-container :deep(.ant-table-thead > tr > th) {
  background: rgba(var(--wl-cyan-rgb), 0.06);
  color: var(--wl-text);
  font-weight: 800;
}

.dashboard-container :deep(.ant-table-tbody > tr:hover > td) {
  background: rgba(var(--wl-cyan-rgb), 0.055);
}

.dashboard-container :deep(.ant-table-placeholder:hover > td) {
  background: transparent;
}

.dashboard-container :deep(.ant-pagination),
.dashboard-container :deep(.ant-pagination-total-text),
.dashboard-container :deep(.ant-pagination-item a) {
  color: var(--wl-muted);
}

.dashboard-container :deep(.ant-pagination-item),
.dashboard-container :deep(.ant-pagination-prev .ant-pagination-item-link),
.dashboard-container :deep(.ant-pagination-next .ant-pagination-item-link) {
  border-color: var(--wl-border);
  background: rgba(var(--wl-cyan-rgb), 0.045);
  color: var(--wl-text-soft);
}

.dashboard-container :deep(.ant-pagination-item-active) {
  border-color: var(--wl-border-gold);
  background: rgba(var(--wl-gold-rgb), 0.12);
}

.dashboard-container :deep(.ant-input),
.dashboard-container :deep(.ant-select-selector),
.dashboard-container :deep(.ant-btn) {
  border-color: var(--wl-border);
  background: rgba(var(--wl-cyan-rgb), 0.045);
  color: var(--wl-text-soft);
}

.dashboard-container :deep(.ant-input::placeholder),
.dashboard-container :deep(.ant-select-selection-placeholder) {
  color: rgba(148, 172, 184, 0.72);
}

.dashboard-container :deep(.ant-input:hover),
.dashboard-container :deep(.ant-input:focus),
.dashboard-container :deep(.ant-select-selector:hover),
.dashboard-container :deep(.ant-btn:hover) {
  border-color: var(--wl-border-strong);
  color: var(--wl-text);
}

.dashboard-container :deep(.ant-btn-link) {
  border-color: transparent;
  background: transparent;
  color: var(--wl-cyan-soft);
}

.dashboard-container :deep(.ant-card-loading-content),
.dashboard-container :deep(.ant-card-loading-block) {
  background: linear-gradient(90deg, rgba(var(--wl-cyan-rgb), 0.05), rgba(var(--wl-cyan-rgb), 0.12), rgba(var(--wl-cyan-rgb), 0.05));
}

:global(.wl-ant-dark .ant-select-dropdown),
:global(.wl-ant-dark .ant-dropdown-menu) {
  border: 1px solid var(--wl-border);
  background: #07131d;
  color: var(--wl-text);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.52);
}

:global(.wl-ant-dark .ant-select-item),
:global(.wl-ant-dark .ant-dropdown-menu-item) {
  color: var(--wl-text-soft);
}

:global(.wl-ant-dark .ant-select-item-option-active),
:global(.wl-ant-dark .ant-select-item-option-selected),
:global(.wl-ant-dark .ant-dropdown-menu-item:hover) {
  background: rgba(var(--wl-cyan-rgb), 0.08);
  color: var(--wl-text);
}

// Dashboard 特有的网格布局
.dashboard-grid {
  display: grid;
  padding: 16px;
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: auto auto;
  gap: 16px;
  margin-bottom: 24px;
  min-height: 600px;

  .grid-item {
    border-radius: 8px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    min-height: 300px;
    background-color: transparent;
    border: none;
    transition: all 0.2s ease;

    &:hover {
      .conversations-section,
      .call-stats-section {
        border-color: var(--gray-200);
        box-shadow: 0 1px 3px 0 var(--shadow-100);
      }
    }

    // 大页面布局：第一行 2x1 + 1x1，第二行 3x1x1
    &.call-stats {
      grid-column: 1 / 3;
      grid-row: 1 / 2;
      min-height: 400px;
    }

    &.user-stats {
      grid-column: 3 / 4;
      grid-row: 1 / 2;
      min-height: 400px;
    }

    &.agent-stats {
      grid-column: 1 / 2;
      grid-row: 2 / 3;
      min-height: 350px;
    }

    &.tool-stats {
      grid-column: 2 / 3;
      grid-row: 2 / 3;
      min-height: 350px;
    }

    &.knowledge-stats {
      grid-column: 3 / 4;
      grid-row: 2 / 3;
      min-height: 350px;
    }

    &.conversations {
      grid-column: 1 / 4;
      grid-row: 3 / 4;
      min-height: 300px;
    }
  }
}

// Dashboard 特有的卡片样式
.conversations-section,
.call-stats-section {
  background-color: var(--gray-0);
  border: 1px solid var(--gray-200);
  border-radius: 12px;
  transition: all 0.2s ease;
  box-shadow: none;

  &:hover {
    background-color: var(--gray-25);
    border-color: var(--gray-200);
    box-shadow: 0 1px 3px 0 var(--shadow-100);
  }

  :deep(.ant-card-head) {
    border-bottom: 1px solid var(--gray-200);
    min-height: 56px;
    padding: 0 20px;
    background-color: var(--gray-0);

    .ant-card-head-title {
      font-size: 16px;
      font-weight: 600;
      color: var(--gray-1000);
    }
  }

  :deep(.ant-card-body) {
    padding: 16px 20px;
    background-color: var(--gray-0);
  }

  :deep(.ant-card-extra) {
    .ant-space {
      gap: 8px;
    }
  }
}

// Dashboard 特有的占位符样式
.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--gray-600);

  .placeholder-icon {
    width: 64px;
    height: 64px;
    background-color: var(--gray-100);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;

    .icon {
      width: 32px;
      height: 32px;
      color: var(--gray-500);
    }
  }

  .placeholder-text {
    font-size: 18px;
    font-weight: 600;
    color: var(--gray-800);
    margin-bottom: 8px;
  }

  .placeholder-subtitle {
    font-size: 14px;
    color: var(--gray-600);
  }
}

// Dashboard 特有的对话记录样式
.conversations-section {
  .conversation-title {
    color: var(--main-500);
    text-decoration: none;
    font-weight: 500;
    font-size: 13px;
    transition: color 0.2s ease;

    &:hover {
      color: var(--main-600);
      text-decoration: underline;
    }
  }

  .time-text {
    color: var(--gray-600);
    font-size: 12px;
  }
}

// 调用统计模块样式
.call-stats-section {
  .call-stats-container {
    .call-summary {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 24px;

      .summary-card {
        background: linear-gradient(135deg, var(--gray-50) 0%, var(--gray-100) 100%);
        border: 1px solid var(--gray-200);
        border-radius: 8px;
        padding: 12px;
        text-align: center;

        .summary-value {
          font-size: 16px;
          font-weight: 600;
          color: var(--gray-800);
          margin-bottom: 4px;
        }

        .summary-label {
          font-size: 11px;
          color: var(--gray-500);
          font-weight: 500;
        }
      }
    }

    .chart-container {
      .chart {
        width: 100%;
        height: 280px;
        border-radius: 8px;
        overflow: hidden;
      }
    }
  }

  :deep(.ant-card-extra) {
    .ant-space {
      gap: 8px;
    }
  }
}

// Dashboard 特有的响应式设计
@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto auto;
    gap: 16px;

    .grid-item {
      // 小页面布局：第一行 2x1，第二行和第三行各是 2x1x1
      &.call-stats {
        grid-column: 1 / 3;
        grid-row: 1 / 2;
        min-height: 350px;
      }

      &.user-stats {
        grid-column: 1 / 2;
        grid-row: 2 / 3;
        min-height: 300px;
      }

      &.agent-stats {
        grid-column: 2 / 3;
        grid-row: 2 / 3;
        min-height: 300px;
      }

      &.tool-stats {
        grid-column: 1 / 2;
        grid-row: 3 / 4;
        min-height: 300px;
      }

      &.knowledge-stats {
        grid-column: 2 / 3;
        grid-row: 3 / 4;
        min-height: 300px;
      }

      &.conversations {
        grid-column: 1 / 3;
        grid-row: 4 / 5;
        min-height: 300px;
      }
    }
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
  }

  .dashboard-intro {
    padding: 0 0 8px;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
    gap: 12px;

    .grid-item {
      &.call-stats,
      &.agent-stats,
      &.user-stats,
      &.tool-stats,
      &.knowledge-stats,
      &.conversations {
        grid-column: 1 / 2;
        grid-row: auto;
        min-height: 300px;
      }
    }
  }

  .call-stats-section {
    .call-stats-container {
      .call-summary {
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;

        .summary-card {
          padding: 12px;

          .summary-value {
            font-size: 18px;
          }

          .summary-label {
            font-size: 11px;
          }
        }
      }

      .chart-container {
        .chart {
          height: 200px;
        }
      }
    }
  }

  .placeholder-content {
    height: 150px;

    .placeholder-icon {
      width: 48px;
      height: 48px;
      margin-bottom: 12px;

      .icon {
        width: 24px;
        height: 24px;
      }
    }

    .placeholder-text {
      font-size: 16px;
    }

    .placeholder-subtitle {
      font-size: 12px;
    }
  }
}
</style>
