<template>
  <div class="history-container">
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <h3>历史记录</h3>
          <div class="header-right">
            <el-input
              v-model="searchQuery"
              placeholder="搜索..."
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
      </template>

      <el-table :data="historyList" style="width: 100%">
        <el-table-column prop="task.subject" label="邮件主题" />
        <el-table-column prop="success_count" label="成功数" />
        <el-table-column prop="failed_count" label="失败数" />
        <el-table-column prop="created_at" label="发送时间">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" @click="showDetail(row)">
              详情
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
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="detailVisible"
      title="发送详情"
      width="600px"
    >
      <div v-if="currentDetail">
        <p><strong>邮件主题：</strong>{{ currentDetail.task.subject }}</p>
        <p><strong>发送时间：</strong>{{ formatDate(currentDetail.created_at) }}</p>
        <p><strong>成功数量：</strong>{{ currentDetail.success_count }}</p>
        <p><strong>失败数量：</strong>{{ currentDetail.failed_count }}</p>
        <div v-if="currentDetail.error_message">
          <p><strong>错误信息：</strong></p>
          <pre class="error-message">{{ currentDetail.error_message }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getHistoryList, getHistoryDetail } from '@/api/history'
import { formatDate } from '@/utils/format'

const historyList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const detailVisible = ref(false)
const currentDetail = ref(null)

const loadHistoryList = async () => {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value
    }
    const res = await getHistoryList(params)
    historyList.value = res.results
    total.value = res.count
  } catch (error) {
    console.error('Failed to load history:', error)
  }
}

const showDetail = async (row) => {
  try {
    const res = await getHistoryDetail(row.id)
    currentDetail.value = res
    detailVisible.value = true
  } catch (error) {
    console.error('Failed to load detail:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadHistoryList()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  loadHistoryList()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadHistoryList()
}

onMounted(() => {
  loadHistoryList()
})
</script>

<style scoped>
.history-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-right {
  display: flex;
  gap: 16px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.error-message {
  background: var(--bg-tertiary);
  padding: 12px;
  border-radius: 4px;
  white-space: pre-wrap;
  color: var(--text-secondary);
}
</style> 