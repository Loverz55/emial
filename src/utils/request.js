import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: '/api',
  timeout: 15000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const { response } = error
    
    if (response?.status === 401) {
      const userStore = useUserStore()
      
      // 尝试刷新 token
      try {
        const { data } = await refreshToken()
        userStore.token = data.access
        localStorage.setItem('token', data.access)
        
        // 重试失败的请求
        const config = error.config
        config.headers.Authorization = `Bearer ${data.access}`
        return service(config)
      } catch (refreshError) {
        // 如果刷新 token 失败，清除用户信息并跳转到登录页
        userStore.clearUserInfo()
        window.location.href = '/login'
        return Promise.reject(new Error('请重新登录'))
      }
    }
    
    ElMessage.error(response?.data?.detail || '请求失败')
    return Promise.reject(error)
  }
)

export default service 