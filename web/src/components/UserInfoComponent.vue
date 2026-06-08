<template>
  <div class="user-info-component">
    <a-dropdown v-if="userStore.isLoggedIn" :trigger="['hover']">
      <button class="user-trigger" type="button" :data-align="showRole ? 'left' : 'center'">
        <span class="user-avatar">
          <img v-if="userStore.avatar" :src="userStore.avatar" :alt="userStore.username" class="avatar-image" />
          <CircleUser v-else :size="20" />
        </span>
        <span v-if="showRole" class="trigger-name">{{ userStore.username || userStore.userIdLogin }}</span>
      </button>
      <template #overlay>
        <a-menu class="user-menu">
          <a-menu-item key="profile" @click="openProfile">
            <div class="user-info-display">
              <div class="user-menu-username">{{ userStore.username || 'Worldline User' }}</div>
              <div class="user-menu-details">
                <span>ID: {{ userStore.userIdLogin }}</span>
                <span>{{ userRoleText }}</span>
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
          <a-menu-item key="theme" @click="toggleTheme" :icon="themeStore.isDark ? SunIcon : MoonIcon">
            <span class="menu-text">{{ themeStore.isDark ? '切换浅色模式' : '切换深色模式' }}</span>
          </a-menu-item>
          <a-menu-divider v-if="userStore.isAdmin" />
          <a-menu-item v-if="userStore.isSuperAdmin" key="debug" @click="showDebug = true" :icon="TerminalIcon">
            <span class="menu-text">调试面板</span>
          </a-menu-item>
          <a-menu-item v-if="userStore.isAdmin" key="setting" @click="goToSetting" :icon="SettingsIcon">
            <span class="menu-text">系统设置</span>
          </a-menu-item>
          <a-menu-item key="logout" @click="logout" :icon="LogOutIcon">
            <span class="menu-text">退出登录</span>
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>

    <button v-else-if="showButton" class="login-button" type="button" @click="goToLogin">登录</button>

    <a-modal
      v-model:open="profileModalVisible"
      title="个人资料"
      :footer="null"
      width="520px"
      class="profile-modal"
    >
      <div class="profile-content">
        <div class="avatar-section">
          <div class="avatar-display">
            <img v-if="userStore.avatar" :src="userStore.avatar" :alt="userStore.username" class="large-avatar" />
            <div v-else class="default-avatar">
              <CircleUser :size="58" />
            </div>
          </div>
          <a-upload :show-upload-list="false" :before-upload="beforeUpload" @change="handleAvatarChange" accept="image/*">
            <a-button type="primary" size="small" :loading="avatarUploading">
              <template #icon><Upload size="14" /></template>
              {{ userStore.avatar ? '更换头像' : '上传头像' }}
            </a-button>
          </a-upload>
          <div class="avatar-tips">支持 JPG、PNG，文件不超过 5MB。</div>
        </div>

        <div class="info-section">
          <div class="info-item">
            <span class="info-label">用户名</span>
            <span class="info-value">{{ userStore.username || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">用户 ID</span>
            <span class="info-value mono">{{ userStore.userIdLogin || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">手机号</span>
            <span class="info-value">{{ userStore.phoneNumber || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">角色</span>
            <a-tag :color="getRoleColor(userStore.userRole)" class="role-tag">{{ userRoleText }}</a-tag>
          </div>
          <div v-if="userStore.departmentId" class="info-item">
            <span class="info-label">部门</span>
            <span class="info-value">{{ userStore.departmentName || '默认部门' }}</span>
          </div>
        </div>

        <div class="actions-section">
          <a-space>
            <a-button @click="profileModalVisible = false">关闭</a-button>
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
import { computed, h, inject, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { useUserStore } from '@/stores/user'
import { useInfoStore } from '@/stores/info'
import { useThemeStore } from '@/stores/theme'
import DebugComponent from '@/components/DebugComponent.vue'
import SettingsModal from '@/components/SettingsModal.vue'
import { BookOpen, CircleUser, LayoutGrid, LogOut, Moon, Settings, Sun, Terminal, Upload } from 'lucide-vue-next'

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

const userRoleText = computed(() => {
  switch (userStore.userRole) {
    case 'superadmin':
      return '最高权限'
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
  router.push({ name: 'Home', query: { login: '1' } })
}

const goToLogin = () => {
  router.push({ name: 'Home', query: { login: '1' } })
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

  try {
    await userStore.getCurrentUser()
  } catch (error) {
    console.warn('Refresh user profile failed:', error)
  }
}

const getRoleColor = (role) => {
  switch (role) {
    case 'superadmin':
      return 'gold'
    case 'admin':
      return 'blue'
    case 'user':
      return 'green'
    default:
      return 'default'
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
  try {
    avatarUploading.value = true
    await userStore.uploadAvatar(info.file.originFileObj || info.file)
    message.success('头像上传成功')
  } catch (error) {
    console.warn('Upload avatar failed:', error)
    message.error(`头像上传失败：${error.message || '请稍后重试'}`)
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
  color: var(--wl-text);
}

.user-trigger,
.login-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 36px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.06);
  color: var(--wl-text-soft);
  cursor: pointer;
  font-weight: 800;
}

.user-trigger {
  width: 100%;
  gap: 8px;
  padding: 2px 8px;
}

.user-trigger[data-align='center'] {
  justify-content: center;
}

.user-trigger[data-align='left'] {
  justify-content: flex-start;
}

.login-button {
  padding: 0 12px;
}

.user-avatar {
  width: 30px;
  height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--wl-border);
  border-radius: 50%;
  overflow: hidden;
  color: var(--wl-cyan);
  background: rgba(var(--wl-cyan-rgb), 0.07);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.trigger-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-info-display {
  line-height: 1.45;
}

.user-menu-username {
  color: var(--wl-ink);
  font-size: 14px;
  font-weight: 800;
}

.user-menu-details {
  display: flex;
  gap: 12px;
  color: rgba(6, 16, 24, 0.68);
  font-size: 12px;
}

.menu-text {
  line-height: 20px;
}

.profile-content {
  display: grid;
  gap: 20px;
}

.avatar-section {
  display: grid;
  justify-items: center;
  gap: 10px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--wl-border);
}

.avatar-display,
.large-avatar,
.default-avatar {
  width: 80px;
  height: 80px;
}

.large-avatar,
.default-avatar {
  border: 1px solid var(--wl-border);
  border-radius: 50%;
}

.large-avatar {
  object-fit: cover;
}

.default-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--wl-cyan);
  background: rgba(var(--wl-cyan-rgb), 0.07);
}

.avatar-tips {
  color: var(--wl-muted);
  font-size: 12px;
}

.info-section {
  display: grid;
  gap: 10px;
}

.info-item {
  display: grid;
  grid-template-columns: 86px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(var(--wl-cyan-rgb), 0.1);
}

.info-label {
  color: var(--wl-muted-soft);
  font-weight: 800;
}

.info-value {
  color: var(--wl-text);
}

.mono {
  font-family: Monaco, Consolas, monospace;
}

.actions-section {
  display: flex;
  justify-content: center;
  padding-top: 6px;
}

:deep(.ant-modal-content),
:deep(.ant-modal-header) {
  background: var(--wl-panel-solid);
  color: var(--wl-text);
}

:deep(.ant-modal-title) {
  color: var(--wl-text);
  font-weight: 900;
}

:deep(.ant-modal-close) {
  color: var(--wl-muted);
}

:deep(.ant-dropdown-menu-item svg) {
  margin-right: 4px;
  vertical-align: middle;
}
</style>
