<template>
  <div class="extensions-view">
    <div class="extensions-header">
      <a-tabs v-model:activeKey="activeTab" class="extensions-tabs">
        <a-tab-pane key="tools" tab="工具" />
        <a-tab-pane key="skills" tab="Skills 管理" />
        <a-tab-pane key="mcp" tab="MCP 服务器" />
      </a-tabs>
      <div class="header-actions">
        <!-- Skills Tab 的按钮 -->
        <template v-if="activeTab === 'skills'">
          <a-upload
            accept=".zip"
            :show-upload-list="false"
            :custom-request="handleImportUpload"
            :disabled="skillsLoading || skillsImporting"
          >
            <a-button type="primary" :loading="skillsImporting" class="lucide-icon-btn">
              <Upload :size="14" />
              <span>导入 ZIP</span>
            </a-button>
          </a-upload>
          <a-button @click="handleSkillsRefresh" :disabled="skillsLoading" class="lucide-icon-btn">
            <RotateCw :size="14" />
            <span>刷新</span>
          </a-button>
        </template>
        <!-- Tools Tab 的按钮 -->
        <template v-else-if="activeTab === 'tools'">
          <a-button @click="handleToolsRefresh" :disabled="toolsLoading" class="lucide-icon-btn">
            <RotateCw :size="14" />
            <span>刷新</span>
          </a-button>
        </template>
        <!-- MCP Tab 的按钮 -->
        <template v-else-if="activeTab === 'mcp'">
          <a-button type="primary" @click="handleMcpAdd" class="lucide-icon-btn">
            <Plus :size="14" />
            <span>添加服务器</span>
          </a-button>
          <a-button @click="handleMcpRefresh" :disabled="mcpLoading" class="lucide-icon-btn">
            <RotateCw :size="14" />
            <span>刷新</span>
          </a-button>
        </template>
      </div>
    </div>

    <div class="extensions-content">
      <div v-show="activeTab === 'tools'" class="tab-panel">
        <ToolsManagerComponent ref="toolsRef" @refresh="handleToolsRefresh" />
      </div>
      <div v-show="activeTab === 'skills'" class="tab-panel">
        <SkillsManagerComponent
          ref="skillsRef"
          @import="handleSkillsImport"
          @refresh="handleSkillsRefresh"
        />
      </div>
      <div v-show="activeTab === 'mcp'" class="tab-panel">
        <McpServersComponent ref="mcpRef" @add="handleMcpAdd" @refresh="handleMcpRefresh" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Upload, RotateCw, Plus } from 'lucide-vue-next'
import SkillsManagerComponent from '@/components/SkillsManagerComponent.vue'
import ToolsManagerComponent from '@/components/ToolsManagerComponent.vue'
import McpServersComponent from '@/components/McpServersComponent.vue'

const route = useRoute()
const activeTab = ref('tools')
const skillsRef = ref(null)

// 监听路由 query 参数变化
watch(
  () => route.query,
  (query) => {
    if (query.tab && ['tools', 'skills', 'mcp'].includes(query.tab)) {
      activeTab.value = query.tab
    }
  },
  { immediate: true }
)
const toolsRef = ref(null)
const mcpRef = ref(null)

// Skills 相关状态（从子组件透传）
const skillsLoading = ref(false)
const skillsImporting = ref(false)
const toolsLoading = ref(false)
const mcpLoading = ref(false)

// 暴露给子组件的状态更新
const updateSkillsState = (loading, importing) => {
  skillsLoading.value = loading
  skillsImporting.value = importing
}

const updateToolsState = (loading) => {
  toolsLoading.value = loading
}

const updateMcpState = (loading) => {
  mcpLoading.value = loading
}

// Skills 事件处理
const handleSkillsImport = () => {
  // 导入完成后自动刷新
  handleSkillsRefresh()
}

const handleSkillsRefresh = () => {
  if (skillsRef.value?.fetchSkills) {
    updateSkillsState(true, skillsImporting.value)
    skillsRef.value.fetchSkills().finally(() => {
      updateSkillsState(false, skillsImporting.value)
    })
  }
}

// Tools 事件处理
const handleToolsRefresh = () => {
  if (toolsRef.value?.fetchTools) {
    updateToolsState(true)
    toolsRef.value.fetchTools().finally(() => {
      updateToolsState(false)
    })
  }
}

// MCP 事件处理
const handleMcpAdd = () => {
  if (mcpRef.value?.showAddModal) {
    mcpRef.value.showAddModal()
  }
}

const handleMcpRefresh = () => {
  if (mcpRef.value?.fetchServers) {
    updateMcpState(true)
    mcpRef.value.fetchServers().finally(() => {
      updateMcpState(false)
    })
  }
}

// 处理导入上传
const handleImportUpload = async ({ file, onSuccess, onError }) => {
  if (skillsRef.value?.handleImportUpload) {
    updateSkillsState(skillsLoading.value, true)
    try {
      await skillsRef.value.handleImportUpload({ file, onSuccess, onError })
      handleSkillsImport()
    } catch (e) {
      onError?.(e)
    } finally {
      updateSkillsState(skillsLoading.value, false)
    }
  }
}
</script>

<style scoped lang="less">
.extensions-view {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  --gray-0: #061017;
  --gray-10: #08131c;
  --gray-25: #061017;
  --gray-50: #0a1a24;
  --gray-100: rgba(124, 246, 255, 0.1);
  --gray-150: rgba(124, 246, 255, 0.15);
  --gray-200: rgba(124, 246, 255, 0.2);
  --gray-500: #7f9aa6;
  --gray-600: var(--wl-muted);
  --gray-700: var(--wl-text-soft);
  --gray-800: var(--wl-text);
  --gray-900: var(--wl-text);
  --gray-1000: var(--wl-text);
  --main-color: var(--wl-cyan);
  --main-10: rgba(var(--wl-cyan-rgb), 0.06);
  --main-20: rgba(var(--wl-cyan-rgb), 0.08);
  --main-50: rgba(var(--wl-cyan-rgb), 0.14);
  --main-300: rgba(var(--wl-cyan-rgb), 0.35);
  --main-500: var(--wl-cyan);
  --main-600: var(--wl-cyan);
  --main-700: var(--wl-text);
  background-color: var(--wl-page-bg);
  color: var(--wl-text);

  .extensions-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 16px;
    border-bottom: 1px solid var(--wl-border);
    background-color: rgba(2, 5, 10, 0.74);

    .extensions-tabs {
      flex: 1;
      height: auto;
      display: flex;
      flex-direction: column;

      :deep(.ant-tabs-nav) {
        margin: 0;
        padding: 0;

        &::before {
          border-bottom: none;
        }
      }

      :deep(.ant-tabs-nav::after) {
        content: none;
      }

      :deep(.ant-tabs-nav-left-bar) {
        display: none;
      }

      :deep(.ant-tabs-items) {
        padding: 0;
      }

      :deep(.ant-tabs-tab) {
        padding: 12px 16px;
        font-size: 14px;
        margin: 0;
      }

      :deep(.ant-tabs-ink-bar) {
        display: block;
      }
    }

    .header-actions {
      display: flex;
      gap: 8px;
      padding: 8px 0;
    }
  }

  .extensions-content {
    flex: 1;
    min-height: 0;
    overflow: hidden;

    .tab-panel {
      height: 100%;
      min-height: 0;
      overflow: hidden;
    }
  }
}

.extensions-view :deep(.extension-page-root),
.extensions-view :deep(.layout-wrapper),
.extensions-view :deep(.sidebar-list),
.extensions-view :deep(.main-panel),
.extensions-view :deep(.config-view) {
  background: var(--wl-page-bg);
  color: var(--wl-text);
}

.extensions-view :deep(.sidebar-list) {
  border-right-color: var(--wl-border);
}

.extensions-view :deep(.list-item),
.extensions-view :deep(.detail-section),
.extensions-view :deep(.server-card),
.extensions-view :deep(.skill-card),
.extensions-view :deep(.tool-card),
.extensions-view :deep(.ant-card) {
  border-color: var(--wl-border);
  background: rgba(var(--wl-cyan-rgb), 0.045);
  color: var(--wl-text);
}

.extensions-view :deep(.list-item.active),
.extensions-view :deep(.list-item:hover) {
  border-color: var(--wl-border-gold);
  background: rgba(var(--wl-cyan-rgb), 0.08);
}

.extensions-view :deep(.item-name),
.extensions-view :deep(.section-header),
.extensions-view :deep(.tool-summary h2),
.extensions-view :deep(.ant-tabs-tab),
.extensions-view :deep(.ant-table),
.extensions-view :deep(.ant-table-cell) {
  color: var(--wl-text);
}

.extensions-view :deep(.item-category),
.extensions-view :deep(.section-content),
.extensions-view :deep(.text-muted),
.extensions-view :deep(code) {
  color: var(--wl-muted);
}

@media (max-width: 720px) {
  .extensions-view {
    .extensions-header {
      align-items: flex-start;
      gap: 6px;
      padding: 0 10px;

      .extensions-tabs {
        min-width: 0;

        :deep(.ant-tabs-nav-list) {
          flex-wrap: wrap;
        }

        :deep(.ant-tabs-tab) {
          padding: 10px 8px;
          font-size: 13px;
        }
      }

      .header-actions {
        flex-shrink: 0;
        gap: 6px;
      }
    }
  }
}

@media (max-width: 480px) {
  .extensions-view {
    .extensions-header {
      .header-actions {
        :deep(.lucide-icon-btn) {
          width: 34px;
          min-width: 34px;
          height: 34px;
          padding: 0;
          justify-content: center;

          span {
            display: none;
          }
        }
      }
    }
  }
}
</style>
