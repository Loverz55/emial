import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login, logout, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    username: '',
    avatar: '',
    isAdmin: false
  }),
  actions: {
    clearUserInfo() {
      this.token = ''
      this.username = ''
      this.avatar = ''
      this.isAdmin = false
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
    },
    // 登录
    async loginAction(loginForm) {
      try {
        const { data } = await login(loginForm)
        const { access, refresh, user } = data
        this.token = access
        this.isAdmin = user.is_admin
        localStorage.setItem('token', access)
        localStorage.setItem('refresh_token', refresh)
        await this.getInfo()
        return data
      } catch (error) {
        this.clearUserInfo()
        throw error
      }
    },
    // 获取用户信息
    async getInfo() {
      try {
        const { data } = await getUserInfo()
        this.username = data.username
        this.avatar = data.avatar || ''
        this.isAdmin = data.is_admin
        return data
      } catch (error) {
        this.clearUserInfo()
        throw error
      }
    },
    // 退出登录
    async logoutAction() {
      try {
        await logout()
        this.clearUserInfo()
        return { code: 200, detail: '退出成功' }
      } catch (error) {
        console.error('Logout error:', error)
        this.clearUserInfo()
        throw error
      }
    }
  },
  persist: {
    key: 'user-store',
    storage: localStorage,
    paths: ['token', 'username', 'avatar', 'isAdmin']
  }
}) 