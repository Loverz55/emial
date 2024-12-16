import request from '@/utils/request'

// 获取模板列表
export function getTemplateList(params) {
  return request({
    url: '/email/templates/',
    method: 'get',
    params
  })
}

// 创建模板
export function createTemplate(data) {
  return request({
    url: '/email/templates/',
    method: 'post',
    data
  })
}

// 更新模板
export function updateTemplate(id, data) {
  return request({
    url: `/email/templates/${id}/`,
    method: 'put',
    data
  })
}

// 删除模板
export function deleteTemplate(id) {
  return request({
    url: `/email/templates/${id}/`,
    method: 'delete'
  })
}

// 复制模板
export function copyTemplate(id) {
  return request({
    url: `/email/templates/${id}/copy/`,
    method: 'post'
  })
}

// 获取模板详情
export function getTemplateDetail(id) {
  return request({
    url: `/email/templates/${id}/`,
    method: 'get'
  })
} 