<template>
  <div class="theme-hub-view layout-container wl-ant-dark">
    <main class="hub-shell">
      <header class="hub-header">
        <div class="header-copy">
          <p class="eyebrow">MODULE REGISTRY</p>
          <h1>主题分区</h1>
          <p>用真实知识库创建可进入 Wiki、图谱、时间线和质量门禁的 Worldline 模块。</p>
        </div>
        <div class="header-actions">
          <router-link class="ghost-link" to="/">首页</router-link>
          <router-link class="ghost-link" to="/worldline">世界线</router-link>
          <a
            v-if="docsUrl"
            class="ghost-link"
            :href="docsUrl"
            target="_blank"
            rel="noopener noreferrer"
          >
            文档
          </a>
        </div>
      </header>

      <section class="module-console">
        <div class="section-header">
          <div>
            <p class="eyebrow">CUSTOM MODULES</p>
            <h2>知识模块</h2>
          </div>
          <div class="section-actions">
            <span class="module-count">{{ enabledModuleCount }} 个已启用模块</span>
            <button class="primary-command" type="button" @click="openAddModule()">
              <Plus :size="17" />
              <span>添加模块</span>
            </button>
          </div>
        </div>

        <div v-if="infoStore.isLoading" class="module-loading">
          <a-spin />
          <span>正在加载模块</span>
        </div>

        <div v-else-if="modules.length" class="module-grid">
          <article v-for="module in modules" :key="module.id" class="module-card">
            <div class="module-card-head">
              <div>
                <p class="eyebrow">{{ module.status || 'live' }}</p>
                <h3>{{ module.name }}</h3>
              </div>
              <span class="source-badge" :class="{ custom: isCustomModule(module) }">
                {{ isCustomModule(module) ? 'Custom' : 'Config' }}
              </span>
            </div>

            <p class="module-description">
              {{ module.description || '暂无模块描述' }}
            </p>

            <div class="module-meta-grid">
              <div>
                <Database :size="16" />
                <span>{{ resolveModuleDbId(module) || '未绑定知识库' }}</span>
              </div>
              <div>
                <Network :size="16" />
                <span>{{ moduleSurfaceText(module) }}</span>
              </div>
              <div>
                <ShieldCheck :size="16" />
                <span>{{ moduleCapabilityText(module) }}</span>
              </div>
            </div>

            <div class="tag-list">
              <span v-for="tag in (module.tags || []).slice(0, 4)" :key="tag">{{ tag }}</span>
            </div>

            <div class="module-actions">
              <button class="secondary-button" type="button" @click="openWorldline(module)">
                <GitBranch :size="16" />
                <span>世界线</span>
              </button>
              <button class="secondary-button" type="button" @click="openThemeDetail(module)">
                <ExternalLink :size="16" />
                <span>详情</span>
              </button>
              <button
                v-if="isCustomModule(module)"
                class="icon-button"
                type="button"
                aria-label="编辑模块"
                title="编辑模块"
                @click="openEditModule(module)"
              >
                <Pencil :size="16" />
              </button>
              <button
                v-if="isCustomModule(module)"
                class="icon-button danger"
                type="button"
                aria-label="删除模块"
                title="删除模块"
                @click="confirmDeleteModule(module)"
              >
                <Trash2 :size="16" />
              </button>
            </div>
          </article>
        </div>

        <button v-else class="add-module-card" type="button" @click="openAddModule()">
          <span class="add-icon"><Plus :size="34" /></span>
          <span class="add-title">添加自定义模块</span>
          <span class="add-copy">绑定知识库后，Worldline 首页会立即出现可启动模块。</span>
        </button>
      </section>

      <section class="principles">
        <article>
          <FileText :size="22" />
          <h3>Evidence First</h3>
          <p>模块必须能追溯到来源、页码、片段和证据锚点。</p>
        </article>
        <article>
          <Network :size="22" />
          <h3>Wiki + Graph</h3>
          <p>优先构建可审查的 LLM Wiki 和 Temporal Evidence Graph。</p>
        </article>
        <article>
          <ShieldCheck :size="22" />
          <h3>Quality Gate</h3>
          <p>公开或交给 Agent 前必须经过引用覆盖率与一致性检查。</p>
        </article>
      </section>
    </main>

    <a-modal
      :open="state.openModuleModal"
      :title="state.editingId ? '编辑自定义模块' : '添加自定义模块'"
      :confirm-loading="state.saving"
      width="820px"
      class="theme-module-modal wl-ant-dark"
      @ok="saveModule"
      @cancel="closeModuleModal"
    >
      <div class="module-form-grid">
        <label>
          <span>模块名称</span>
          <a-input v-model:value="moduleForm.name" placeholder="例如：产品需求知识库" />
        </label>
        <label>
          <span>绑定知识库</span>
          <a-select
            v-model:value="moduleForm.db_id"
            show-search
            :loading="dbState.listLoading"
            :options="databaseOptions"
            option-filter-prop="label"
            placeholder="选择知识库"
          />
        </label>
        <label>
          <span>副标题</span>
          <a-input v-model:value="moduleForm.subtitle" placeholder="Live knowledge bridge" />
        </label>
        <label>
          <span>文档链接</span>
          <a-input v-model:value="moduleForm.docs_url" placeholder="可选" />
        </label>
        <label class="wide">
          <span>模块描述</span>
          <a-textarea v-model:value="moduleForm.description" :auto-size="{ minRows: 3, maxRows: 5 }" />
        </label>
        <label class="wide">
          <span>模块目标</span>
          <a-textarea v-model:value="moduleForm.objective" :auto-size="{ minRows: 2, maxRows: 3 }" />
        </label>
        <label class="wide">
          <span>证据来源</span>
          <a-input v-model:value="moduleForm.evidence_sources" placeholder="逗号分隔，例如：上传文档, Wiki, 图谱" />
        </label>
        <label class="wide">
          <span>默认问题起点</span>
          <a-textarea
            v-model:value="moduleForm.default_question"
            :auto-size="{ minRows: 2, maxRows: 4 }"
          />
        </label>
        <label>
          <span>标签</span>
          <a-input v-model:value="moduleForm.tags" placeholder="逗号分隔" />
        </label>
        <label>
          <span>能力摘要</span>
          <a-input v-model:value="moduleForm.highlights" placeholder="逗号分隔" />
        </label>
      </div>

      <div v-if="selectedKnowledgeSummary" class="selected-kb-summary">
        <Database :size="17" />
        <div>
          <strong>{{ selectedKnowledgeSummary.name }}</strong>
          <span>{{ selectedKnowledgeSummary.type || '知识库' }} · {{ selectedKnowledgeSummary.description || selectedKnowledgeSummary.id }}</span>
        </div>
      </div>

      <div class="module-secondary-actions">
        <button class="secondary-button" type="button" @click="state.configDrawerOpen = true">
          <SlidersHorizontal :size="16" />
          <span>能力与生成配置</span>
        </button>
        <span>{{ draftCapabilitySummary.enabledGroupCount }} 组能力 / {{ draftCapabilitySummary.endpointCount }} 个接口</span>
      </div>
    </a-modal>

    <a-drawer
      :open="state.configDrawerOpen"
      width="640"
      class="theme-module-drawer wl-ant-dark"
      title="模块配置"
      placement="right"
      @close="state.configDrawerOpen = false"
    >
      <section class="drawer-section">
        <div class="drawer-section-head">
          <p class="eyebrow">SURFACES</p>
          <h3>能力开关</h3>
        </div>
        <div class="surface-switches">
          <div v-for="surface in surfaceOptions" :key="surface.key" class="surface-switch">
            <component :is="surface.icon" :size="18" />
            <div>
              <strong>{{ surface.label }}</strong>
              <span>{{ surface.detail }}</span>
            </div>
            <a-switch v-model:checked="moduleForm.surfaces[surface.key]" />
          </div>
        </div>
      </section>

      <section class="drawer-section">
        <div class="drawer-section-head">
          <p class="eyebrow">GENERATION</p>
          <h3>世界线生成</h3>
        </div>
        <div class="generation-grid">
          <label>
            <span>生成模式</span>
            <a-select v-model:value="moduleForm.generation.mode" :options="generationModeOptions" />
          </label>
          <label>
            <span>分支预算</span>
            <a-input-number v-model:value="moduleForm.generation.branch_budget" :min="1" :max="12" />
          </label>
          <label>
            <span>质量策略</span>
            <a-select v-model:value="moduleForm.generation.quality_profile" :options="qualityProfileOptions" />
          </label>
        </div>
      </section>

      <section class="capability-preview drawer-section">
        <div class="capability-preview-head">
          <div>
            <p class="eyebrow">BACKEND MAP</p>
            <h3>后端能力映射</h3>
          </div>
          <strong>{{ draftCapabilitySummary.enabledGroupCount }} 组 / {{ draftCapabilitySummary.endpointCount }} 个接口</strong>
        </div>

        <div v-if="moduleForm.db_id" class="capability-pill-grid">
          <article v-for="group in draftCapabilityGroups" :key="group.key">
            <strong>{{ group.label }}</strong>
            <span>{{ group.endpoints.map((endpoint) => endpoint.name).join(' / ') }}</span>
          </article>
        </div>
        <p v-else class="capability-empty">先绑定知识库，模块会自动获得证据、Wiki、图谱、时间线、MCP、工作流和质量门禁入口。</p>

        <details class="payload-preview">
          <summary>查看保存到后端的模块配置</summary>
          <pre>{{ modulePayloadPreview }}</pre>
        </details>
      </section>
    </a-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { Modal, message } from 'ant-design-vue'
import { useDatabaseStore } from '@/stores/database'
import { useInfoStore } from '@/stores/info'
import { useUserStore } from '@/stores/user'
import { hasWorldlineLiveBridge, resolveThemeKnowledgeDbId } from '@/apis/worldline_api'
import { buildWorldlineCapabilityContract, summarizeCapabilityContract } from '@/utils/worldlineCapabilities'
import {
  Database,
  ExternalLink,
  FileText,
  GitBranch,
  Network,
  Pencil,
  Plus,
  SlidersHorizontal,
  ShieldCheck,
  Trash2
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const infoStore = useInfoStore()
const userStore = useUserStore()
const databaseStore = useDatabaseStore()
const { databases, state: dbState } = storeToRefs(databaseStore)

const state = reactive({
  openModuleModal: false,
  editingId: '',
  saving: false,
  configDrawerOpen: false
})

const moduleForm = reactive({
  name: '',
  subtitle: 'Live knowledge bridge',
  db_id: '',
  knowledge_name: '',
  knowledge_type: '',
  knowledge_description: '',
  description: '',
  objective: '围绕绑定知识库生成可验证的世界线。',
  evidence_sources: '上传文档, Evidence Anchor, LLM Wiki, Temporal Graph',
  default_question: '围绕这个知识库生成一条可验证的世界线，并指出证据、图谱关系和待确认分支。',
  tags: 'Worldline, Evidence, Wiki, Graph',
  highlights: '证据锚点, LLM Wiki, Temporal Graph, Quality Gate',
  docs_url: '',
  generation: {
    mode: 'base',
    branch_budget: 3,
    quality_profile: 'balanced'
  },
  surfaces: {
    wiki: true,
    graph: true,
    timeline: true,
    quality_gate: true,
    mcp: true,
    workflow: true
  }
})

const surfaceOptions = [
  { key: 'wiki', label: 'Wiki', detail: 'LLM Wiki 页面与引用锚点', icon: FileText },
  { key: 'graph', label: 'Graph', detail: '实体、关系和 Neo4j 投影', icon: Network },
  { key: 'timeline', label: 'Timeline', detail: '时间事实与变化路径', icon: GitBranch },
  { key: 'quality_gate', label: 'Quality Gate', detail: '引用覆盖率和一致性检查', icon: ShieldCheck },
  { key: 'mcp', label: 'MCP', detail: '受控工具清单和审计日志', icon: ShieldCheck },
  { key: 'workflow', label: 'Workflow', detail: 'Agent 工作流规划', icon: GitBranch }
]

const generationModeOptions = [
  { label: '基础生成', value: 'base' },
  { label: '聚焦分支', value: 'focused' }
]

const qualityProfileOptions = [
  { label: '平衡', value: 'balanced' },
  { label: '严格', value: 'strict' },
  { label: '快速', value: 'fast' }
]

const docsUrl = computed(() => infoStore.docsUrl || '')
const modules = computed(() => infoStore.themes || [])
const enabledModuleCount = computed(() => modules.value.filter((module) => hasWorldlineLiveBridge(module)).length)
const databaseOptions = computed(() =>
  (databases.value || []).map((database) => ({
    label: `${database.name || database.db_id} (${database.kb_type || 'kb'})`,
    value: database.db_id
  }))
)
const selectedDatabase = computed(() => (databases.value || []).find((database) => database.db_id === moduleForm.db_id))
const selectedKnowledgeSummary = computed(() => {
  const database = selectedDatabase.value || {}
  const id = moduleForm.db_id
  if (!id) return null
  return {
    id,
    name: moduleForm.knowledge_name || database.name || id,
    type: moduleForm.knowledge_type || database.kb_type || '',
    description: moduleForm.knowledge_description || database.description || ''
  }
})

const splitList = (value = '') =>
  String(value || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)

const joinList = (value, fallback = []) => (Array.isArray(value) ? value : splitList(value || fallback.join(', '))).join(', ')

const resolveModuleDbId = (module = {}) => resolveThemeKnowledgeDbId(module)

const isCustomModule = (module = {}) => module?.metadata?.source === 'custom-theme-module'

const moduleSurfaceText = (module = {}) => {
  const surfaces = module?.worldline?.surfaces || {}
  const active = surfaceOptions.filter((item) => surfaces[item.key] !== false).map((item) => item.label)
  return active.length ? active.join(' / ') : 'Worldline'
}

const buildModuleCapabilityContract = (module = {}) =>
  buildWorldlineCapabilityContract({
    themeId: module?.id || '',
    dbId: resolveModuleDbId(module),
    surfaces: module?.worldline?.surfaces || {}
  })

const moduleCapabilityText = (module = {}) => {
  if (!resolveModuleDbId(module)) return '待绑定后端能力'
  const summary = summarizeCapabilityContract(buildModuleCapabilityContract(module))
  return `${summary.enabledGroupCount} 组能力 / ${summary.endpointCount} 个接口`
}

const draftCapabilityContract = computed(() =>
  buildWorldlineCapabilityContract({
    themeId: state.editingId,
    dbId: moduleForm.db_id,
    surfaces: moduleForm.surfaces
  })
)
const draftCapabilitySummary = computed(() => summarizeCapabilityContract(draftCapabilityContract.value))
const draftCapabilityGroups = computed(() => draftCapabilitySummary.value.enabledGroups.slice(0, 6))

const resetForm = (module = null) => {
  const routeDbId = String(route.query.knowledge_db_id || route.query.db_id || '')
  const routeKnowledgeName = String(route.query.knowledge_name || route.query.name || '')
  const routeKnowledgeType = String(route.query.knowledge_type || '')
  const routeKnowledgeDescription = String(route.query.knowledge_description || '')
  const dbId = module ? resolveModuleDbId(module) : routeDbId
  moduleForm.name = module?.name || String(route.query.name || (routeKnowledgeName ? `${routeKnowledgeName} 世界线` : ''))
  moduleForm.subtitle = module?.subtitle || 'Live knowledge bridge'
  moduleForm.db_id = dbId
  moduleForm.knowledge_name = module?.knowledge?.name || module?.metadata?.knowledge_name || routeKnowledgeName
  moduleForm.knowledge_type =
    module?.knowledge?.kb_type || module?.knowledge?.type || module?.metadata?.knowledge_type || routeKnowledgeType
  moduleForm.knowledge_description =
    module?.knowledge?.description || module?.metadata?.knowledge_description || routeKnowledgeDescription
  moduleForm.description = module?.description || ''
  moduleForm.objective =
    module?.worldline?.objective || module?.context?.objective || String(route.query.objective || '围绕绑定知识库生成可验证的世界线。')
  moduleForm.evidence_sources = joinList(
    module?.worldline?.evidence_sources || module?.context?.evidence_sources,
    ['上传文档', 'Evidence Anchor', 'LLM Wiki', 'Temporal Graph']
  )
  moduleForm.default_question =
    module?.worldline?.default_question ||
    module?.context?.default_question ||
    '围绕这个知识库生成一条可验证的世界线，并指出证据、图谱关系和待确认分支。'
  moduleForm.tags = (module?.tags || ['Worldline', 'Evidence', 'Wiki', 'Graph']).join(', ')
  moduleForm.highlights = (
    module?.highlights || ['证据锚点', 'LLM Wiki', 'Temporal Graph', 'Quality Gate']
  ).join(', ')
  moduleForm.docs_url = module?.links?.docs || ''
  moduleForm.generation = {
    mode: module?.worldline?.generation?.mode || module?.context?.generation?.mode || 'base',
    branch_budget: Number(module?.worldline?.generation?.branch_budget || module?.context?.generation?.branch_budget || 3),
    quality_profile:
      module?.worldline?.generation?.quality_profile || module?.context?.generation?.quality_profile || 'balanced'
  }
  const surfaces = module?.worldline?.surfaces || {}
  surfaceOptions.forEach((item) => {
    moduleForm.surfaces[item.key] = surfaces[item.key] !== false
  })
}

const openAddModule = () => {
  state.editingId = ''
  resetForm()
  state.openModuleModal = true
}

const openEditModule = (module) => {
  state.editingId = module.id
  resetForm(module)
  state.openModuleModal = true
}

const closeModuleModal = () => {
  state.openModuleModal = false
  state.editingId = ''
  state.configDrawerOpen = false
  resetForm()
}

const buildPayload = () => {
  const capabilityMap = buildWorldlineCapabilityContract({
    themeId: state.editingId,
    dbId: moduleForm.db_id,
    surfaces: moduleForm.surfaces
  })
  const evidenceSources = splitList(moduleForm.evidence_sources)
  const generation = { ...moduleForm.generation }

  return {
    name: moduleForm.name.trim(),
    subtitle: moduleForm.subtitle.trim(),
    db_id: moduleForm.db_id,
    knowledge_db_id: moduleForm.db_id,
    knowledge_name: selectedKnowledgeSummary.value?.name || '',
    knowledge_type: selectedKnowledgeSummary.value?.type || '',
    knowledge_description: selectedKnowledgeSummary.value?.description || '',
    description: moduleForm.description.trim(),
    objective: moduleForm.objective.trim(),
    evidence_sources: evidenceSources,
    default_question: moduleForm.default_question.trim(),
    tags: splitList(moduleForm.tags),
    highlights: splitList(moduleForm.highlights),
    docs_url: moduleForm.docs_url.trim(),
    knowledge: {
      db_id: moduleForm.db_id,
      knowledge_db_id: moduleForm.db_id,
      name: selectedKnowledgeSummary.value?.name || '',
      type: selectedKnowledgeSummary.value?.type || '',
      kb_type: selectedKnowledgeSummary.value?.type || '',
      description: selectedKnowledgeSummary.value?.description || '',
      evidence_sources: evidenceSources
    },
    context: {
      theme: state.editingId,
      module: state.editingId,
      scene: 'overview',
      version: 'worldline-context-v1',
      db_id: moduleForm.db_id,
      knowledge_db_id: moduleForm.db_id,
      knowledge_name: selectedKnowledgeSummary.value?.name || '',
      knowledge_type: selectedKnowledgeSummary.value?.type || '',
      objective: moduleForm.objective.trim(),
      evidence_sources: evidenceSources,
      generation,
      default_question: moduleForm.default_question.trim()
    },
    worldline: {
      surfaces: { ...moduleForm.surfaces },
      db_id: moduleForm.db_id,
      knowledge_db_id: moduleForm.db_id,
      objective: moduleForm.objective.trim(),
      evidence_sources: evidenceSources,
      generation,
      default_question: moduleForm.default_question.trim(),
      capability_map: capabilityMap
    },
    metadata: {
      knowledge_name: selectedKnowledgeSummary.value?.name || '',
      knowledge_type: selectedKnowledgeSummary.value?.type || '',
      knowledge_description: selectedKnowledgeSummary.value?.description || ''
    }
  }
}

const modulePayloadPreview = computed(() => JSON.stringify(buildPayload(), null, 2))

const saveModule = async () => {
  if (!userStore.isAdmin) {
    message.warning('需要管理员权限')
    return
  }
  if (!moduleForm.name.trim()) {
    message.warning('请填写模块名称')
    return
  }
  if (!moduleForm.db_id) {
    message.warning('请选择知识库')
    return
  }

  state.saving = true
  try {
    if (state.editingId) {
      await infoStore.updateThemeModule(state.editingId, buildPayload())
      message.success('模块已更新')
    } else {
      await infoStore.createThemeModule(buildPayload())
      message.success('模块已创建')
    }
    closeModuleModal()
  } catch (error) {
    message.error(error.message || '保存模块失败')
  } finally {
    state.saving = false
  }
}

const confirmDeleteModule = (module) => {
  Modal.confirm({
    title: '删除自定义模块',
    content: `确认删除“${module.name}”？`,
    okText: '删除',
    cancelText: '取消',
    okType: 'danger',
    onOk: async () => {
      await infoStore.deleteThemeModule(module.id)
      message.success('模块已删除')
    }
  })
}

const openWorldline = (module) => {
  const dbId = resolveModuleDbId(module)
  router.push({
    path: `/worldline/${module.id}`,
    query: dbId
      ? {
          db_id: dbId,
          knowledge_db_id: dbId
        }
      : {}
  })
}

const openThemeDetail = (module) => {
  router.push(`/themes/${module.id}`)
}

onMounted(async () => {
  await infoStore.loadInfoConfig(true)
  if (userStore.isAdmin) {
    await databaseStore.loadDatabases()
  }
  if (route.query.new_module === '1') {
    openAddModule()
  }
})

watch(
  () => moduleForm.db_id,
  (dbId) => {
    const database = (databases.value || []).find((item) => item.db_id === dbId)
    if (!database) return
    moduleForm.knowledge_name = database.name || database.db_id
    moduleForm.knowledge_type = database.kb_type || ''
    moduleForm.knowledge_description = database.description || ''
  }
)
</script>

<style scoped lang="less">
.theme-hub-view {
  min-height: 100vh;
  color: var(--wl-text);
  background: var(--wl-page-bg);
}

.hub-shell {
  width: min(1260px, calc(100% - 32px));
  margin: 0 auto;
  padding: 26px 0 54px;
}

.hub-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 18px;
}

.header-copy {
  max-width: 820px;
}

.eyebrow {
  margin: 0 0 8px;
  color: var(--wl-gold);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0;
  text-transform: uppercase;
}

.header-copy h1 {
  margin: 0;
  color: var(--wl-text);
  font-size: 52px;
  font-weight: 950;
  line-height: 1.05;
  letter-spacing: 0;
}

.header-copy p:last-child {
  margin: 12px 0 0;
  color: var(--wl-muted);
  line-height: 1.7;
}

.header-actions,
.section-actions,
.module-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.header-actions {
  justify-content: flex-end;
}

.ghost-link,
.primary-command,
.secondary-button,
.icon-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 38px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  color: var(--wl-text-soft);
  text-decoration: none;
  font-weight: 800;
  cursor: pointer;
}

.ghost-link,
.secondary-button,
.icon-button {
  background: rgba(var(--wl-cyan-rgb), 0.06);
}

.ghost-link,
.secondary-button {
  padding: 0 13px;
}

.primary-command {
  gap: 7px;
  padding: 0 14px;
  border-color: var(--wl-border-gold);
  background: rgba(var(--wl-gold-rgb), 0.13);
  color: var(--wl-gold-soft);
}

.secondary-button {
  gap: 7px;
}

.icon-button {
  width: 38px;
  padding: 0;
}

.icon-button.danger {
  border-color: rgba(255, 107, 107, 0.35);
  color: #ff9d9d;
}

.ghost-link:hover,
.secondary-button:hover,
.icon-button:hover,
.primary-command:hover {
  border-color: var(--wl-border-strong);
  background: rgba(var(--wl-cyan-rgb), 0.1);
  color: var(--wl-text);
}

.module-console,
.principles article,
.module-card {
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background: var(--wl-panel);
  box-shadow: var(--wl-shadow-soft);
}

.module-console {
  padding: 22px;
}

.section-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.section-header h2 {
  margin: 0;
  color: var(--wl-text);
  font-size: 25px;
  font-weight: 950;
}

.module-count,
.source-badge {
  border: 1px solid rgba(var(--wl-gold-rgb), 0.25);
  border-radius: 999px;
  padding: 7px 11px;
  background: rgba(var(--wl-gold-rgb), 0.08);
  color: var(--wl-gold-soft);
  font-size: 13px;
  font-weight: 900;
  white-space: nowrap;
}

.source-badge {
  padding: 5px 9px;
  color: var(--wl-muted);
  border-color: var(--wl-border);
  background: rgba(var(--wl-cyan-rgb), 0.05);
}

.source-badge.custom {
  border-color: var(--wl-border-gold);
  color: var(--wl-gold-soft);
}

.module-loading {
  min-height: 160px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--wl-muted);
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.module-card {
  min-height: 264px;
  display: flex;
  flex-direction: column;
  padding: 18px;
}

.module-card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.module-card h3 {
  margin: 0;
  color: var(--wl-text);
  font-size: 20px;
  font-weight: 950;
}

.module-description {
  min-height: 48px;
  margin: 12px 0;
  color: var(--wl-muted);
  line-height: 1.6;
}

.module-meta-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
  margin-bottom: 12px;
}

.module-meta-grid div {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--wl-text-soft);
  font-size: 13px;
}

.module-meta-grid span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  min-height: 28px;
  margin-bottom: 14px;
}

.tag-list span {
  border: 1px solid var(--wl-border);
  border-radius: 999px;
  padding: 4px 8px;
  background: rgba(var(--wl-cyan-rgb), 0.06);
  color: var(--wl-muted);
  font-size: 12px;
  font-weight: 800;
}

.module-actions {
  margin-top: auto;
}

.add-module-card {
  width: 100%;
  min-height: 230px;
  display: grid;
  grid-template-columns: 78px minmax(0, 1fr);
  grid-template-areas:
    'icon title'
    'icon copy';
  align-items: center;
  column-gap: 20px;
  padding: 24px;
  border: 1px dashed var(--wl-border-strong);
  border-radius: var(--wl-radius);
  background:
    linear-gradient(90deg, rgba(var(--wl-gold-rgb), 0.07), transparent 30%),
    rgba(var(--wl-cyan-rgb), 0.045);
  color: var(--wl-text);
  cursor: pointer;
  text-align: left;
}

.add-module-card:hover {
  border-color: var(--wl-border-gold);
  background:
    linear-gradient(90deg, rgba(var(--wl-gold-rgb), 0.1), transparent 32%),
    rgba(var(--wl-cyan-rgb), 0.065);
}

.add-icon {
  grid-area: icon;
  width: 78px;
  height: 78px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--wl-border-gold);
  border-radius: var(--wl-radius);
  background: rgba(var(--wl-gold-rgb), 0.1);
  color: var(--wl-gold-soft);
}

.add-title {
  grid-area: title;
  color: var(--wl-text);
  font-size: 24px;
  font-weight: 950;
}

.add-copy {
  grid-area: copy;
  max-width: 720px;
  margin-top: 8px;
  color: var(--wl-muted);
  line-height: 1.7;
}

.principles {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 14px;
}

.principles article {
  min-height: 164px;
  padding: 18px;
}

.principles svg {
  color: var(--wl-cyan);
}

.principles h3 {
  margin: 12px 0 0;
  color: var(--wl-text);
  font-size: 18px;
  font-weight: 950;
}

.principles p {
  margin: 8px 0 0;
  color: var(--wl-muted);
  line-height: 1.65;
}

.module-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.module-form-grid label {
  display: flex;
  flex-direction: column;
  gap: 7px;
  color: var(--wl-text);
  font-weight: 800;
}

.module-form-grid label.wide {
  grid-column: 1 / -1;
}

.selected-kb-summary,
.module-secondary-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 14px;
  padding: 12px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.045);
}

.selected-kb-summary svg {
  color: var(--wl-cyan);
  flex: 0 0 auto;
}

.selected-kb-summary strong,
.selected-kb-summary span {
  display: block;
}

.selected-kb-summary strong {
  color: var(--wl-text);
}

.selected-kb-summary span,
.module-secondary-actions span {
  color: var(--wl-muted);
  font-size: 12px;
}

.module-secondary-actions {
  flex-wrap: wrap;
  justify-content: space-between;
}

.drawer-section {
  margin-bottom: 18px;
}

.drawer-section-head {
  margin-bottom: 10px;
}

.drawer-section-head h3 {
  margin: 0;
  color: var(--wl-text);
  font-size: 17px;
  font-weight: 950;
}

.generation-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.generation-grid label {
  display: flex;
  flex-direction: column;
  gap: 7px;
  color: var(--wl-text);
  font-weight: 800;
}

.surface-switches {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.surface-switch {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.045);
}

.surface-switch svg {
  color: var(--wl-cyan);
}

.surface-switch strong,
.surface-switch span {
  display: block;
}

.surface-switch strong {
  color: var(--wl-text);
}

.surface-switch span {
  color: var(--wl-muted);
  font-size: 12px;
}

.capability-preview {
  margin-top: 16px;
  padding: 14px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.035);
}

.capability-preview-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 12px;
}

.capability-preview-head h3 {
  margin: 0;
  color: var(--wl-text);
  font-size: 17px;
  font-weight: 950;
}

.capability-preview-head strong {
  border: 1px solid var(--wl-border-gold);
  border-radius: 999px;
  padding: 6px 10px;
  color: var(--wl-gold-soft);
  background: rgba(var(--wl-gold-rgb), 0.08);
  font-size: 12px;
  white-space: nowrap;
}

.capability-pill-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.capability-pill-grid article {
  min-width: 0;
  padding: 10px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(255, 255, 255, 0.025);
}

.capability-pill-grid strong,
.capability-pill-grid span {
  display: block;
}

.capability-pill-grid strong {
  color: var(--wl-text);
  font-size: 13px;
}

.capability-pill-grid span {
  overflow: hidden;
  margin-top: 5px;
  color: var(--wl-muted);
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.capability-empty {
  margin: 0;
  color: var(--wl-muted);
  line-height: 1.7;
}

.payload-preview {
  margin-top: 12px;
}

.payload-preview summary {
  cursor: pointer;
  color: var(--wl-gold-soft);
  font-size: 13px;
  font-weight: 800;
}

.payload-preview pre {
  max-height: 220px;
  overflow: auto;
  margin: 10px 0 0;
  padding: 12px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: #02060a;
  color: var(--wl-text-soft);
  font-size: 11px;
  line-height: 1.55;
  white-space: pre-wrap;
}

:global(.theme-module-modal .ant-modal-content),
:global(.theme-module-modal .ant-modal-header),
:global(.theme-module-modal .ant-modal-body),
:global(.theme-module-modal .ant-modal-footer),
:global(.theme-module-drawer .ant-drawer-header),
:global(.theme-module-drawer .ant-drawer-body),
:global(.theme-module-drawer .ant-drawer-content) {
  background: #07131d;
}

:global(.theme-module-modal .ant-modal-content) {
  border: 1px solid var(--wl-border-strong);
  box-shadow: 0 28px 76px rgba(0, 0, 0, 0.62);
}

@media (max-width: 1050px) {
  .module-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 820px) {
  .hub-header,
  .section-header {
    flex-direction: column;
  }

  .header-actions,
  .section-actions {
    justify-content: flex-start;
  }

  .header-copy h1 {
    font-size: 40px;
  }

  .module-grid,
  .principles,
  .module-form-grid,
  .generation-grid,
  .surface-switches,
  .capability-pill-grid {
    grid-template-columns: 1fr;
  }

  .add-module-card {
    grid-template-columns: 1fr;
    grid-template-areas:
      'icon'
      'title'
      'copy';
    row-gap: 12px;
  }
}
</style>
