import request from '@/utils/request'

// 上传图片
export function uploadImage(data) {
  return request({
    url: '/email/upload/image/',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
} 