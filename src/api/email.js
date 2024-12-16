import request from '@/utils/request'

// 发送邮件
export function sendEmail(data) {
  // 转换参数名称以匹配API要求
  const apiData = {
    to: data.recipients,
    from_mail: data.from,
    subject: data.subject,
    message: data.content
  }
  
  return request({
    url: '/email/send/',
    method: 'post',
    data: apiData,
    timeout: 30000  // 设置30秒超时
  })
}

// 获取发送记录
export function getEmailHistory(params) {
  return request({
    url: '/email/history/',
    method: 'get',
    params
  })
}

// 获取邮件详情
export function getEmailDetail(id) {
  return request({
    url: `/email/detail/${id}/`,
    method: 'get'
  })
}

// 重新发送邮件
export function resendEmail(id) {
  return request({
    url: `/email/resend/${id}/`,
    method: 'post'
  })
} 