import request from '@/utils/request'

// 获取工作台统计数据
export function getDashboardStats() {
  return request({
    url: '/dashboard/stats',
    method: 'get'
  })
}

// 获取最近任务列表
export function getRecentTasks(params) {
  return request({
    url: '/dashboard/recent-tasks',
    method: 'get',
    params
  })
}

// 获取本周统计数据
export function getWeeklyStats() {
  return request({
    url: '/dashboard/weekly-stats',
    method: 'get'
  })
}

// 获取管理后台统计数据
export function getAdminStats() {
  return request({
    url: '/dashboard/admin/stats',
    method: 'get'
  })
}

// 获取管理后台图表数据
export function getAdminChartData(params) {
  return request({
    url: '/dashboard/admin/chart',
    method: 'get',
    params
  })
}

// 获取系统动态
export function getSystemActivities() {
  return request({
    url: '/dashboard/admin/activities',
    method: 'get'
  })
}

// 获取最新用户列表
export function getRecentUsers() {
  return request({
    url: '/dashboard/admin/recent-users',
    method: 'get'
  })
}

// 获取热门模板列表
export function getPopularTemplates() {
  return request({
    url: '/dashboard/admin/popular-templates',
    method: 'get'
  })
} 