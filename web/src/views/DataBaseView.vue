<template>
  <div class="database-container layout-container wl-ant-dark">
    <HeaderComponent title="文档知识库" :loading="dbState.listLoading">
      <template #actions>
        <a-button type="primary" @click="openCreateDatabaseModal"> 新建知识库 </a-button>
      </template>
    </HeaderComponent>

    <a-modal
      :open="state.openNewDatabaseModel"
      title="新建知识库"
      :confirm-loading="dbState.creating"
      @ok="handleCreateDatabase"
      @cancel="cancelCreateDatabase"
      class="new-database-modal wl-ant-dark"
      width="760px"
      destroyOnClose
    >
      <div class="create-modal-body">
        <section class="create-section">
          <div class="create-section-title">
            <span>知识库类型</span>
            <em>*</em>
          </div>
          <div class="kb-type-cards compact">
            <div
              v-for="(typeInfo, typeKey) in orderedKbTypes"
              :key="typeKey"
              class="kb-type-card"
              :class="{ active: newDatabase.kb_type === typeKey }"
              :data-type="typeKey"
              @click="handleKbTypeChange(typeKey)"
            >
              <div class="card-header">
                <component :is="getKbTypeIcon(typeKey)" class="type-icon" />
                <span class="type-title">{{ getKbTypeLabel(typeKey) }}</span>
              </div>
              <div class="card-description">{{ typeInfo.description }}</div>
            </div>
          </div>
        </section>

        <section class="create-field-grid">
          <label class="create-field">
            <span>知识库名称 <em>*</em></span>
            <a-input v-model:value="newDatabase.name" placeholder="新建知识库名称" size="large" />
          </label>
          <label class="create-field">
            <span>知识库描述</span>
            <AiTextarea
              v-model="newDatabase.description"
              :name="newDatabase.name"
              placeholder="新建知识库描述"
              :auto-size="{ minRows: 2, maxRows: 4 }"
            />
          </label>
        </section>

        <template v-if="newDatabase.kb_type !== 'dify'">
          <section class="create-field-grid">
            <label class="create-field">
              <span>嵌入模型</span>
              <EmbeddingModelSelector
                v-model:value="newDatabase.embed_model_name"
                style="width: 100%"
                size="large"
                placeholder="请选择嵌入模型"
              />
            </label>
            <label class="create-field">
              <span>
                分块策略
                <a-tooltip :title="selectedPresetDescription">
                  <QuestionCircleOutlined class="chunk-preset-help-icon" />
                </a-tooltip>
              </span>
              <a-select
                v-model:value="newDatabase.chunk_preset_id"
                :options="chunkPresetOptions"
                style="width: 100%"
                size="large"
              />
            </label>
          </section>
          <div class="embedding-health-strip" :class="embeddingHealthClass">
            <span>{{ embeddingHealthText }}</span>
            <a-button
              type="link"
              size="small"
              :loading="state.embeddingStatusLoading"
              @click="loadEmbeddingStatuses"
            >
              刷新
            </a-button>
          </div>
        </template>

        <section v-if="newDatabase.kb_type === 'lightrag'" class="create-field-grid">
          <label class="create-field">
            <span>语言</span>
            <a-select
              v-model:value="newDatabase.language"
              :options="languageOptions"
              style="width: 100%"
              size="large"
              :dropdown-match-select-width="false"
            />
          </label>
          <label class="create-field">
            <span>语言模型 (LLM)</span>
            <ModelSelectorComponent
              :model_spec="llmModelSpec"
              placeholder="请选择模型"
              @select-model="handleLLMSelect"
              size="large"
              style="width: 100%; height: 60px"
            />
          </label>
        </section>

        <section v-if="newDatabase.kb_type === 'dify'" class="create-field-grid">
          <label class="create-field">
            <span>Dify API URL <em>*</em></span>
            <a-input
              v-model:value="newDatabase.dify_api_url"
              placeholder="例如: https://api.dify.ai/v1"
              size="large"
            />
          </label>
          <label class="create-field">
            <span>Dify Token <em>*</em></span>
            <a-input-password
              v-model:value="newDatabase.dify_token"
              placeholder="请输入 Dify API Token"
              size="large"
            />
          </label>
          <label class="create-field">
            <span>Dataset ID <em>*</em></span>
            <a-input
              v-model:value="newDatabase.dify_dataset_id"
              placeholder="请输入 Dify dataset_id"
              size="large"
            />
          </label>
        </section>

        <section class="compact-summary-grid">
          <div class="compact-summary-card">
            <div>
              <span>后端配置</span>
              <strong>{{ backendConfigSummary }}</strong>
            </div>
            <a-button size="small" @click="openBackendConfigDrawer">
              <template #icon><Settings :size="14" /></template>
              设置
            </a-button>
          </div>

          <div class="compact-summary-card">
            <div>
              <span>分块解析</span>
              <strong>{{ chunkConfigSummary }}</strong>
            </div>
            <a-button
              size="small"
              :disabled="newDatabase.kb_type === 'dify'"
              @click="openChunkParserDrawer"
            >
              <template #icon><SlidersHorizontal :size="14" /></template>
              配置
            </a-button>
          </div>

          <div class="compact-summary-card">
            <div>
              <span>共享设置</span>
              <strong>{{ shareConfigSummary }}</strong>
            </div>
            <a-button size="small" @click="openShareConfigDrawer">
              <template #icon><Share2 :size="14" /></template>
              调整
            </a-button>
          </div>

          <div class="compact-summary-card">
            <div>
              <span>创建请求</span>
              <strong>POST /api/knowledge/databases</strong>
            </div>
            <a-button size="small" @click="openBackendPayloadPreview">
              <template #icon><Code2 :size="14" /></template>
              预览
            </a-button>
          </div>
        </section>

        <div class="create-capability-panel compact">
          <div class="capability-panel-head">
            <div>
              <p>创建后能力</p>
              <h3>{{ selectedKbTypeCapabilityTitle }}</h3>
            </div>
            <span>{{ newDatabase.kb_type || 'kb' }}</span>
          </div>
          <div class="capability-grid">
            <div v-for="item in selectedCapabilityItems" :key="item.title" class="capability-item">
              <component :is="item.icon" :size="18" />
              <strong>{{ item.title }}</strong>
              <small>{{ item.description }}</small>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <a-button key="back" @click="cancelCreateDatabase">取消</a-button>
        <a-button
          key="submit"
          type="primary"
          :loading="dbState.creating"
          @click="handleCreateDatabase"
          >创建</a-button
        >
      </template>
    </a-modal>

    <a-drawer
      :open="state.backendConfigDrawerOpen"
      width="460"
      class="create-database-drawer wl-ant-dark"
      title="高级后端配置"
      placement="right"
      @close="closeCreateDrawers"
    >
      <div class="create-drawer-body">
        <div class="backend-advanced-summary">
          <strong>{{ backendConfigSummary }}</strong>
          <span>映射到后端 additional_params，不影响主表单字段。</span>
        </div>

        <div v-if="newDatabase.kb_type !== 'dify'" class="backend-advanced-grid">
          <div class="backend-advanced-item">
            <div>
              <strong>私有知识库</strong>
              <span>创建后使用私有前缀，卡片会显示锁定标记。</span>
            </div>
            <a-switch
              v-model:checked="newDatabase.is_private"
              checked-children="私有"
              un-checked-children="公开"
            />
          </div>
          <div class="backend-advanced-item">
            <div>
              <strong>存储标识</strong>
              <span>可选，写入 additional_params.storage。</span>
            </div>
            <a-input v-model:value="newDatabase.storage" placeholder="默认后端存储" allow-clear />
          </div>
        </div>

        <div v-else class="backend-advanced-summary">
          <strong>Dify Dataset</strong>
          <span>Dify API URL、Token 和 Dataset ID 在主表单填写，后端会校验必填项。</span>
        </div>
      </div>
    </a-drawer>

    <a-drawer
      :open="state.chunkParserDrawerOpen"
      width="520"
      class="create-database-drawer wl-ant-dark"
      title="分块解析"
      placement="right"
      @close="closeCreateDrawers"
    >
      <div class="create-drawer-body">
        <div class="backend-advanced-summary">
          <strong>{{ chunkConfigSummary }}</strong>
          <span>不覆盖时只提交分块策略 preset，由后端填充默认解析参数。</span>
        </div>

        <div v-if="newDatabase.kb_type !== 'dify'" class="chunk-override-panel">
          <div class="backend-advanced-item inline">
            <div>
              <strong>覆盖分块解析参数</strong>
              <span>开启后提交 chunk_parser_config。</span>
            </div>
            <a-switch
              v-model:checked="newDatabase.use_chunk_parser_override"
              checked-children="覆盖"
              un-checked-children="默认"
            />
          </div>

          <div v-if="newDatabase.use_chunk_parser_override" class="chunk-override-grid">
            <label>
              <span>Chunk Token 数</span>
              <a-input-number
                v-model:value="newDatabase.chunk_parser_config.chunk_token_num"
                :min="128"
                :max="4096"
                style="width: 100%"
              />
            </label>
            <label>
              <span>重叠比例 %</span>
              <a-input-number
                v-model:value="newDatabase.chunk_parser_config.overlapped_percent"
                :min="0"
                :max="99"
                style="width: 100%"
              />
            </label>
            <label>
              <span>分隔符</span>
              <a-input
                v-model:value="newDatabase.chunk_parser_config.delimiter"
                placeholder="例如 \\n 或 ---"
                allow-clear
              />
            </label>
            <div class="chunk-override-toggles">
              <a-switch
                v-model:checked="newDatabase.chunk_parser_config.raptor_use"
                checked-children="RAPTOR 开"
                un-checked-children="RAPTOR 关"
              />
              <a-switch
                v-model:checked="newDatabase.chunk_parser_config.graphrag_use"
                checked-children="GraphRAG 开"
                un-checked-children="GraphRAG 关"
              />
            </div>
          </div>
        </div>

        <div v-else class="backend-advanced-summary">
          <strong>Dify 外部解析</strong>
          <span>Dify 类型由外部 Dataset 管理分块和检索。</span>
        </div>
      </div>
    </a-drawer>

    <a-drawer
      :open="state.shareConfigDrawerOpen"
      width="460"
      class="create-database-drawer wl-ant-dark"
      title="共享设置"
      placement="right"
      @close="closeCreateDrawers"
    >
      <div class="create-drawer-body">
        <div class="backend-advanced-summary">
          <strong>{{ shareConfigSummary }}</strong>
          <span>提交为 share_config，指定部门时会写入 accessible_departments。</span>
        </div>
        <ShareConfigForm v-model="shareConfig" :auto-select-user-dept="true" />
      </div>
    </a-drawer>

    <a-drawer
      :open="state.payloadPreviewDrawerOpen"
      width="620"
      class="create-database-drawer wl-ant-dark"
      title="创建请求预览"
      placement="right"
      @close="closeCreateDrawers"
    >
      <div class="create-drawer-body">
        <div class="backend-payload-inline" data-backend-payload-preview="true">
          <div class="backend-payload-inline-head">
            <div>
              <strong>POST /api/knowledge/databases</strong>
              <span>敏感 Token 已遮罩。</span>
            </div>
          </div>
          <pre>{{ backendPayloadPreview }}</pre>
        </div>
      </div>
    </a-drawer>

    <section v-if="lastCreatedDatabase" class="creation-next-actions">
      <div>
        <p class="eyebrow">CREATED</p>
        <h3>{{ lastCreatedDatabase.name || lastCreatedDatabase.db_id }}</h3>
        <span>{{ lastCreatedDatabase.db_id }}</span>
      </div>
      <div class="next-action-buttons">
        <a-button @click="navigateToDatabase(lastCreatedDatabase.db_id)">上传知识文件</a-button>
        <a-button @click="openGraphForDatabase(lastCreatedDatabase)">查看知识图谱</a-button>
        <a-button type="primary" @click="openThemeModuleForDatabase(lastCreatedDatabase)">
          创建主题模块
        </a-button>
      </div>
    </section>

    <!-- 加载状态 -->
    <div v-if="dbState.listLoading" class="loading-container">
      <a-spin size="large" />
      <p>正在加载知识库...</p>
    </div>

    <!-- 空状态显示 -->
    <div v-else-if="!databases || databases.length === 0" class="empty-state">
      <h3 class="empty-title">暂无知识库</h3>
      <p class="empty-description">创建您的第一个知识库，开始管理文档和知识</p>
      <a-button type="primary" size="large" @click="openCreateDatabaseModal">
        <template #icon>
          <PlusOutlined />
        </template>
        创建知识库
      </a-button>
    </div>

    <!-- 数据库列表 -->
    <div v-else class="databases">
      <div
        v-for="database in databases"
        :key="database.db_id"
        class="database dbcard"
        @click="navigateToDatabase(database.db_id)"
      >
        <!-- 私有知识库锁定图标 -->
        <LockOutlined
          v-if="database.metadata?.is_private"
          class="private-lock-icon"
          title="私有知识库"
        />
        <div class="top">
          <div class="icon">
            <component :is="getKbTypeIcon(database.kb_type || 'lightrag')" />
          </div>
          <div class="info">
            <h3>{{ database.name }}</h3>
            <p>
              <span>{{ database.files ? Object.keys(database.files).length : 0 }} 文件</span>
              <span class="created-time-inline" v-if="database.created_at">
                {{ formatCreatedTime(database.created_at) }}
              </span>
            </p>
          </div>
        </div>
        <!-- <a-tooltip :title="database.description || '暂无描述'">
          <p class="description">{{ database.description || '暂无描述' }}</p>
        </a-tooltip> -->
        <p class="description">{{ database.description || '暂无描述' }}</p>
        <div class="tags">
          <a-tag color="blue" v-if="database.embed_info?.name">{{
            database.embed_info.name
          }}</a-tag>
          <!-- <a-tag color="green" v-if="database.embed_info?.dimension">{{ database.embed_info.dimension }}</a-tag> -->
          <a-tag
            :color="getKbTypeColor(database.kb_type || 'lightrag')"
            class="kb-type-tag"
            size="small"
          >
            {{ getKbTypeLabel(database.kb_type || 'lightrag') }}
          </a-tag>
        </div>
        <!-- <button @click="deleteDatabase(database.collection_name)">删除</button> -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useConfigStore } from '@/stores/config'
import { useDatabaseStore } from '@/stores/database'
import { LockOutlined, PlusOutlined, QuestionCircleOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { embeddingApi, typeApi } from '@/apis/knowledge_api'
import HeaderComponent from '@/components/HeaderComponent.vue'
import ModelSelectorComponent from '@/components/ModelSelectorComponent.vue'
import EmbeddingModelSelector from '@/components/EmbeddingModelSelector.vue'
import ShareConfigForm from '@/components/ShareConfigForm.vue'
import dayjs, { parseToShanghai } from '@/utils/time'
import AiTextarea from '@/components/AiTextarea.vue'
import { getKbTypeLabel, getKbTypeIcon, getKbTypeColor } from '@/utils/kb_utils'
import { CHUNK_PRESET_OPTIONS, getChunkPresetDescription } from '@/utils/chunk_presets'
import {
  Code2,
  Database,
  FileText,
  GitBranch,
  Network,
  Search,
  Settings,
  Share2,
  ShieldCheck,
  SlidersHorizontal
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const configStore = useConfigStore()
const databaseStore = useDatabaseStore()

// 使用 store 的状态
const { databases, state: dbState } = storeToRefs(databaseStore)

const state = reactive({
  openNewDatabaseModel: false,
  backendConfigDrawerOpen: false,
  chunkParserDrawerOpen: false,
  shareConfigDrawerOpen: false,
  payloadPreviewDrawerOpen: false,
  embeddingStatusLoading: false,
  embeddingStatusError: ''
})

const embeddingStatuses = ref({})
const lastCreatedDatabase = ref(null)

// 共享配置状态（用于提交数据）
const shareConfig = ref({
  is_shared: true,
  accessible_department_ids: []
})

// 语言选项（值使用英文，以保证后端/LightRAG 兼容；标签为中英文方便理解）
const languageOptions = [
  { label: '中文 Chinese', value: 'Chinese' },
  { label: '英语 English', value: 'English' },
  { label: '日语 Japanese', value: 'Japanese' },
  { label: '韩语 Korean', value: 'Korean' },
  { label: '德语 German', value: 'German' },
  { label: '法语 French', value: 'French' },
  { label: '西班牙语 Spanish', value: 'Spanish' },
  { label: '葡萄牙语 Portuguese', value: 'Portuguese' },
  { label: '俄语 Russian', value: 'Russian' },
  { label: '阿拉伯语 Arabic', value: 'Arabic' },
  { label: '印地语 Hindi', value: 'Hindi' }
]

const chunkPresetOptions = CHUNK_PRESET_OPTIONS.map(({ label, value }) => ({ label, value }))

const createEmptyDatabaseForm = () => ({
  name: '',
  description: '',
  embed_model_name: configStore.config?.embed_model,
  kb_type: 'milvus',
  is_private: false,
  storage: '',
  chunk_preset_id: 'general',
  use_chunk_parser_override: false,
  chunk_parser_config: {
    chunk_token_num: 512,
    overlapped_percent: 10,
    delimiter: '\n',
    raptor_use: true,
    graphrag_use: true
  },
  language: 'Chinese',
  llm_info: {
    provider: '',
    model_name: ''
  },
  dify_api_url: '',
  dify_token: '',
  dify_dataset_id: ''
})

const newDatabase = reactive(createEmptyDatabaseForm())

const selectedPresetDescription = computed(() =>
  getChunkPresetDescription(newDatabase.chunk_preset_id)
)

const selectedPresetLabel = computed(
  () =>
    chunkPresetOptions.find((item) => item.value === newDatabase.chunk_preset_id)?.label ||
    newDatabase.chunk_preset_id ||
    'General'
)

const backendConfigSummary = computed(() => {
  if (newDatabase.kb_type === 'dify') return 'Dify Dataset 只读桥接'
  const privacy = newDatabase.is_private ? '私有' : '公开'
  const storage = String(newDatabase.storage || '').trim() || '默认存储'
  return `${privacy} · ${storage}`
})

const chunkConfigSummary = computed(() => {
  if (newDatabase.kb_type === 'dify') return 'Dify 外部 Dataset'
  if (!newDatabase.use_chunk_parser_override) return `${selectedPresetLabel.value} 默认`

  const parser = newDatabase.chunk_parser_config || {}
  const raptor = parser.raptor_use ? 'RAPTOR 开' : 'RAPTOR 关'
  const graph = parser.graphrag_use ? 'GraphRAG 开' : 'GraphRAG 关'
  return `${parser.chunk_token_num || 512} token · ${parser.overlapped_percent || 0}% · ${raptor} · ${graph}`
})

const shareConfigSummary = computed(() => {
  if (shareConfig.value.is_shared) return '全员共享'
  const count = shareConfig.value.accessible_department_ids?.length || 0
  return count ? `指定 ${count} 个部门` : '指定部门'
})

const buildChunkParserConfig = () => {
  const config = {}
  const chunkTokenNum = Number(newDatabase.chunk_parser_config?.chunk_token_num || 0)
  const overlappedPercent = Number(newDatabase.chunk_parser_config?.overlapped_percent || 0)
  const delimiter = newDatabase.chunk_parser_config?.delimiter

  if (chunkTokenNum > 0) config.chunk_token_num = chunkTokenNum
  if (Number.isFinite(overlappedPercent)) {
    config.overlapped_percent = Math.max(0, Math.min(overlappedPercent, 99))
  }
  if (typeof delimiter === 'string' && delimiter.length) config.delimiter = delimiter

  config.raptor = {
    use_raptor: Boolean(newDatabase.chunk_parser_config?.raptor_use)
  }
  config.graphrag = {
    use_graphrag: Boolean(newDatabase.chunk_parser_config?.graphrag_use)
  }

  return config
}

const maskSensitiveCreatePayload = (payload) => {
  const cloned = JSON.parse(JSON.stringify(payload || {}))
  if (cloned.additional_params?.dify_token) {
    cloned.additional_params.dify_token = '***'
  }
  return cloned
}

const backendPayloadPreview = computed(() =>
  JSON.stringify(maskSensitiveCreatePayload(buildRequestData()), null, 2)
)

const llmModelSpec = computed(() => {
  const provider = newDatabase.llm_info?.provider || ''
  const modelName = newDatabase.llm_info?.model_name || ''
  if (provider && modelName) {
    return `${provider}/${modelName}`
  }
  return ''
})

const selectedEmbeddingStatus = computed(() => {
  const modelName = newDatabase.embed_model_name || configStore.config?.embed_model || ''
  return modelName ? embeddingStatuses.value?.[modelName] || null : null
})

const embeddingHealthText = computed(() => {
  if (newDatabase.kb_type === 'dify') return 'Dify 知识库由外部 Dataset 提供检索能力'
  if (state.embeddingStatusLoading) return '正在检查嵌入模型状态'
  if (state.embeddingStatusError) return state.embeddingStatusError
  if (!selectedEmbeddingStatus.value) return '尚未检查当前嵌入模型状态'

  const status = selectedEmbeddingStatus.value.status || 'unknown'
  const detail = selectedEmbeddingStatus.value.message || ''
  if (status === 'available') return detail ? `当前模型可用：${detail}` : '当前模型可用'
  if (status === 'unavailable') return detail ? `当前模型不可用：${detail}` : '当前模型不可用'
  if (status === 'error') return detail ? `当前模型检查失败：${detail}` : '当前模型检查失败'
  return '当前模型状态未知'
})

const embeddingHealthClass = computed(() => {
  if (state.embeddingStatusError) return 'warning'
  const status = selectedEmbeddingStatus.value?.status
  if (status === 'available') return 'success'
  if (status === 'unavailable' || status === 'error') return 'warning'
  return ''
})

const selectedKbTypeCapabilityTitle = computed(() => {
  if (newDatabase.kb_type === 'dify') return 'Dify Dataset 检索桥'
  if (newDatabase.kb_type === 'lightrag') return 'LightRAG 图谱知识链'
  return '文档向量库知识链'
})

const selectedCapabilityItems = computed(() => {
  if (newDatabase.kb_type === 'dify') {
    return [
      { title: '只读检索', description: '通过 Dataset Retrieve API 接入外部知识库', icon: Search },
      { title: '智能体工具', description: '名称和描述会参与 Agent 工具选择', icon: GitBranch },
      { title: '主题模块', description: '可绑定为 Worldline 模块入口', icon: Network }
    ]
  }

  const commonItems = [
    { title: '上传/URL', description: '文件、文件夹和网页抓取入口', icon: FileText },
    { title: '解析/入库', description: '手动解析、索引和后台任务追踪', icon: Database },
    { title: '查询测试', description: '查询参数、样例问题和检索调试', icon: Search }
  ]

  if (newDatabase.kb_type === 'lightrag') {
    commonItems.push({
      title: '图谱闭环',
      description: '实体关系、Neo4j 投影和 Worldline Graph',
      icon: Network
    })
  }

  commonItems.push({
    title: '质量门禁',
    description: 'Worldline Wiki、Graph、Timeline 与 Gate 入口',
    icon: ShieldCheck
  })

  return commonItems
})

// 支持的知识库类型
const supportedKbTypes = ref({})

// 有序的知识库类型
const orderedKbTypes = computed(() => supportedKbTypes.value)

// 加载支持的知识库类型
const loadSupportedKbTypes = async () => {
  try {
    const data = await typeApi.getKnowledgeBaseTypes()
    supportedKbTypes.value = data.kb_types
    console.log('支持的知识库类型:', supportedKbTypes.value)
  } catch (error) {
    console.error('加载知识库类型失败:', error)
    // 如果加载失败，设置默认类型
    supportedKbTypes.value = {
      lightrag: {
        description: '基于图检索的知识库，支持实体关系构建和复杂查询',
        class_name: 'LightRagKB'
      }
    }
  }
}

const loadEmbeddingStatuses = async () => {
  if (newDatabase.kb_type === 'dify') return

  state.embeddingStatusLoading = true
  state.embeddingStatusError = ''
  try {
    const response = await embeddingApi.getAllModelsStatus()
    embeddingStatuses.value = response?.status?.models || {}
  } catch (error) {
    console.error('检查嵌入模型状态失败:', error)
    state.embeddingStatusError = error.message || '嵌入模型状态检查失败'
  } finally {
    state.embeddingStatusLoading = false
  }
}

// 重排序模型信息现在直接从 configStore.config.reranker_names 获取，无需单独加载

const resetNewDatabase = () => {
  Object.assign(newDatabase, createEmptyDatabaseForm())
  // 重置共享配置
  shareConfig.value = {
    is_shared: true,
    accessible_department_ids: []
  }
}

const closeCreateDrawers = () => {
  state.backendConfigDrawerOpen = false
  state.chunkParserDrawerOpen = false
  state.shareConfigDrawerOpen = false
  state.payloadPreviewDrawerOpen = false
}

const cancelCreateDatabase = () => {
  state.openNewDatabaseModel = false
  closeCreateDrawers()
  resetNewDatabase()
}

const openCreateDatabaseModal = () => {
  state.openNewDatabaseModel = true
  loadEmbeddingStatuses()
}

const openBackendConfigDrawer = () => {
  state.backendConfigDrawerOpen = true
}

const openChunkParserDrawer = () => {
  if (newDatabase.kb_type === 'dify') return
  state.chunkParserDrawerOpen = true
}

const openShareConfigDrawer = () => {
  state.shareConfigDrawerOpen = true
}

const openBackendPayloadPreview = () => {
  state.payloadPreviewDrawerOpen = true
}

// 格式化创建时间
const formatCreatedTime = (createdAt) => {
  if (!createdAt) return ''
  const parsed = parseToShanghai(createdAt)
  if (!parsed) return ''

  const today = dayjs().startOf('day')
  const createdDay = parsed.startOf('day')
  const diffInDays = today.diff(createdDay, 'day')

  if (diffInDays === 0) {
    return '今天创建'
  }
  if (diffInDays === 1) {
    return '昨天创建'
  }
  if (diffInDays < 7) {
    return `${diffInDays} 天前创建`
  }
  if (diffInDays < 30) {
    const weeks = Math.floor(diffInDays / 7)
    return `${weeks} 周前创建`
  }
  if (diffInDays < 365) {
    const months = Math.floor(diffInDays / 30)
    return `${months} 个月前创建`
  }
  const years = Math.floor(diffInDays / 365)
  return `${years} 年前创建`
}

// 处理知识库类型改变
const handleKbTypeChange = (type) => {
  console.log('知识库类型改变:', type)
  closeCreateDrawers()
  resetNewDatabase()
  newDatabase.kb_type = type
  if (type !== 'dify') {
    loadEmbeddingStatuses()
  }
}

// 处理LLM选择
const handleLLMSelect = (spec) => {
  console.log('LLM选择:', spec)
  if (typeof spec !== 'string' || !spec) return

  const index = spec.indexOf('/')
  const provider = index !== -1 ? spec.slice(0, index) : ''
  const modelName = index !== -1 ? spec.slice(index + 1) : ''

  newDatabase.llm_info.provider = provider
  newDatabase.llm_info.model_name = modelName
}

// 构建请求数据（只负责表单数据转换）
const buildRequestData = () => {
  const requestData = {
    database_name: newDatabase.name.trim(),
    description: newDatabase.description?.trim() || '',
    kb_type: newDatabase.kb_type,
    additional_params: {}
  }

  if (newDatabase.kb_type !== 'dify') {
    requestData.embed_model_name = newDatabase.embed_model_name || configStore.config.embed_model
    requestData.additional_params.is_private = newDatabase.is_private || false
    requestData.additional_params.chunk_preset_id = newDatabase.chunk_preset_id || 'general'
    const storage = String(newDatabase.storage || '').trim()
    if (storage) {
      requestData.additional_params.storage = storage
    }
    if (newDatabase.use_chunk_parser_override) {
      requestData.additional_params.chunk_parser_config = buildChunkParserConfig()
    }
  }

  // 添加共享配置
  requestData.share_config = {
    is_shared: shareConfig.value.is_shared,
    accessible_departments: shareConfig.value.is_shared
      ? []
      : shareConfig.value.accessible_department_ids || []
  }

  if (newDatabase.kb_type === 'lightrag') {
    requestData.additional_params.language = newDatabase.language || 'English'
    if (newDatabase.llm_info.provider && newDatabase.llm_info.model_name) {
      requestData.llm_info = {
        provider: newDatabase.llm_info.provider,
        model_name: newDatabase.llm_info.model_name
      }
    }
  }

  if (newDatabase.kb_type === 'dify') {
    requestData.additional_params.dify_api_url = (newDatabase.dify_api_url || '').trim()
    requestData.additional_params.dify_token = (newDatabase.dify_token || '').trim()
    requestData.additional_params.dify_dataset_id = (newDatabase.dify_dataset_id || '').trim()
  }

  return requestData
}

// 创建按钮处理
const handleCreateDatabase = async () => {
  if (newDatabase.kb_type === 'dify') {
    if (
      !newDatabase.dify_api_url?.trim() ||
      !newDatabase.dify_token?.trim() ||
      !newDatabase.dify_dataset_id?.trim()
    ) {
      message.error('请完整填写 Dify API URL、Token 和 Dataset ID')
      return
    }
    if (!newDatabase.dify_api_url.trim().endsWith('/v1')) {
      message.error('Dify API URL 必须以 /v1 结尾')
      return
    }
  }

  const requestData = buildRequestData()
  try {
    const result = await databaseStore.createDatabase(requestData)
    if (!result) return
    lastCreatedDatabase.value = resolveCreatedDatabase(result, requestData)
    closeCreateDrawers()
    resetNewDatabase()
    state.openNewDatabaseModel = false
  } catch {
    // 错误已在 store 中处理
  }
}

const resolveCreatedDatabase = (result, requestData) => {
  const createdId =
    result?.db_id ||
    result?.id ||
    result?.database?.db_id ||
    result?.database?.id ||
    result?.data?.db_id ||
    result?.data?.id ||
    ''
  const byId = createdId ? databases.value.find((item) => item.db_id === createdId) : null
  if (byId) return byId

  const byName = databases.value.find((item) => item.name === requestData.database_name)
  if (byName) return byName

  return {
    db_id: createdId,
    name: requestData.database_name,
    kb_type: requestData.kb_type,
    description: requestData.description
  }
}

const navigateToDatabase = (databaseId) => {
  router.push({ path: `/database/${databaseId}` })
}

const openGraphForDatabase = (database) => {
  if (!database?.db_id) return
  router.push({
    path: '/graph',
    query: {
      db_id: database.db_id,
      knowledge_db_id: database.db_id
    }
  })
}

const openThemeModuleForDatabase = (database) => {
  if (!database?.db_id) return
  router.push({
    path: '/themes',
    query: {
      new_module: '1',
      db_id: database.db_id,
      knowledge_db_id: database.db_id,
      knowledge_name: database.name || database.db_id,
      knowledge_description: database.description || '',
      knowledge_type: database.kb_type || '',
      name: `${database.name || database.db_id} 世界线`
    }
  })
}

watch(
  () => route.path,
  (newPath) => {
    if (newPath === '/database') {
      databaseStore.loadDatabases()
    }
  }
)

onMounted(() => {
  loadSupportedKbTypes()
  databaseStore.loadDatabases()
  loadEmbeddingStatuses()
})
</script>

<style lang="less" scoped>
.new-database-modal {
  .chunk-preset-title-row {
    margin-top: 20px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .chunk-preset-help-icon {
    color: var(--gray-500);
    cursor: help;
    font-size: 14px;
  }

  .kb-type-guide {
    margin: 12px 0;
  }

  .privacy-config {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
  }

  .kb-type-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 16px 0;

    @media (max-width: 768px) {
      grid-template-columns: 1fr;
      gap: 12px;
    }

    .kb-type-card {
      border: 2px solid var(--gray-150);
      border-radius: 12px;
      padding: 16px;
      cursor: pointer;
      transition: all 0.3s ease;
      background: var(--gray-0);
      position: relative;
      overflow: hidden;

      &:hover {
        border-color: var(--main-color);
      }

      &.active {
        border-color: var(--main-color);
        background: var(--main-10);
        .type-icon {
          color: var(--main-color);
        }
      }

      .card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;

        .type-icon {
          width: 24px;
          height: 24px;
          color: var(--main-color);
          flex-shrink: 0;
        }

        .type-title {
          font-size: 16px;
          font-weight: 600;
          color: var(--gray-800);
        }
      }

      .card-description {
        font-size: 13px;
        color: var(--gray-600);
        line-height: 1.5;
        margin-bottom: 0;
        // min-height: 40px;
      }

      .deprecated-badge {
        background: var(--color-error-100);
        color: var(--color-error-600);
        font-size: 10px;
        font-weight: 600;
        padding: 2px 6px;
        border-radius: 4px;
        margin-left: auto;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        cursor: help;
        transition: all 0.2s ease;

        &:hover {
          background: var(--color-error-200);
          color: var(--color-error-700);
        }
      }
    }
  }

  .chunk-config {
    margin-top: 16px;
    padding: 12px 16px;
    background-color: var(--gray-25);
    border-radius: 6px;
    border: 1px solid var(--gray-150);

    h3 {
      margin-top: 0;
      margin-bottom: 12px;
      color: var(--gray-800);
    }

    .chunk-params {
      display: flex;
      flex-direction: column;
      gap: 12px;

      .param-row {
        display: flex;
        align-items: center;
        gap: 12px;

        label {
          min-width: 80px;
          font-weight: 500;
          color: var(--gray-700);
        }

        .param-hint {
          font-size: 12px;
          color: var(--gray-500);
          margin-left: 8px;
        }
      }
    }
  }
}

.database-container {
  .databases {
    .database {
      .top {
        .info {
          h3 {
            display: block;
          }
        }
      }
    }
  }
}
.database-actions,
.document-actions {
  margin-bottom: 20px;
}
.databases {
  padding: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.database,
.graphbase {
  background: linear-gradient(145deg, var(--gray-0) 0%, var(--gray-10) 100%);
  box-shadow: 0px 1px 2px 0px var(--shadow-2);
  border: 1px solid var(--gray-100);
  transition: none;
  position: relative;
}

.dbcard,
.database {
  width: 100%;
  padding: 16px;
  border-radius: 16px;
  height: 156px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  position: relative; // 为绝对定位的锁定图标提供参考
  overflow: hidden;

  .private-lock-icon {
    position: absolute;
    top: 20px;
    right: 20px;
    color: var(--gray-600);
    background: linear-gradient(135deg, var(--gray-0) 0%, var(--gray-100) 100%);
    font-size: 12px;
    border-radius: 8px;
    padding: 6px;
    z-index: 2;
    box-shadow: 0px 2px 4px var(--shadow-2);
    border: 1px solid var(--gray-100);
  }

  .top {
    display: flex;
    align-items: center;
    height: 54px;
    margin-bottom: 14px;

    .icon {
      width: 54px;
      height: 54px;
      font-size: 26px;
      margin-right: 14px;
      display: flex;
      justify-content: center;
      align-items: center;
      background: var(--main-30);
      border-radius: 12px;
      border: 1px solid var(--gray-150);
      color: var(--main-color);
      position: relative;
    }

    .info {
      flex: 1;
      min-width: 0;

      h3,
      p {
        margin: 0;
        color: var(--gray-10000);
      }

      h3 {
        font-size: 17px;
        font-weight: 600;
        letter-spacing: -0.02em;
        line-height: 1.4;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      p {
        color: var(--gray-700);
        font-size: 13px;
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 4px;
        font-weight: 400;

        .created-time-inline {
          color: var(--gray-700);
          font-size: 11px;
          font-weight: 400;
          background: var(--gray-50);
          padding: 2px 6px;
          border-radius: 4px;
        }
      }
    }
  }

  .description {
    color: var(--gray-600);
    overflow: hidden;
    display: -webkit-box;
    line-clamp: 1;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    text-overflow: ellipsis;
    margin-bottom: 12px;
    font-size: 13px;
    font-weight: 400;
    flex: 1;
  }
}

.database-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  flex-direction: column;
  color: var(--gray-900);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
  text-align: center;

  .empty-title {
    font-size: 20px;
    font-weight: 600;
    color: var(--gray-900);
    margin: 0 0 12px 0;
    letter-spacing: -0.02em;
  }

  .empty-description {
    font-size: 14px;
    color: var(--gray-600);
    margin: 0 0 32px 0;
    line-height: 1.5;
    max-width: 320px;
  }

  .ant-btn {
    height: 44px;
    padding: 0 24px;
    font-size: 15px;
    font-weight: 500;
  }
}

.database-container {
  padding: 0;
}

.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 300px;
  gap: 16px;
}

.new-database-modal {
  h3 {
    margin-top: 10px;
  }
}

.create-modal-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.create-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.create-section-title,
.create-field > span {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--wl-text);
  font-size: 13px;
  font-weight: 900;
}

.create-section-title em,
.create-field em {
  color: var(--color-error-500);
  font-style: normal;
}

.create-field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;

  @media (max-width: 760px) {
    grid-template-columns: 1fr;
  }
}

.create-field {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 7px;
  margin: 0;
}

.compact-summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;

  @media (max-width: 760px) {
    grid-template-columns: 1fr;
  }
}

.compact-summary-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  min-height: 64px;
  padding: 10px 12px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.045);

  > div {
    display: flex;
    min-width: 0;
    flex-direction: column;
    gap: 3px;
  }

  span {
    color: var(--wl-muted);
    font-size: 11px;
    font-weight: 900;
  }

  strong {
    overflow: hidden;
    color: var(--wl-text);
    font-size: 13px;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .ant-btn {
    flex-shrink: 0;
  }

  .ant-btn .ant-btn-icon {
    display: inline-flex;
    align-items: center;
  }
}

.create-drawer-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

:global(.create-database-drawer .ant-drawer-content),
:global(.create-database-drawer .ant-drawer-header),
:global(.create-database-drawer .ant-drawer-body) {
  background: #07131d;
  color: var(--wl-text);
}

:global(.create-database-drawer .ant-drawer-content) {
  border-left: 1px solid var(--wl-border-strong);
}

:global(.create-database-drawer .ant-drawer-title),
:global(.create-database-drawer .ant-drawer-close) {
  color: var(--wl-text);
}

:global(.create-database-drawer .share-config-form .share-config-content) {
  border-color: var(--wl-border);
  background: rgba(var(--wl-cyan-rgb), 0.045);
}

:global(.create-database-drawer .share-config-form .share-hint) {
  color: var(--wl-muted);
}

.database-container {
  background: var(--wl-page-bg);
  color: var(--wl-text);

  :deep(.header-container) {
    border-bottom: 1px solid var(--wl-border);
    background: rgba(2, 5, 10, 0.72);
    color: var(--wl-text);
  }
}

.databases {
  padding: 22px;
}

.database,
.graphbase,
.dbcard {
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background:
    linear-gradient(145deg, rgba(var(--wl-cyan-rgb), 0.075), rgba(var(--wl-gold-rgb), 0.035)),
    var(--wl-panel);
  box-shadow: var(--wl-shadow-soft);
  color: var(--wl-text);
}

.dbcard,
.database {
  height: 164px;

  .private-lock-icon {
    border-color: var(--wl-border);
    background: rgba(var(--wl-cyan-rgb), 0.08);
    color: var(--wl-gold-soft);
    box-shadow: none;
  }

  .top {
    .icon {
      border-color: var(--wl-border);
      background: rgba(var(--wl-cyan-rgb), 0.1);
      color: var(--wl-cyan);
    }

    .info {
      h3,
      p {
        color: var(--wl-text);
      }

      p {
        color: var(--wl-muted);

        .created-time-inline {
          background: rgba(var(--wl-cyan-rgb), 0.07);
          color: var(--wl-muted);
        }
      }
    }
  }

  .description {
    color: var(--wl-muted);
  }
}

.empty-state,
.loading-container,
.database-empty {
  color: var(--wl-text);

  .empty-title,
  p {
    color: var(--wl-text);
  }

  .empty-description {
    color: var(--wl-muted);
  }
}

.new-database-modal {
  h3 {
    color: var(--wl-text);
  }

  p {
    color: var(--wl-muted) !important;
  }

  .kb-type-cards {
    &.compact {
      gap: 10px;
      margin: 0;

      .kb-type-card {
        min-height: 92px;
        padding: 11px;
      }

      .card-header {
        gap: 8px;
        margin-bottom: 7px;
      }

      .card-description {
        display: -webkit-box;
        overflow: hidden;
        line-clamp: 2;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        font-size: 12px;
        line-height: 1.45;
      }
    }

    .kb-type-card {
      border-color: var(--wl-border);
      border-radius: var(--wl-radius);
      background: rgba(var(--wl-cyan-rgb), 0.055);
      color: var(--wl-text);

      &:hover {
        border-color: var(--wl-border-strong);
        background: rgba(var(--wl-cyan-rgb), 0.08);
      }

      &.active {
        border-color: var(--wl-border-gold);
        background:
          linear-gradient(90deg, rgba(var(--wl-gold-rgb), 0.12), transparent 44%),
          rgba(var(--wl-cyan-rgb), 0.075);

        .type-icon {
          color: var(--wl-gold-soft);
        }
      }

      .card-header {
        .type-icon {
          color: var(--wl-cyan);
        }

        .type-title {
          color: var(--wl-text);
        }
      }

      .card-description {
        color: var(--wl-muted);
      }
    }
  }
}

.embedding-health-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 8px;
  padding: 8px 10px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.055);
  color: var(--wl-muted);
  font-size: 13px;
}

.embedding-health-strip.success {
  border-color: rgba(75, 222, 128, 0.32);
  color: #b9f8d0;
}

.embedding-health-strip.warning {
  border-color: rgba(var(--wl-gold-rgb), 0.38);
  color: var(--wl-gold-soft);
}

.backend-advanced-collapse {
  margin-top: 16px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background: rgba(var(--wl-cyan-rgb), 0.035);
}

.backend-advanced-collapse :deep(.ant-collapse-header) {
  color: var(--wl-text) !important;
  font-weight: 800;
}

.backend-advanced-collapse :deep(.ant-collapse-content-box) {
  padding-top: 0 !important;
}

.backend-advanced-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.backend-advanced-summary {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(0, 0, 0, 0.14);

  strong {
    color: var(--wl-text);
  }

  span {
    color: var(--wl-muted);
    font-size: 12px;
    line-height: 1.45;
  }
}

.backend-advanced-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;

  @media (max-width: 720px) {
    grid-template-columns: 1fr;
  }
}

.backend-advanced-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 78px;
  padding: 12px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(0, 0, 0, 0.14);

  > div {
    display: flex;
    min-width: 0;
    flex-direction: column;
    gap: 4px;
  }

  strong {
    color: var(--wl-text);
  }

  span {
    color: var(--wl-muted);
    font-size: 12px;
    line-height: 1.45;
  }

  .ant-input {
    max-width: 220px;
  }
}

.backend-advanced-item.inline {
  min-height: auto;
}

.chunk-override-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chunk-override-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;

  @media (max-width: 720px) {
    grid-template-columns: 1fr;
  }

  label,
  .chunk-override-toggles {
    display: flex;
    min-height: 76px;
    flex-direction: column;
    justify-content: center;
    gap: 8px;
    padding: 12px;
    border: 1px solid var(--wl-border);
    border-radius: var(--wl-radius-sm);
    background: rgba(0, 0, 0, 0.14);
  }

  label > span {
    color: var(--wl-muted);
    font-size: 12px;
    font-weight: 800;
  }
}

.chunk-override-toggles {
  flex-direction: row !important;
  align-items: center;
  justify-content: flex-start !important;
  flex-wrap: wrap;
}

.backend-payload-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  border: 1px dashed var(--wl-border);
  border-radius: var(--wl-radius-sm);
  color: var(--wl-muted);
  font-size: 12px;

  @media (max-width: 720px) {
    align-items: flex-start;
    flex-direction: column;
  }
}

.backend-payload-inline {
  padding: 12px;
  border: 1px solid var(--wl-border-gold);
  border-radius: var(--wl-radius-sm);
  background:
    linear-gradient(90deg, rgba(var(--wl-gold-rgb), 0.08), transparent 42%),
    rgba(0, 0, 0, 0.2);
}

.backend-payload-inline-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;

  > div {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  strong {
    color: var(--wl-text);
  }

  span {
    color: var(--wl-muted);
    font-size: 12px;
  }
}

.backend-payload-inline pre {
  max-height: 320px;
  margin: 0;
  overflow: auto;
  padding: 12px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(0, 0, 0, 0.28);
  color: var(--wl-text);
  font-size: 12px;
  line-height: 1.55;
  white-space: pre-wrap;
}

.create-capability-panel {
  margin-top: 18px;
  padding: 14px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background: rgba(var(--wl-cyan-rgb), 0.045);
}

.create-capability-panel.compact {
  margin-top: 0;
  padding: 12px;

  .capability-panel-head {
    margin-bottom: 9px;
  }

  .capability-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));

    @media (max-width: 760px) {
      grid-template-columns: 1fr;
    }
  }

  .capability-item {
    min-height: 58px;
    padding: 9px;
  }
}

.capability-panel-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;

  p {
    margin: 0 0 4px;
    color: var(--wl-gold);
    font-size: 11px;
    font-weight: 900;
    text-transform: uppercase;
  }

  h3 {
    margin: 0;
  }

  > span {
    padding: 5px 9px;
    border: 1px solid var(--wl-border);
    border-radius: 999px;
    color: var(--wl-muted);
    font-size: 12px;
    font-weight: 800;
  }
}

.capability-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.capability-item {
  display: grid;
  grid-template-columns: 26px minmax(0, 1fr);
  grid-template-areas:
    'icon title'
    'icon desc';
  align-items: center;
  column-gap: 8px;
  min-height: 68px;
  padding: 10px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(0, 0, 0, 0.16);

  svg {
    grid-area: icon;
    color: var(--wl-cyan);
  }

  strong {
    grid-area: title;
    color: var(--wl-text);
  }

  small {
    grid-area: desc;
    color: var(--wl-muted);
    line-height: 1.45;
  }
}

.creation-next-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin: 18px 22px 0;
  padding: 16px;
  border: 1px solid var(--wl-border-gold);
  border-radius: var(--wl-radius);
  background:
    linear-gradient(90deg, rgba(var(--wl-gold-rgb), 0.1), transparent 34%),
    rgba(var(--wl-cyan-rgb), 0.05);
  color: var(--wl-text);

  .eyebrow {
    margin: 0 0 4px;
    color: var(--wl-gold);
    font-size: 11px;
    font-weight: 900;
  }

  h3 {
    margin: 0;
    color: var(--wl-text);
    font-size: 18px;
    font-weight: 900;
  }

  span {
    color: var(--wl-muted);
    font-size: 12px;
  }
}

.next-action-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 760px) {
  :global(.new-database-modal) {
    top: 12px;
    width: calc(100vw - 24px) !important;
    max-width: calc(100vw - 24px);
    margin: 0 auto;
    padding-bottom: 12px;
  }

  :global(.new-database-modal .ant-modal-content) {
    overflow: hidden;
  }

  :global(.new-database-modal .ant-modal-body) {
    max-height: calc(100vh - 150px);
    overflow-x: hidden;
    overflow-y: auto;
    padding: 16px;
  }

  :global(.new-database-modal .ant-modal-footer) {
    padding: 10px 16px 14px;
  }

  :global(.create-database-drawer .ant-drawer-content-wrapper) {
    width: calc(100vw - 16px) !important;
    max-width: calc(100vw - 16px);
  }

  :global(.create-database-drawer .ant-drawer-body) {
    overflow-x: hidden;
    padding: 14px;
  }

  .capability-grid {
    grid-template-columns: 1fr;
  }

  .creation-next-actions {
    align-items: flex-start;
    flex-direction: column;
  }

  .next-action-buttons {
    justify-content: flex-start;
  }
}
</style>
