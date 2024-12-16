<template>
  <div class="history-container">
    <el-card class="history-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon"><Timer /></el-icon>
            <h3>发送记录</h3>
          </div>
          <div class="header-actions">
            <el-input
              v-model="searchQuery"
              placeholder="搜索收件人或主题..."
              :prefix-icon="Search"
              clearable
              class="search-input"
              @input="handleSearch"
            />
            <el-button type="primary" :icon="Refresh" @click="refreshList">
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="emailList"
        style="width: 100%"
        border
        stripe
        highlight-current-row
      >
        <el-table-column prop="recipient" label="收件人" min-width="180">
          <template #default="{ row }">
            <el-tooltip :content="row.recipient" placement="top" :show-after="500">
              <span class="email-cell">
                <el-icon><Message /></el-icon>
                {{ row.recipient }}
              </span>
            </el-tooltip>
          </template>
        </el-table-column>

        <el-table-column prop="subject" label="主题" min-width="200">
          <template #default="{ row }">
            <el-tooltip :content="row.subject" placement="top" :show-after="500">
              <span class="subject-cell">
                <el-icon><Document /></el-icon>
                {{ row.subject }}
              </span>
            </el-tooltip>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'completed' ? 'success' : 'danger'"
              size="small"
              effect="light"
              class="status-tag"
              round
            >
              <span class="tag-content">
                <el-icon class="status-icon">
                  <CircleCheck v-if="row.status === 'completed'" />
                  <CircleClose v-else />
                </el-icon>
                <span class="status-text">
                  {{ row.status === 'completed' ? '发送成功' : '发送失败' }}
                </span>
              </span>
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="定时任务" width="120" align="center">
          <template #default="{ row }">
            <template v-if="row.schedule">
              <el-tooltip
                :content="getScheduleTooltip(row.schedule)"
                placement="top"
                effect="dark"
              >
                <el-tag type="warning" size="small" effect="plain" class="schedule-tag" round>
                  <span class="tag-content">
                    <el-icon class="schedule-icon"><Timer /></el-icon>
                    <span class="schedule-text">
                      {{ getRepeatTypeText(row.schedule.repeat_type) }}
                    </span>
                  </span>
                </el-tag>
              </el-tooltip>
            </template>
            <span v-else class="no-schedule">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="send_time" label="发送时间" width="180" align="center">
          <template #default="{ row }">
            <span class="time-cell">
              <el-icon><Calendar /></el-icon>
              {{ formatDate(row.send_time) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-tooltip 
                content="重新发送" 
                placement="top" 
                :show-after="500"
                v-if="row.status === 'failed'"
              >
                <el-button
                  type="primary"
                  size="small"
                  circle
                  :icon="RefreshRight"
                  @click="handleResend(row)"
                />
              </el-tooltip>
              <el-tooltip 
                content="查看详情" 
                placement="top" 
                :show-after="500"
              >
                <el-button
                  type="info"
                  size="small"
                  circle
                  plain
                  :icon="View"
                  @click="showDetail(row)"
                />
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="邮件详情"
      width="600px"
      destroy-on-close
      class="detail-dialog"
    >
      <div class="email-detail" v-if="currentEmail">
        <div class="detail-item">
          <label><el-icon><Message /></el-icon>收件人：</label>
          <span>{{ currentEmail.recipient }}</span>
        </div>
        <div class="detail-item">
          <label><el-icon><Document /></el-icon>主题：</label>
          <span>{{ currentEmail.subject }}</span>
        </div>
        <div class="detail-item">
          <label><el-icon><InfoFilled /></el-icon>状态：</label>
          <el-tag
            :type="currentEmail.status === 'completed' ? 'success' : 'danger'"
            size="small"
            effect="dark"
          >
            <el-icon>
              <CircleCheck v-if="currentEmail.status === 'completed'" />
              <CircleClose v-else />
            </el-icon>
            {{ currentEmail.status === 'completed' ? '发送成功' : '发送失败' }}
          </el-tag>
        </div>
        <div class="detail-item">
          <label><el-icon><Calendar /></el-icon>发送时间：</label>
          <span>{{ formatDate(currentEmail.send_time) }}</span>
        </div>
        <template v-if="currentEmail.schedule">
          <div class="detail-section">
            <h4><el-icon><Timer /></el-icon>定时任务信息</h4>
            <div class="detail-item">
              <label>定时类型：</label>
              <el-tag type="warning" size="small" effect="plain">
                {{ getRepeatTypeText(currentEmail.schedule.repeat_type) }}
              </el-tag>
            </div>
            <div class="detail-item">
              <label>执行时间：</label>
              <span>{{ formatTime(currentEmail.schedule.schedule_time) }}</span>
            </div>
            <div v-if="currentEmail.schedule.repeat_type === 'weekly'" class="detail-item">
              <label>重复日期：</label>
              <span>{{ formatWeekDays(currentEmail.schedule.week_days) }}</span>
            </div>
            <div v-if="currentEmail.schedule.repeat_type === 'monthly'" class="detail-item">
              <label>执行日期：</label>
              <span>每月 {{ currentEmail.schedule.month_day }} 号</span>
            </div>
            <div class="detail-item">
              <label>下次执行：</label>
              <span>{{ formatDate(currentEmail.schedule.next_run) }}</span>
            </div>
          </div>
        </template>
        <div class="detail-section">
          <h4><el-icon><Document /></el-icon>邮件内容</h4>
          <div class="content-box">{{ currentEmail.content }}</div>
        </div>
        <div class="detail-section" v-if="currentEmail.error_message">
          <h4><el-icon><Warning /></el-icon>错误信息</h4>
          <div class="error-message">{{ currentEmail.error_message }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getEmailHistory, resendEmail } from '@/api/history'
import { formatDate } from '@/utils/format'
import {
  Timer,
  Search,
  Refresh,
  Message,
  Document,
  Calendar,
  CircleCheck,
  CircleClose,
  View,
  RefreshRight,
  InfoFilled,
  Warning
} from '@element-plus/icons-vue'

// 数据列表
const emailList = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const detailVisible = ref(false)
const currentEmail = ref(null)

// 获取重复类型文本
const getRepeatTypeText = (type) => {
  const types = {
    'daily': '每天',
    'weekly': '每周',
    'monthly': '每月',
    'none': '单次'
  }
  return types[type] || type
}

// 格式化时间（不含日期）
const formatTime = (time) => {
  if (!time) return '-'
  return time.substring(0, 5)  // 只显示 HH:mm
}

// 格式化周几
const formatWeekDays = (days) => {
  if (!days) return '-'
  const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return days.split(',').map(day => weekDays[parseInt(day)]).join('、')
}

// 获取定时任务提示文本
const getScheduleTooltip = (schedule) => {
  let text = `${getRepeatTypeText(schedule.repeat_type)}\n`
  text += `执行时间: ${formatTime(schedule.schedule_time)}\n`
  
  if (schedule.repeat_type === 'weekly' && schedule.week_days) {
    text += `重复日期: ${formatWeekDays(schedule.week_days)}\n`
  } else if (schedule.repeat_type === 'monthly' && schedule.month_day) {
    text += `执行日期: 每月${schedule.month_day}号\n`
  }
  
  if (schedule.next_run) {
    text += `下次执行: ${formatDate(schedule.next_run)}`
  }
  return text
}

// 获取列表数据
const getList = async () => {
  try {
    loading.value = true
    const { data } = await getEmailHistory({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value
    })
    console.log('API Response:', data)  // 添加调试日志
    emailList.value = data.data
    total.value = data.total
  } catch (error) {
    console.error('获取发送记录失败:', error)
    ElMessage.error('获取发送记录失败')
  } finally {
    loading.value = false
  }
}

// 刷新列表
const refreshList = () => {
  currentPage.value = 1
  getList()
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  getList()
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  getList()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  getList()
}

// 重新发送
const handleResend = async (row) => {
  try {
    await ElMessageBox.confirm(
      '确定要重新发送邮件吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await resendEmail(row.id)
    ElMessage.success('重新发送成功')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重新发送失败:', error)
      ElMessage.error('重新发送失败')
    }
  }
}

// 显示详情
const showDetail = (row) => {
  currentEmail.value = row
  detailVisible.value = true
}

onMounted(() => {
  getList()
})
</script>

<style scoped lang="scss">
.history-container {
  padding: 24px;
  background-color: var(--el-bg-color-page);
  min-height: calc(100vh - 48px);
  
  .history-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .header-left {
        display: flex;
        align-items: center;
        gap: 8px;

        .header-icon {
          font-size: 24px;
          color: var(--el-color-primary);
        }
        
        h3 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--el-text-color-primary);
        }
      }
      
      .header-actions {
        display: flex;
        gap: 16px;
        
        .search-input {
          width: 280px;
          transition: all 0.3s ease;
          
          &:focus-within {
            width: 320px;
          }
        }
      }
    }
    
    .email-cell,
    .subject-cell {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .el-icon {
        font-size: 16px;
        color: var(--el-text-color-secondary);
      }
    }
    
    .status-tag,
    .schedule-tag {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      padding: 0 12px;
      height: 24px;
      min-width: 90px;

      .tag-content {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        line-height: 1;
      }
      
      .status-icon,
      .schedule-icon {
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .status-text,
      .schedule-text {
        font-size: 13px;
        line-height: 1;
      }
    }
    
    .status-tag {
      &.el-tag--success {
        background-color: var(--el-color-success-light-9);
        border-color: var(--el-color-success-light-5);
        color: var(--el-color-success);
      }

      &.el-tag--danger {
        background-color: var(--el-color-danger-light-9);
        border-color: var(--el-color-danger-light-5);
        color: var(--el-color-danger);
      }
    }

    .schedule-tag {
      background-color: var(--el-color-warning-light-9);
      border-color: var(--el-color-warning-light-5);
      color: var(--el-color-warning);
    }

    .no-schedule {
      color: var(--el-text-color-secondary);
      font-size: 13px;
    }
    
    .time-cell {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      color: var(--el-text-color-regular);
      
      .el-icon {
        font-size: 14px;
      }
    }
    
    .action-buttons {
      display: flex;
      gap: 8px;
      justify-content: center;
    }
    
    .pagination-container {
      margin-top: 24px;
      padding-top: 16px;
      border-top: 1px solid var(--el-border-color-lighter);
      display: flex;
      justify-content: flex-end;
    }
  }
}

.detail-dialog {
  .email-detail {
    .detail-section {
      margin-bottom: 24px;
      padding: 16px;
      background-color: var(--el-bg-color-page);
      border-radius: 8px;
      
      h4 {
        margin: 0 0 16px;
        font-size: 16px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        display: flex;
        align-items: center;
        gap: 8px;
        
        .el-icon {
          font-size: 18px;
          color: var(--el-color-primary);
        }
      }
    }
    
    .detail-item {
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      label {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-weight: 500;
        color: var(--el-text-color-regular);
        margin-right: 12px;
        min-width: 90px;
        
        .el-icon {
          font-size: 16px;
        }
      }
    }
    
    .content-box {
      padding: 16px;
      background-color: var(--el-bg-color);
      border: 1px solid var(--el-border-color-lighter);
      border-radius: 4px;
      white-space: pre-wrap;
      word-break: break-all;
      min-height: 100px;
      max-height: 300px;
      overflow-y: auto;
      font-size: 14px;
      line-height: 1.6;
      color: var(--el-text-color-regular);
    }
    
    .error-message {
      padding: 12px 16px;
      background-color: var(--el-color-danger-light-9);
      border-radius: 4px;
      color: var(--el-color-danger);
      font-size: 13px;
      line-height: 1.6;
    }
  }
}

@media (max-width: 768px) {
  .history-container {
    padding: 16px;
    
    .history-card {
      .card-header {
        flex-direction: column;
        align-items: stretch;
        gap: 16px;
        
        .header-actions {
          flex-direction: column;
          gap: 12px;
          
          .search-input {
            width: 100%;
            
            &:focus-within {
              width: 100%;
            }
          }
        }
      }
    }
  }
}

.action-buttons {
  display: inline-flex;
  gap: 12px;
  justify-content: center;

  .el-button {
    margin: 0;
  }
}
</style>