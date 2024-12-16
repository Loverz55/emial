import request from '@/utils/request'

export function getEmailTasks(params) {
  return request({
    url: '/api/email-tasks',
    method: 'get',
    params
  })
}

export function createEmailTask(data) {
  return request({
    url: '/api/email-tasks',
    method: 'post',
    data
  })
}

export function updateEmailTask(id, data) {
  return request({
    url: `/api/email-tasks/${id}`,
    method: 'put',
    data
  })
}

export function deleteEmailTask(id) {
  return request({
    url: `/api/email-tasks/${id}`,
    method: 'delete'
  })
}

export function toggleTaskStatus(id, status) {
  return request({
    url: `/api/email-tasks/${id}/status`,
    method: 'put',
    data: { status }
  })
} 