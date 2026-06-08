import { ref, watch } from 'vue'
import { defineStore } from 'pinia'
import { theme } from 'ant-design-vue'

export const useThemeStore = defineStore('theme', () => {
  // 从 localStorage 读取保存的主题，默认为浅色
  const storedTheme = localStorage.getItem('theme')
  const isDark = ref(storedTheme === null ? true : storedTheme === 'dark')

  // 公共主题配置
  const commonTheme = {
    token: {
      fontFamily:
        "'HarmonyOS Sans SC', Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;",
      colorPrimary: '#7cf6ff',
      colorInfo: '#7cf6ff',
      colorSuccess: '#70f0bb',
      colorWarning: '#ffd36f',
      colorError: '#ff7b7b',
      borderRadius: 8,
      wireframe: false
    }
  }

  // 浅色主题配置
  const lightTheme = {
    ...commonTheme
  }

  // 深色主题配置
  const darkTheme = {
    ...commonTheme,
    algorithm: theme.darkAlgorithm,
    token: {
      ...commonTheme.token,
      colorBgBase: '#02050a',
      colorBgContainer: '#07111b',
      colorBgElevated: '#0b1621',
      colorBorder: 'rgba(124, 246, 255, 0.16)',
      colorText: '#f6fbff',
      colorTextSecondary: 'rgba(216, 251, 255, 0.68)',
      colorTextTertiary: 'rgba(216, 251, 255, 0.52)'
    }
  }

  // 当前主题配置
  const currentTheme = ref(isDark.value ? darkTheme : lightTheme)

  // 切换主题
  function toggleTheme() {
    setTheme(!isDark.value)
  }

  // 设置主题
  function setTheme(dark) {
    isDark.value = dark
    currentTheme.value = dark ? darkTheme : lightTheme
    localStorage.setItem('theme', dark ? 'dark' : 'light')
    updateDocumentTheme()
  }

  // 更新 document 的主题类
  function updateDocumentTheme() {
    if (isDark.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  // 初始化时设置主题
  updateDocumentTheme()

  return {
    isDark,
    currentTheme,
    toggleTheme,
    setTheme
  }
})
