<template>
  <a-modal
    :open="props.modelValue"
    title="检索配置"
    width="860px"
    :confirm-loading="saving"
    @cancel="handleCancel"
  >
    <template #footer>
      <div class="modal-footer">
        <a-button :disabled="loading || saving || queryParams.length === 0" @click="resetToDefaults">
          <template #icon>
            <RotateCcw :size="14" />
          </template>
          恢复默认
        </a-button>
        <div class="footer-actions">
          <a-button :disabled="saving" @click="handleCancel">取消</a-button>
          <a-button
            type="primary"
            :loading="saving"
            :disabled="loading || queryParams.length === 0"
            @click="handleSave"
          >
            <template #icon>
              <Save :size="14" />
            </template>
            保存到后端
          </a-button>
        </div>
      </div>
    </template>

    <div class="search-config-modal">
      <div v-if="loading" class="config-loading">
        <a-spin size="large" />
        <p>正在读取后端检索参数...</p>
      </div>

      <div v-else-if="error" class="config-error">
        <a-result status="error" title="配置加载失败" :sub-title="error">
          <template #extra>
            <a-button type="primary" @click="loadQueryParams">
              <template #icon>
                <RefreshCw :size="14" />
              </template>
              重新加载
            </a-button>
          </template>
        </a-result>
      </div>

      <div v-else class="config-body">
        <section class="contract-strip">
          <div class="contract-main">
            <span class="eyebrow">后端联通</span>
            <h3>{{ kbTypeLabel }} 检索参数</h3>
            <p>
              参数来自 <code>GET /query-params</code>，保存后写入
              <code>PUT /query-params</code>，检索测试与评估会使用同一份
              <code>store.meta</code>。
            </p>
          </div>
          <div class="contract-tags">
            <a-tag color="cyan">{{ kbTypeLabel }}</a-tag>
            <a-tag color="blue">{{ queryParams.length }} 项参数</a-tag>
          </div>
        </section>

        <div v-if="summaryParams.length > 0" class="summary-grid">
          <div v-for="param in summaryParams" :key="param.key" class="summary-card">
            <span class="summary-label">{{ getParamLabel(param) }}</span>
            <strong>{{ formatParamValue(param) }}</strong>
            <small>{{ getParamShortDescription(param) }}</small>
          </div>
        </div>

        <a-alert
          v-if="queryParams.length === 0"
          type="info"
          show-icon
          message="当前知识库没有可配置的检索参数"
          description="请确认后端知识库类型是否已经初始化完成。"
        />

        <a-collapse
          v-else
          v-model:activeKey="activeGroupKeys"
          class="param-collapse"
          :bordered="false"
        >
          <a-collapse-panel v-for="group in groupedParams" :key="group.key">
            <template #header>
              <div class="group-header">
                <SlidersHorizontal :size="16" />
                <div>
                  <strong>{{ group.title }}</strong>
                  <span>{{ group.description }}</span>
                </div>
              </div>
            </template>

            <a-row :gutter="[16, 12]">
              <a-col v-for="param in group.params" :key="param.key" :xs="24" :lg="12">
                <a-form-item class="param-item" :label="getParamLabel(param)">
                  <a-select
                    v-if="param.type === 'select'"
                    v-model:value="meta[param.key]"
                    class="param-control"
                    :placeholder="`请选择${getParamLabel(param)}`"
                  >
                    <a-select-option
                      v-for="option in param.options || []"
                      :key="option.value"
                      :value="option.value"
                    >
                      <div class="option-content">
                        <span>{{ option.label }}</span>
                        <small v-if="option.description">{{ option.description }}</small>
                      </div>
                    </a-select-option>
                  </a-select>

                  <div v-else-if="param.type === 'boolean'" class="switch-control">
                    <a-switch
                      v-model:checked="meta[param.key]"
                      checked-children="启用"
                      un-checked-children="关闭"
                      @change="(value) => updateMeta(param.key, value)"
                    />
                    <span>{{ Boolean(meta[param.key]) ? '已启用' : '已关闭' }}</span>
                  </div>

                  <a-input-number
                    v-else-if="param.type === 'number'"
                    v-model:value="meta[param.key]"
                    class="param-control"
                    :min="param.min ?? 0"
                    :max="param.max ?? 100"
                    :step="getNumberStep(param)"
                  />

                  <a-input
                    v-else
                    v-model:value="meta[param.key]"
                    class="param-control"
                    :placeholder="`请输入${getParamLabel(param)}`"
                  />

                  <div v-if="param.description" class="param-description">
                    {{ param.description }}
                  </div>
                </a-form-item>
              </a-col>
            </a-row>
          </a-collapse-panel>
        </a-collapse>

        <a-collapse
          v-if="queryParams.length > 0"
          v-model:activeKey="payloadActiveKey"
          class="payload-collapse"
          :bordered="false"
        >
          <a-collapse-panel key="payload" header="后端请求预览">
            <div class="endpoint-row">
              <span>保存接口</span>
              <code>{{ endpointPath }}</code>
            </div>
            <pre>{{ payloadPreview }}</pre>
          </a-collapse-panel>
        </a-collapse>
      </div>
    </div>
  </a-modal>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useDatabaseStore } from '@/stores/database'
import { message } from 'ant-design-vue'
import { queryApi } from '@/apis/knowledge_api'
import { RefreshCw, RotateCcw, Save, SlidersHorizontal } from 'lucide-vue-next'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  databaseId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'save'])

const store = useDatabaseStore()

const loading = ref(false)
const saving = ref(false)
const error = ref('')
const queryParams = ref([])
const queryParamType = ref('')
const meta = reactive({})
const activeGroupKeys = ref([])
const payloadActiveKey = ref([])

const typeLabelMap = {
  milvus: 'CommonRAG',
  lightrag: 'LightRAG',
  dify: 'Dify'
}

const groupDefinitions = [
  {
    key: 'retrieval',
    title: '检索范围',
    description: '控制检索模式、召回数量和最终返回数量。',
    keys: ['search_mode', 'mode', 'final_top_k', 'top_k', 'recall_top_k', 'keyword_top_k']
  },
  {
    key: 'reranker',
    title: '重排序',
    description: '控制是否启用精排模型以及候选召回数量。',
    keys: ['use_reranker', 'enable_rerank', 'reranker_model']
  },
  {
    key: 'threshold',
    title: '阈值与输出',
    description: '控制过滤阈值、距离度量和结果分数展示。',
    keys: ['score_threshold_enabled', 'similarity_threshold', 'metric_type', 'include_distances']
  },
  {
    key: 'graph',
    title: '图谱上下文',
    description: '控制 LightRAG 返回图谱、文档片段或提示上下文。',
    keys: ['retrieval_content_scope', 'only_need_context', 'only_need_prompt']
  }
]

const summaryKeyOrder = [
  'search_mode',
  'mode',
  'final_top_k',
  'top_k',
  'use_reranker',
  'reranker_model',
  'score_threshold_enabled',
  'similarity_threshold',
  'retrieval_content_scope'
]

const kbTypeLabel = computed(() => {
  const type = queryParamType.value || store.database?.kb_type || ''
  return typeLabelMap[String(type).toLowerCase()] || type || '知识库'
})

const endpointPath = computed(
  () => `/api/knowledge/databases/${props.databaseId || '{db_id}'}/query-params`
)

const summaryParams = computed(() => {
  const byKey = new Map(queryParams.value.map((param) => [param.key, param]))
  const ordered = summaryKeyOrder.map((key) => byKey.get(key)).filter(Boolean)
  const remaining = queryParams.value.filter((param) => !summaryKeyOrder.includes(param.key))
  return [...ordered, ...remaining].slice(0, 4)
})

const groupedParams = computed(() => {
  const usedKeys = new Set()
  const groups = groupDefinitions
    .map((group) => {
      const keys = new Set(group.keys)
      const params = queryParams.value.filter((param) => keys.has(param.key))
      params.forEach((param) => usedKeys.add(param.key))
      return { ...group, params }
    })
    .filter((group) => group.params.length > 0)

  const advancedParams = queryParams.value.filter((param) => !usedKeys.has(param.key))
  if (advancedParams.length > 0) {
    groups.push({
      key: 'advanced',
      title: '高级参数',
      description: '后端暴露但不属于常用分组的参数。',
      params: advancedParams
    })
  }

  return groups
})

const payloadPreview = computed(() => JSON.stringify(buildPayload(), null, 2))

const getParamLabel = (param) => param.label || param.key

const getParamShortDescription = (param) => {
  if (param.description) return param.description
  if (param.type === 'boolean') return '布尔开关'
  if (param.type === 'number') return '数值参数'
  return param.key
}

const getNumberStep = (param) => {
  if (param.step !== undefined) return param.step
  if (param.max !== undefined && param.max <= 1) return 0.1
  return 1
}

const formatParamValue = (param) => {
  const value = meta[param.key]
  if (value === undefined || value === null || value === '') {
    return param.key === 'reranker_model' ? '未选择模型' : '未设置'
  }
  if (param.type === 'boolean') {
    return Boolean(value) ? '启用' : '关闭'
  }
  if (param.type === 'select') {
    const option = (param.options || []).find((item) => item.value === value)
    return option?.label || String(value)
  }
  return String(value)
}

const coerceParamValue = (param, value) => {
  if (param.type === 'boolean') {
    if (typeof value === 'boolean') return value
    if (typeof value === 'string') return value === 'true'
    return Boolean(value)
  }
  if (param.type === 'number') {
    if (value === '' || value === undefined || value === null) return value
    const numberValue = Number(value)
    return Number.isNaN(numberValue) ? value : numberValue
  }
  return value
}

const clearMeta = () => {
  Object.keys(meta).forEach((key) => {
    delete meta[key]
  })
}

const syncActiveGroups = () => {
  const keys = groupedParams.value.map((group) => group.key)
  activeGroupKeys.value = keys.filter((key) => key !== 'advanced').slice(0, 2)
}

const buildPayload = () => {
  const payload = {}
  queryParams.value.forEach((param) => {
    if (param.key in meta && meta[param.key] !== undefined) {
      payload[param.key] = coerceParamValue(param, meta[param.key])
    }
  })
  return payload
}

const updateMeta = (key, value) => {
  const param = queryParams.value.find((item) => item.key === key)
  meta[key] = param ? coerceParamValue(param, value) : value
}

const applyDefaults = () => {
  clearMeta()
  queryParams.value.forEach((param) => {
    if (param.default !== undefined) {
      meta[param.key] = coerceParamValue(param, param.default)
    }
  })
}

const loadQueryParams = async () => {
  try {
    loading.value = true
    error.value = ''

    if (!props.databaseId) {
      queryParams.value = []
      queryParamType.value = ''
      clearMeta()
      return
    }

    const response = await queryApi.getKnowledgeBaseQueryParams(props.databaseId)
    queryParams.value = response.params?.options || []
    queryParamType.value = response.params?.type || store.database?.kb_type || ''
    applyDefaults()
    syncActiveGroups()
  } catch (err) {
    console.error('Failed to load query params:', err)
    error.value = err.message || '加载查询参数失败'
  } finally {
    loading.value = false
  }
}

const resetToDefaults = () => {
  applyDefaults()
  syncActiveGroups()
  message.success('已恢复为后端默认配置')
}

const handleSave = async () => {
  if (!props.databaseId) {
    message.error('无法保存配置：缺少知识库 ID')
    return
  }

  const payload = buildPayload()

  try {
    saving.value = true
    const response = await queryApi.updateKnowledgeBaseQueryParams(props.databaseId, payload)
    if (response.message !== 'success') {
      throw new Error(response.message || '保存失败')
    }

    Object.keys(store.meta).forEach((key) => {
      if (!(key in payload)) {
        delete store.meta[key]
      }
    })
    Object.assign(store.meta, payload)
    await store.loadQueryParams(props.databaseId)

    message.success('检索配置已保存')
    emit('save', { ...payload })
    emit('update:modelValue', false)
  } catch (err) {
    console.error('保存配置到知识库失败:', err)
    message.error('保存配置失败：' + (err.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

const handleCancel = () => {
  emit('update:modelValue', false)
}

watch(
  () => props.modelValue,
  (visible) => {
    if (visible) {
      loadQueryParams()
    }
  }
)
</script>

<style lang="less" scoped>
.search-config-modal {
  min-height: 260px;
}

.config-loading,
.config-error {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  color: var(--gray-500);

  p {
    margin-top: 16px;
    font-size: 14px;
  }
}

.config-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.contract-strip {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 16px;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  background: var(--gray-25);
}

.contract-main {
  min-width: 0;

  h3 {
    margin: 2px 0 6px;
    color: var(--gray-900);
    font-size: 18px;
    font-weight: 700;
  }

  p {
    margin: 0;
    color: var(--gray-600);
    font-size: 13px;
    line-height: 1.7;
  }

  code {
    color: var(--main-color);
    font-size: 12px;
  }
}

.eyebrow {
  color: var(--main-color);
  font-size: 12px;
  font-weight: 700;
}

.contract-tags {
  display: flex;
  flex-shrink: 0;
  align-items: flex-start;
  gap: 6px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.summary-card {
  min-width: 0;
  padding: 12px;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  background: var(--gray-0);

  .summary-label,
  small {
    display: block;
    overflow: hidden;
    color: var(--gray-500);
    font-size: 12px;
    line-height: 1.5;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  strong {
    display: block;
    overflow: hidden;
    margin: 4px 0 2px;
    color: var(--gray-900);
    font-size: 17px;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.param-collapse,
.payload-collapse {
  border-radius: 8px;
  background: var(--gray-0);

  :deep(.ant-collapse-item) {
    border: 1px solid var(--gray-200);
    border-radius: 8px;
    margin-bottom: 10px;
    overflow: hidden;
  }

  :deep(.ant-collapse-header) {
    align-items: center;
    padding: 12px 14px;
    background: var(--gray-25);
  }

  :deep(.ant-collapse-content-box) {
    padding: 14px;
  }
}

.group-header {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--gray-800);

  div {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  span {
    color: var(--gray-500);
    font-size: 12px;
    line-height: 1.4;
  }
}

.param-item {
  margin-bottom: 0;

  :deep(.ant-form-item-label > label) {
    color: var(--gray-800);
    font-weight: 600;
  }
}

.param-control {
  width: 100%;
}

.switch-control {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 32px;
  color: var(--gray-600);
}

.param-description {
  margin-top: 6px;
  color: var(--gray-500);
  font-size: 12px;
  line-height: 1.5;
}

.option-content {
  display: flex;
  flex-direction: column;
  gap: 2px;

  small {
    color: var(--gray-500);
    font-size: 12px;
  }
}

.endpoint-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  color: var(--gray-600);
  font-size: 13px;

  code {
    color: var(--main-color);
    word-break: break-all;
  }
}

pre {
  max-height: 220px;
  margin: 0;
  padding: 12px;
  overflow: auto;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  background: var(--gray-25);
  color: var(--gray-900);
  font-size: 12px;
  line-height: 1.6;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
}

.footer-actions {
  display: flex;
  gap: 8px;
}

:deep(.ant-input),
:deep(.ant-input-number),
:deep(.ant-select-selector) {
  border-radius: 6px;
}

:deep(.ant-switch.ant-switch-checked) {
  background-color: var(--main-color);
}

@media (max-width: 900px) {
  .contract-strip {
    flex-direction: column;
  }

  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
