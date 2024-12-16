<template>
  <div class="email-tasks">
    <div class="page-header">
      <h2>邮件任务管理</h2>
      <el-button type="primary" @click="handleCreate">
        创建任务
      </el-button>
    </div>

    <!-- 任务列表 -->
    <el-table
      v-loading="loading"
      :data="taskList"
      style="width: 100%"
      border
    >
      <el-table-column prop="name" label="任务名称" min-width="120" />
      <el-table-column prop="schedule" label="执行计划" min-width="120">
        <template #default="{ row }">
          {{ formatSchedule(row.schedule) }}
        </template>
      </el-table-column>
      <el-table-column prop="recipients" label="收件人" min-width="200">
        <template #default="{ row }">
          {{ row.recipients.join(', ') }}
        </template>
      </el-table-column>
      <el-table-column prop="nextExecutionTime" label="下次执行时间" min-width="160">
        <template #default="{ row }">
          {{ formatDateTime(row.nextExecutionTime) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button-group>
            <el-button
              :type="row.status === '活跃' ? 'warning' : 'success'"
              size="small"
              @click="handleToggleStatus(row)"
            >
              {{ row.status === '活跃' ? '暂停' : '启动' }}
            </el-button>
            <el-button
              type="primary"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
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

    <!-- 任务表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '创建任务' : '编辑任务'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="taskForm"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>

        <el-form-item label="执行计划" prop="schedule">
          <el-select v-model="taskForm.scheduleType" class="schedule-type">
            <el-option label="每天" value="daily" />
            <el-option label="每周" value="weekly" />
            <el-option label="每月" value="monthly" />
            <el-option label="自定义" value="custom" />
          </el-select>
          
          <template v-if="taskForm.scheduleType === 'daily'">
            <el-time-picker
              v-model="taskForm.scheduleTime"
              placeholder="选择时间"
              format="HH:mm"
            />
          </template>
          
          <template v-if="taskForm.scheduleType === 'weekly'">
            <el-select v-model="taskForm.weekDay" class="week-day">
              <el-option
                v-for="day in weekDays"
                :key="day.value"
                :label="day.label"
                :value="day.value"
              />
            </el-select>
            <el-time-picker
              v-model="taskForm.scheduleTime"
              placeholder="选择时间"
              format="HH:mm"
            />
          </template>
          
          <template v-if="taskForm.scheduleType === 'monthly'">
            <el-input-number
              v-model="taskForm.monthDay"
              :min="1"
              :max="31"
              class="month-day"
            />
            <span class="day-label">日</span>
            <el-time-picker
              v-model="taskForm.scheduleTime"
              placeholder="选择时间"
              format="HH:mm"
            />
          </template>
          
          <template v-if="taskForm.scheduleType === 'custom'">
            <el-input
              v-model="taskForm.customSchedule"
              placeholder="Cron 表达式"
            />
          </template>
        </el-form-item>

        <el-form-item label="收件人" prop="recipients">
          <el-select
            v-model="taskForm.recipients"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请输入收件人邮箱"
          >
            <el-option
              v-for="item in recipientOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="邮件主题" prop="subject">
          <el-input v-model="taskForm.subject" placeholder="请输入邮件主题" />
        </el-form-item>

        <el-form-item label="邮件内容" prop="content">
          <el-input
            v-model="taskForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入邮件内容"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getEmailTasks, createEmailTask, updateEmailTask, deleteEmailTask, toggleTaskStatus } from '@/api/emailTask'
import dayjs from 'dayjs'

// 数据
const loading = ref(false)
const taskList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const dialogType = ref('create')
const formRef = ref(null)

const weekDays = [
  { label: '周一', value: 1 },
  { label: '周二', value: 2 },
  { label: '周三', value: 3 },
  { label: '周四', value: 4 },
  { label: '周五', value: 5 },
  { label: '周六', value: 6 },
  { label: '周日', value: 0 }
]

const recipientOptions = ref([]) // 这里可以放置常用收件人列表

const taskForm = reactive({
  name: '',
  scheduleType: 'daily',
  scheduleTime: '',
  weekDay: 1,
  monthDay: 1,
  customSchedule: '',
  recipients: [],
  subject: '',
  content: ''
})

const formRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  recipients: [
    { required: true, message: '请添加收件人', trigger: 'change' },
    {
      type: 'array',
      validator: (rule, value, callback) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        const invalid = value.some(email => !emailRegex.test(email))
        if (invalid) {
          callback(new Error('请输入有效的邮箱地址'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ],
  subject: [
    { required: true, message: '请输入邮件主题', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入邮件内容', trigger: 'blur' }
  ]
}

// 方法
const formatDateTime = (time) => {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '未设置'
}

const formatSchedule = (schedule) => {
  // 这里根据实际的schedule格式来实现格式化逻辑
  return schedule
}

const getStatusType = (status) => {
  const types = {
    '活跃': 'success',
    '暂停': 'warning',
    '错误': 'danger'
  }
  return types[status] || 'info'
}

const loadTasks = async () => {
  loading.value = true
  try {
    const res = await getEmailTasks({
      page: currentPage.value,
      pageSize: pageSize.value
    })
    taskList.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    console.error('加载任务列表失败:', error)
  } finally {
    loading.value = false
  }
}

const resetTaskForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(taskForm, {
    name: '',
    scheduleType: 'daily',
    scheduleTime: '',
    weekDay: 1,
    monthDay: 1,
    customSchedule: '',
    recipients: [],
    subject: '',
    content: ''
  })
}

const handleCreate = () => {
  dialogType.value = 'create'
  resetTaskForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogType.value = 'edit'
  Object.assign(taskForm, row)
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该任务吗？', '提示', {
      type: 'warning'
    })
    await deleteEmailTask(row.id)
    ElMessage.success('删除成功')
    loadTasks()
  } catch (error) {
    console.error('删除任务失败:', error)
  }
}

const handleToggleStatus = async (row) => {
  try {
    const newStatus = row.status === '活跃' ? '暂停' : '活跃'
    await toggleTaskStatus(row.id, newStatus)
    ElMessage.success(`${newStatus}成功`)
    loadTasks()
  } catch (error) {
    console.error('切换任务状态失败:', error)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // 构建schedule
    let schedule = ''
    switch (taskForm.scheduleType) {
      case 'daily':
        schedule = `每天 ${dayjs(taskForm.scheduleTime).format('HH:mm')}`
        break
      case 'weekly':
        schedule = `每周${weekDays.find(d => d.value === taskForm.weekDay).label} ${dayjs(taskForm.scheduleTime).format('HH:mm')}`
        break
      case 'monthly':
        schedule = `每月${taskForm.monthDay}日 ${dayjs(taskForm.scheduleTime).format('HH:mm')}`
        break
      case 'custom':
        schedule = taskForm.customSchedule
        break
    }
    
    const data = {
      ...taskForm,
      schedule
    }
    
    if (dialogType.value === 'create') {
      await createEmailTask(data)
      ElMessage.success('创建成功')
    } else {
      await updateEmailTask(data.id, data)
      ElMessage.success('更新成功')
    }
    
    dialogVisible.value = false
    loadTasks()
  } catch (error) {
    console.error('提交任务失败:', error)
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  loadTasks()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadTasks()
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.email-tasks {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.schedule-type {
  width: 120px;
  margin-right: 10px;
}

.week-day {
  width: 100px;
  margin-right: 10px;
}

.month-day {
  width: 100px;
  margin-right: 10px;
}

.day-label {
  margin-right: 10px;
}

:deep(.el-select) {
  width: 100%;
}
</style> 