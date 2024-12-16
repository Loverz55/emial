import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // 从本地存储获取主题状态，默认为 false（浅色主题）
  const isDark = ref(localStorage.getItem('theme') === 'dark')

  // 设置主题
  const setTheme = (dark) => {
    isDark.value = dark
    // 保存到本地存储
    localStorage.setItem('theme', dark ? 'dark' : 'light')
    // 修改 html 标签的类名来切换主题
    if (dark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    // 修改 Element Plus 的主题
    document.documentElement.className = dark ? 'dark' : ''
  }

  // 初始化主题
  const initTheme = () => {
    setTheme(isDark.value)
  }

  return {
    isDark,
    setTheme,
    initTheme
  }
}) 