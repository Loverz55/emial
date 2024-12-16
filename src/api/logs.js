import request from '@/utils/request'

export function getLogsList(params) {
  return request({
    url: '/api/logs/',
    method: 'get',
    params
  })
}

export function getLogsDetail(id) {
  return request({
    url: `/api/logs/${id}/`,
    method: 'get'
  })
}

export function getLogsStats() {
  return request({
    url: '/api/logs/statistics/',
    method: 'get'
  })
} 