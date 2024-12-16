import request from '@/utils/request'

export function getHistoryList(params) {
  return request({
    url: '/api/history/',
    method: 'get',
    params
  })
}

export function getHistoryDetail(id) {
  return request({
    url: `/api/history/${id}/`,
    method: 'get'
  })
}

export function getHistoryStats() {
  return request({
    url: '/api/history/statistics/',
    method: 'get'
  })
}

// 获取邮件发送历史记录
export function getEmailHistory(params) {
  return request({
    url: '/email/history/',
    method: 'get',
    params
  })
}

// 重新发送邮件
export function resendEmail(id) {
  return request({
    url: `/email/resend/${id}/`,
    method: 'post'
  })
} 