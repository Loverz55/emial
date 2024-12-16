/**
 * 格式化日期时间
 * @param {string|number|Date} date 日期对象、时间戳或日期字符串
 * @param {string} format 格式化模板，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的日期字符串
 */
export const formatDate = (date, format = 'YYYY-MM-DD HH:mm:ss') => {
  if (!date) return ''
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化文件大小
 * @param {number} bytes 字节数
 * @returns {string} 格式化后的文件大小
 */
export const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  
  while (bytes >= 1024 && i < units.length - 1) {
    bytes /= 1024
    i++
  }
  
  return `${bytes.toFixed(2)} ${units[i]}`
}

/**
 * 格式化数字（添加千分位）
 * @param {number} num 数字
 * @returns {string} 格式化后的数字
 */
export const formatNumber = (num) => {
  if (!num && num !== 0) return ''
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/**
 * 格式化时间间隔
 * @param {number} seconds 秒数
 * @returns {string} 格式化后的时间间隔
 */
export const formatDuration = (seconds) => {
  if (!seconds && seconds !== 0) return ''
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const remainingSeconds = seconds % 60

  const parts = []
  if (hours) parts.push(`${hours}小时`)
  if (minutes) parts.push(`${minutes}分钟`)
  if (remainingSeconds || !parts.length) parts.push(`${remainingSeconds}秒`)

  return parts.join('')
}

/**
 * 格式化金额
 * @param {number} amount 金额
 * @param {number} decimals 小数位数，默认2位
 * @returns {string} 格式化后的金额
 */
export const formatAmount = (amount, decimals = 2) => {
  if (!amount && amount !== 0) return ''
  return Number(amount).toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
} 