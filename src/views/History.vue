<template>
  <div class="history-page">
    <div class="page-header">
      <h2>发送记录</h2>
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item>
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索收件人/主题"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            :shortcuts="dateShortcuts"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-card class="history-table">
      <el-table
        v-loading="loading"
        :data="historyList"
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="recipient" label="收件人" min-width="200" />
        <el-table-column prop="subject" label="邮件主题" min-width="200" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
              {{ row.status === 'success' ? '发送成功' : '发送失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="send_time" label="发送时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.send_time) }}
          </template>
        </el-table-column>
        <el-table-column label="定时任务" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.schedule" type="warning" size="small">
              {{ getRepeatTypeText(row.schedule.repeat_type) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">
              查看详情
            </el-button>
            <el-button 
              v-if="row.status === 'failed'"
              link 
              type="primary" 
              @click="handleResend(row)"
            >
              重新发送
            </el-button>
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
    >
      <template v-if="currentEmail">
        <div class="email-detail">
          <div class="detail-item">
            <label>收件人：</label>
            <span>{{ currentEmail.recipient }}</span>
          </div>
          <div class="detail-item">
            <label>主题：</label>
            <span>{{ currentEmail.subject }}</span>
          </div>
          <div class="detail-item">
            <label>发送时间：</label>
            <span>{{ formatDate(currentEmail.send_time) }}</span>
          </div>
          <div class="detail-item">
            <label>状态：</label>
            <el-tag :type="currentEmail.status === 'success' ? 'success' : 'danger'">
              {{ currentEmail.status === 'success' ? '发送成功' : '发送失败' }}
            </el-tag>
          </div>
          <template v-if="currentEmail.schedule">
            <div class="detail-item">
              <label>定时类型：</label>
              <el-tag type="warning">{{ getRepeatTypeText(currentEmail.schedule.repeat_type) }}</el-tag>
            </div>
            <div class="detail-item">
              <label>执行时间：</label>
              <span>{{ formatDate(currentEmail.schedule.schedule_time) }}</span>
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
          </template>
          <div class="detail-item full">
            <label>邮件内容：</label>
            <div class="email-content" v-html="currentEmail.content"></div>
          </div>
          <div v-if="currentEmail.error" class="detail-item full">
            <label>错误信息：</label>
            <div class="error-message">{{ currentEmail.error }}</div>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getEmailHistory, resendEmail } from '@/api/history'
import dayjs from 'dayjs'

// 搜索表单
const searchForm = ref({
  keyword: '',
  dateRange: []
})

// 表格数据
const loading = ref(false)
const historyList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 详情对话框
const detailVisible = ref(false)
const currentEmail = ref(null)

// 日期快捷选项
const dateShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    },
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    },
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    },
  }
]

// 格式化日期
const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
}

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

// 格式化周几
const formatWeekDays = (days) => {
  if (!days) return '-'
  const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return days.map(day => weekDays[parseInt(day)]).join('、')
}

// 获取历史记录
const fetchHistory = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchForm.value.keyword,
      start_date: searchForm.value.dateRange?.[0]?.toISOString(),
      end_date: searchForm.value.dateRange?.[1]?.toISOString()
    }
    
    const { data } = await getEmailHistory(params)
    historyList.value = data.results
    total.value = data.total
  } catch (error) {
    ElMessage.error('获取发送记录失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchHistory()
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    keyword: '',
    dateRange: []
  }
  handleSearch()
}

// 查看详情
const viewDetail = (row) => {
  currentEmail.value = row
  detailVisible.value = true
}

// 重新发送
const handleResend = async (row) => {
  try {
    await ElMessageBox.confirm('确定要重新发送该邮件吗？')
    await resendEmail(row.id)
    ElMessage.success('重新发送成功')
    fetchHistory()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重新发送失败')
    }
  }
}

// 分页
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchHistory()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchHistory()
}

onMounted(() => {
  fetchHistory()
})
</script>

<style scoped lang="scss">
.history-page {
  .page-header {
    margin-bottom: 20px;
    
    h2 {
      margin-bottom: 20px;
    }
    
    .search-form {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
  }

  .history-table {
    margin-bottom: 20px;
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}

.email-detail {
  .detail-item {
    margin-bottom: 16px;
    display: flex;
    
    &.full {
      display: block;
      
      label {
        margin-bottom: 8px;
        display: block;
      }
    }
    
    label {
      width: 80px;
      color: var(--el-text-color-secondary);
    }
    
    .email-content {
      padding: 12px;
      background-color: var(--el-fill-color-light);
      border-radius: 4px;
      min-height: 100px;
    }
    
    .error-message {
      color: var(--el-color-danger);
      padding: 8px;
      background-color: var(--el-color-danger-light-9);
      border-radius: 4px;
    }
  }
}
</style> 