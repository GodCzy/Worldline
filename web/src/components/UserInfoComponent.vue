<template>
  <div class="user-info-component">
    <a-dropdown v-if="userStore.isLoggedIn" :trigger="['hover']">
      <div class="user-info-dropdown" :data-align="showRole ? 'left' : 'center'">
        <div class="user-avatar">
          <img
            v-if="userStore.avatar"
            :src="userStore.avatar"
            :alt="userStore.username"
            class="avatar-image"
          />
          <CircleUser v-else />
        </div>
        <div v-if="showRole">{{ userStore.username }}</div>
      </div>
      <template #overlay>
        <a-menu>
          <a-menu-item key="user-info" @click="openProfile">
            <div class="user-info-display">
              <div class="user-menu-username">{{ userStore.username }}</div>
              <div class="user-menu-details">
                <span class="user-menu-info">ID: {{ userStore.userIdLogin }}</span>
                <span class="user-menu-role">{{ userRoleText }}</span>
              </div>
            </div>
          </a-menu-item>
          <a-menu-divider />
          <a-menu-item key="themes" @click="openThemes" :icon="LayoutGridIcon">
            <span class="menu-text">主题分区</span>
          </a-menu-item>
          <a-menu-item key="docs" @click="openDocs" :icon="BookOpenIcon">
            <span class="menu-text">文档中心</span>
          </a-menu-item>
          <a-menu-item
            key="theme"
            @click="toggleTheme"
            :icon="themeStore.isDark ? SunIcon : MoonIcon"
          >
            <span class="menu-text">{{
              themeStore.isDark ? '切换到浅色模式' : '切换到深色模式'
            }}</span>
          </a-menu-item>
          <a-menu-divider v-if="userStore.isAdmin" />
          <a-menu-item
            v-if="userStore.isSuperAdmin"
            key="debug"
            @click="showDebug = true"
            :icon="TerminalIcon"
          >
            <span class="menu-text">调试面板（非生产环境）</span>
          </a-menu-item>
          <a-menu-item
            v-if="userStore.isAdmin"
            key="setting"
            @click="goToSetting"
            :icon="SettingsIcon"
          >
            <span class="menu-text">系统设置</span>
          </a-menu-item>
          <a-menu-item key="logout" @click="logout" :icon="LogOutIcon">
            <span class="menu-text">退出登录</span>
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
    <a-button v-else-if="showButton" type="primary" @click="goToLogin">登录</a-button>

    <a-modal
      v-model:open="profileModalVisible"
      title="个人资料"
      :footer="null"
      width="520px"
      class="profile-modal"
    >
      <div class="profile-content">
        <div class="avatar-section">
          <div class="avatar-container">
            <div class="avatar-display">
              <img
                v-if="userStore.avatar"
                :src="userStore.avatar"
                :alt="userStore.username"
                class="large-avatar"
              />
              <div v-else class="default-avatar">
                <CircleUser :size="60" />
              </div>
            </div>
            <div class="avatar-actions">
              <a-upload
                :show-upload-list="false"
                :before-upload="beforeUpload"
                @change="handleAvatarChange"
                accept="image/*"
              >
                <a-button type="primary" size="small" :loading="avatarUploading">
                  <template #icon><Upload size="14" /></template>
                  {{ userStore.avatar ? '更换头像' : '上传头像' }}
                </a-button>
              </a-upload>
              <div class="avatar-tips">支持 JPG、PNG 格式，文件不超过 5MB</div>
            </div>
          </div>
        </div>

        <div class="info-section">
          <div class="info-item">
            <div class="info-label">用户名</div>
            <div v-if="!profileEditing" class="info-value">
              {{ userStore.username || '未设置' }}
            </div>
            <div v-else class="info-value">
              <a-input
                v-model:value="editedProfile.username"
                placeholder="请输入用户名（2-20 个字符）"
                :max-length="20"
                style="width: 240px"
              />
            </div>
          </div>
          <div class="info-item">
            <div class="info-label">用户ID</div>
            <div v-if="!profileEditing" class="info-value user-id">
              {{ userStore.userIdLogin || '未设置' }}
            </div>
            <div v-else class="info-value">
              <a-input :value="userStore.userIdLogin || ''" disabled style="width: 240px" />
            </div>
          </div>
          <div class="info-item">
            <div class="info-label">手机号</div>
            <div v-if="!profileEditing" class="info-value">
              {{ userStore.phoneNumber || '未设置' }}
            </div>
            <div v-else class="info-value">
              <a-input
                v-model:value="editedProfile.phone_number"
                placeholder="请输入手机号"
                :max-length="11"
                style="width: 200px"
              />
            </div>
          </div>
          <div class="info-item">
            <div class="info-label">角色</div>
            <div class="info-value">
              <a-tag :color="getRoleColor(userStore.userRole)" class="role-tag">
                {{ userRoleText }}
              </a-tag>
            </div>
          </div>
          <div v-if="userStore.departmentId" class="info-item">
            <div class="info-label">部门</div>
            <div class="info-value">{{ userStore.departmentName || '默认部门' }}</div>
          </div>
        </div>

        <div class="actions-section">
          <a-space>
            <template v-if="!profileEditing">
              <a-button type="primary" @click="startEdit">编辑资料</a-button>
              <a-button @click="profileModalVisible = false">关闭</a-button>
            </template>
            <template v-else>
              <a-button type="primary" @click="saveProfile" :loading="avatarUploading">
                保存
              </a-button>
              <a-button @click="cancelEdit">取消</a-button>
            </template>
          </a-space>
        </div>
      </div>
    </a-modal>

    <SettingsModal
      v-if="showLocalSettingsModal"
      v-model:visible="showLocalSettingsModal"
      @close="showLocalSettingsModal = false"
    />

    <DebugComponent v-model:show="showDebug" />
  </div>
</template>

<script setup>
import { computed, ref, inject, h } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useInfoStore } from '@/stores/info'
import { useThemeStore } from '@/stores/theme'
import DebugComponent from '@/components/DebugComponent.vue'
import SettingsModal from '@/components/SettingsModal.vue'
import { message } from 'ant-design-vue'
import {
  CircleUser,
  BookOpen,
  LayoutGrid,
  Sun,
  Moon,
  LogOut,
  Upload,
  Settings,
  Terminal
} from 'lucide-vue-next'

const router = useRouter()
const userStore = useUserStore()
const infoStore = useInfoStore()
const themeStore = useThemeStore()

const BookOpenIcon = h(BookOpen, { size: '16' })
const LayoutGridIcon = h(LayoutGrid, { size: '16' })
const SunIcon = h(Sun, { size: '16' })
const MoonIcon = h(Moon, { size: '16' })
const TerminalIcon = h(Terminal, { size: '16' })
const SettingsIcon = h(Settings, { size: '16' })
const LogOutIcon = h(LogOut, { size: '16' })

const showDebug = ref(false)
const settingsModalApi = inject('settingsModal', null)
const showLocalSettingsModal = ref(false)
const profileModalVisible = ref(false)
const avatarUploading = ref(false)
const profileEditing = ref(false)
const editedProfile = ref({
  username: '',
  phone_number: ''
})

defineProps({
  showRole: {
    type: Boolean,
    default: false
  },
  showButton: {
    type: Boolean,
    default: false
  }
})

const userRoleText = computed(() => {
  switch (userStore.userRole) {
    case 'superadmin':
      return '超级管理员'
    case 'admin':
      return '管理员'
    case 'user':
      return '普通用户'
    default:
      return '未知角色'
  }
})

const docsUrl = computed(() => infoStore.docsUrl || '')

const logout = () => {
  userStore.logout()
  message.success('已退出登录')
  router.push('/login')
}

const goToLogin = () => {
  router.push('/login')
}

const openThemes = () => {
  router.push('/themes')
}

const openDocs = async () => {
  if (!docsUrl.value) {
    await infoStore.loadInfoConfig()
  }

  if (!infoStore.docsUrl) {
    message.warning('文档中心链接未配置')
    return
  }

  window.open(infoStore.docsUrl, '_blank', 'noopener,noreferrer')
}

const toggleTheme = () => {
  themeStore.toggleTheme()
}

const goToSetting = () => {
  if (settingsModalApi?.openSettingsModal) {
    settingsModalApi.openSettingsModal()
    return
  }

  showLocalSettingsModal.value = true
}

const openProfile = async () => {
  profileModalVisible.value = true
  profileEditing.value = false

  try {
    await userStore.getCurrentUser()
    editedProfile.value = {
      username: userStore.username || '',
      phone_number: userStore.phoneNumber || ''
    }
  } catch (error) {
    console.error('刷新用户信息失败:', error)
  }
}

const getRoleColor = (role) => {
  switch (role) {
    case 'superadmin':
      return 'red'
    case 'admin':
      return 'blue'
    case 'user':
      return 'green'
    default:
      return 'default'
  }
}

const startEdit = () => {
  profileEditing.value = true
  editedProfile.value = {
    username: userStore.username || '',
    phone_number: userStore.phoneNumber || ''
  }
}

const cancelEdit = () => {
  profileEditing.value = false
  editedProfile.value = {
    username: userStore.username || '',
    phone_number: userStore.phoneNumber || ''
  }
}

const validatePhoneNumber = (phone) => {
  if (!phone) return true
  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(phone)
}

const saveProfile = async () => {
  try {
    if (
      editedProfile.value.username &&
      (editedProfile.value.username.trim().length < 2 ||
        editedProfile.value.username.trim().length > 20)
    ) {
      message.error('用户名长度必须在 2-20 个字符之间')
      return
    }

    if (
      editedProfile.value.phone_number &&
      !validatePhoneNumber(editedProfile.value.phone_number)
    ) {
      message.error('请输入正确的手机号格式')
      return
    }

    await userStore.updateProfile({
      username: editedProfile.value.username?.trim() || undefined,
      phone_number: editedProfile.value.phone_number || undefined
    })
    message.success('个人资料更新成功')
    profileEditing.value = false
  } catch (error) {
    console.error('更新个人资料失败:', error)
    message.error('更新失败：' + (error.message || '请稍后重试'))
  }
}

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    message.error('只能上传图片文件')
    return false
  }

  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    message.error('图片大小不能超过 5MB')
    return false
  }

  return true
}

const handleAvatarChange = async (info) => {
  if (info.file.status === 'uploading') {
    avatarUploading.value = true
    return
  }

  if (info.file.status === 'done') {
    avatarUploading.value = false
    return
  }

  try {
    avatarUploading.value = true
    await userStore.uploadAvatar(info.file.originFileObj || info.file)
    message.success('头像上传成功')
  } catch (error) {
    console.error('头像上传失败:', error)
    message.error('头像上传失败：' + (error.message || '请稍后重试'))
  } finally {
    avatarUploading.value = false
  }
}
</script>

<style lang="less" scoped>
.user-info-component {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--gray-800);
}

.user-info-dropdown {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;

  &[data-align='center'] {
    justify-content: center;
  }

  &[data-align='left'] {
    justify-content: flex-start;
  }
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px var(--shadow-2);

  &:hover {
    opacity: 0.9;
  }

  .avatar-image {
    width: 100%;
    height: 100%;
    object-fit: contain;
    border-radius: 50%;
    border: 2px solid var(--gray-150);
  }
}

.user-info-display {
  line-height: 1.4;
}

.user-menu-username {
  font-weight: 600;
  color: var(--gray-900);
  font-size: 14px;
  display: block;
  margin-bottom: 2px;
}

.user-menu-details {
  display: flex;
  gap: 12px;
  align-items: center;
}

.user-menu-info {
  font-size: 12px;
  color: var(--gray-600);
}

.user-menu-role {
  font-size: 12px;
  color: var(--gray-500);
}

.profile-modal {
  :deep(.ant-modal-header) {
    padding: 20px 24px;
    border-bottom: 1px solid var(--gray-150);

    .ant-modal-title {
      font-size: 18px;
      font-weight: 600;
      color: var(--gray-900);
    }
  }

  :deep(.ant-modal-body) {
    padding: 24px;
  }
}

.profile-content {
  .avatar-section {
    text-align: center;
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--gray-150);

    .avatar-container {
      display: inline-block;

      .avatar-display {
        margin-bottom: 16px;

        .large-avatar {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          object-fit: cover;
          border: 3px solid var(--gray-150);
          box-shadow: 0 2px 8px var(--shadow-2);
        }

        .default-avatar {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          background: var(--gray-50);
          display: flex;
          margin: 0 auto;
          align-items: center;
          justify-content: center;
          border: 3px solid var(--gray-150);
          box-shadow: 0 2px 8px var(--shadow-2);

          :deep(svg) {
            color: var(--gray-400);
          }
        }
      }

      .avatar-actions {
        .avatar-tips {
          margin-top: 8px;
          font-size: 12px;
          color: var(--gray-500);
          line-height: 1.4;
        }
      }
    }
  }

  .info-section {
    margin-bottom: 24px;

    .info-item {
      display: flex;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid var(--gray-50);

      &:last-child {
        border-bottom: none;
      }

      .info-label {
        width: 80px;
        font-weight: 500;
        color: var(--gray-500);
        flex-shrink: 0;
      }

      .info-value {
        flex: 1;
        color: var(--gray-900);
        font-size: 14px;

        &.user-id {
          font-family: 'Monaco', 'Consolas', monospace;
          border-radius: 4px;
          display: inline-block;
        }
      }

      .role-tag {
        font-weight: 500;
        border-radius: 4px;
        padding: 4px 12px;
      }
    }
  }

  .actions-section {
    text-align: center;
    padding-top: 16px;
    border-top: 1px solid var(--gray-150);
  }
}

:deep(.ant-dropdown-menu) {
  padding: 8px 0;
}

:deep(.ant-dropdown-menu-title-content) {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--gray-900);
}

:deep(.ant-dropdown-menu-item svg) {
  margin-right: 4px;
  color: var(--gray-900);
  vertical-align: middle;
}

.menu-text {
  line-height: 20px;
}
</style>
