<template>
  <a-modal
    v-model:open="visible"
    title="上传评估基准"
    width="600px"
    :confirmLoading="uploading"
    @ok="handleUpload"
    @cancel="handleCancel"
  >
    <a-form ref="formRef" :model="formState" :rules="rules" layout="vertical">
      <a-form-item label="基准名称" name="name">
        <a-input v-model:value="formState.name" placeholder="请输入评估基准名称" />
      </a-form-item>

      <a-form-item label="描述" name="description">
        <a-textarea
          v-model:value="formState.description"
          placeholder="请输入评估基准描述（可选）"
          :rows="3"
        />
      </a-form-item>

      <a-form-item label="基准文件" name="file" :extra="extraText">
        <a-upload-dragger
          v-model:fileList="fileList"
          name="file"
          :multiple="false"
          accept=".jsonl"
          :before-upload="beforeUpload"
          @remove="handleRemove"
        >
          <p class="ant-upload-text">
            <FileTextOutlined />
            点击或拖拽文件到此区域上传
          </p>
          <p class="ant-upload-hint">仅支持 JSONL 格式文件（.jsonl）</p>
        </a-upload-dragger>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup>
import { computed, h, reactive, ref, watch } from 'vue'
import { FileTextOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { evaluationApi } from '@/apis/knowledge_api'
import { useInfoStore } from '@/stores/info'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  databaseId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:visible', 'success'])
const infoStore = useInfoStore()
const formRef = ref()
const fileList = ref([])
const uploading = ref(false)

const formState = reactive({
  name: '',
  description: '',
  file: null
})

const rules = {
  name: [
    { required: true, message: '请输入基准名称', trigger: 'blur' },
    { min: 2, max: 100, message: '基准名称长度应在 2-100 个字符之间', trigger: 'blur' }
  ],
  file: [{ required: true, message: '请选择基准文件', trigger: 'change' }]
}

const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const evaluationGuideUrl = computed(() => infoStore.resolveDocsUrl('06-platform-operations') || infoStore.docsUrl || '#')

const extraText = computed(() =>
  h('span', {}, [
    '需要了解评估基准格式？查看',
    h(
      'a',
      {
        href: evaluationGuideUrl.value,
        target: '_blank',
        rel: 'noopener noreferrer'
      },
      '使用说明'
    )
  ])
)

const beforeUpload = async (file) => {
  if (!file.name.endsWith('.jsonl')) {
    message.error('仅支持 JSONL 格式文件')
    return false
  }

  const isLt100M = file.size / 1024 / 1024 < 100
  if (!isLt100M) {
    message.error('文件大小不能超过 100MB')
    return false
  }

  try {
    const content = await new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (event) => resolve(event.target.result)
      reader.onerror = () => reject(new Error('文件读取失败'))
      reader.readAsText(file)
    })

    const lines = content.trim().split('\n')
    if (lines.length === 0) {
      message.error('文件不能为空')
      return false
    }

    for (let index = 0; index < Math.min(5, lines.length); index += 1) {
      const line = lines[index].trim()
      if (line) {
        JSON.parse(line)
      }
    }

    formState.file = file
    return true
  } catch (error) {
    if (error instanceof SyntaxError) {
      message.error('文件格式错误，请检查 JSONL 格式')
    } else {
      message.error(`文件验证失败: ${error.message}`)
    }
    return false
  }
}

const handleRemove = () => {
  formState.file = null
}

const handleUpload = async () => {
  try {
    await formRef.value.validate()

    if (!formState.file) {
      message.error('请选择基准文件')
      return
    }

    uploading.value = true

    const response = await evaluationApi.uploadBenchmark(props.databaseId, formState.file, {
      name: formState.name,
      description: formState.description
    })

    if (response.message === 'success') {
      message.success('上传成功')
      handleCancel()
      emit('success')
    } else {
      message.error(response.message || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)
    message.error('上传失败')
  } finally {
    uploading.value = false
  }
}

const handleCancel = () => {
  visible.value = false
  resetForm()
}

const resetForm = () => {
  formRef.value?.resetFields()
  fileList.value = []
  formState.file = null
  uploading.value = false
}

watch(visible, (value) => {
  if (!value) {
    resetForm()
  }
})
</script>

<style lang="less" scoped>
:deep(.ant-upload-dragger) {
  .ant-upload-text {
    font-size: 16px;
    color: var(--gray-700);

    .anticon {
      font-size: 48px;
      color: var(--gray-400);
      margin-bottom: 16px;
    }
  }

  .ant-upload-hint {
    color: var(--gray-500);
  }
}
</style>
