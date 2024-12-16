import request from '@/utils/request'

// 登录
export function login(data) {
  return request({
    url: '/auth/token/',
    method: 'post',
    data: {
      username: data.username,
      password: data.password
    }
  })
}

// 注册
export function register(data) {
  return request({
    url: '/auth/users/register/',
    method: 'post',
    data
  })
}

// 退出登录
export function logout() {
  return request({
    url: '/auth/token/blacklist/',
    method: 'post',
    data: {
      refresh: localStorage.getItem('refresh_token')
    }
  })
}

// 获取当前用户信息
export function getUserInfo() {
  return request({
    url: '/auth/users/me/',
    method: 'get'
  })
}

export function changePassword(data) {
  return request({
    url: '/auth/users/change_password/',
    method: 'post',
    data
  })
}

// 刷新 token
export function refreshToken() {
  return request({
    url: '/auth/token/refresh/',
    method: 'post',
    data: {
      refresh: localStorage.getItem('refresh_token')
    }
  })
} 