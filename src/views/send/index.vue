<template>
  <div class="send-container">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="send-card">
          <template #header>
            <div class="card-header">
              <h3>
                <el-icon><Message /></el-icon>
                发送邮件
              </h3>
              <el-button type="primary" :loading="sending" @click="handleSend">
                <el-icon><ArrowRight /></el-icon>
                {{ isScheduled ? '定时发送' : '立即发送' }}
              </el-button>
            </div>
          </template>

          <el-form
            ref="formRef"
            :model="formData"
            :rules="rules"
            label-position="top"
            class="send-form"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="发件人" prop="from">
                  <el-input
                    v-model="formData.from"
                    placeholder="请输入发件人名称"
                    :prefix-icon="User"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="主题" prop="subject">
                  <el-input
                    v-model="formData.subject"
                    placeholder="请输入邮件主题"
                    :prefix-icon="Edit"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="收件人" prop="recipients">
              <el-input
                v-model="formData.recipients"
                type="textarea"
                :rows="2"
                placeholder="请输入收件人邮箱，多个邮箱用逗号分隔"
                :prefix-icon="Avatar"
              />
              <div class="form-tips">
                <el-icon><InfoFilled /></el-icon>
                <span>多个收件人请用英文逗号（,）分隔</span>
              </div>
            </el-form-item>

            <el-form-item label="内容" prop="content">
              <el-input
                v-model="formData.content"
                type="textarea"
                :rows="12"
                placeholder="请输入邮件内容"
                resize="none"
              />
            </el-form-item>

            <!-- 定时发送设置 -->
            <el-form-item>
              <el-divider>定时发送设置</el-divider>
              <div class="schedule-settings">
                <el-switch
                  v-model="isScheduled"
                  active-text="定时发送"
                  inactive-text="立即发送"
                />
                
                <template v-if="isScheduled">
                  <el-form-item label="发送时间" prop="scheduleTime" class="mt-4">
                    <el-time-picker
                      v-model="formData.scheduleTime"
                      format="HH:mm"
                      placeholder="选择发送时间"
                      :disabled="!isScheduled"
                    />
                  </el-form-item>
                  
                  <el-form-item label="重复类型" prop="repeat" class="mt-4">
                    <el-select v-model="formData.repeat" placeholder="选择重复类型">
                      <el-option label="不重复" value="none" />
                      <el-option label="每天" value="daily" />
                      <el-option label="每周" value="weekly" />
                      <el-option label="每月" value="monthly" />
                    </el-select>
                  </el-form-item>
                  
                  <template v-if="formData.repeat === 'weekly'">
                    <el-form-item label="重复日期" prop="weekDays" class="mt-4">
                      <el-select
                        v-model="formData.weekDays"
                        multiple
                        placeholder="选择重复的星期"
                      >
                        <el-option label="星期一" value="0" />
                        <el-option label="星期二" value="1" />
                        <el-option label="星期三" value="2" />
                        <el-option label="星期四" value="3" />
                        <el-option label="星期五" value="4" />
                        <el-option label="星期六" value="5" />
                        <el-option label="星期日" value="6" />
                      </el-select>
                    </el-form-item>
                  </template>
                  
                  <template v-if="formData.repeat === 'monthly'">
                    <el-form-item label="每月日期" prop="monthDay" class="mt-4">
                      <el-input-number
                        v-model="formData.monthDay"
                        :min="1"
                        :max="31"
                        placeholder="选择每月几号"
                      />
                    </el-form-item>
                  </template>
                </template>
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="tips-card">
          <template #header>
            <div class="card-header">
              <h3>
                <el-icon><InfoFilled /></el-icon>
                使用说明
              </h3>
            </div>
          </template>
          <div class="tips-content">
            <h4>邮件发送注意事项：</h4>
            <ul>
              <li>确保收件人邮箱格式正确</li>
              <li>多个收件人使用英文逗号分隔</li>
              <li>邮件主题简明扼要</li>
              <li>正文内容清晰易读</li>
            </ul>
            <el-divider />
            <h4>定时发送说明：</h4>
            <ul>
              <li>开启定时发送后可设置具体发送时间</li>
              <li>支持每天、每周、每月重复发送</li>
              <li>选择每周重复需指定具体星期几</li>
              <li>选择每月重复需指定每月几号发送</li>
            </ul>
            <el-divider />
            <h4>快捷操作：</h4>
            <el-button-group class="quick-actions">
              <el-button @click="resetForm">
                <el-icon><RefreshRight /></el-icon>
                重置表单
              </el-button>
              <el-button type="primary" @click="loadTemplate">
                <el-icon><Document /></el-icon>
                加载模板
              </el-button>
            </el-button-group>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { sendEmail } from '@/api/email'
import { getTemplateDetail } from '@/api/template'
import {
  Message,
  ArrowRight,
  User,
  Avatar,
  Edit,
  InfoFilled,
  Document,
  RefreshRight
} from '@element-plus/icons-vue'

const route = useRoute()
const formRef = ref(null)
const sending = ref(false)
const isScheduled = ref(false)

const formData = ref({
  recipients: '',
  from: '',
  subject: '',
  content: '',
  scheduleTime: null,
  repeat: 'none',
  weekDays: [],
  monthDay: null
})

const rules = {
  recipients: [
    { required: true, message: '请输入收件人邮箱', trigger: 'blur' },
    {
      pattern: /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])+/,
      message: '请输入正确的邮箱格式',
      trigger: 'blur'
    }
  ],
  from: [
    { required: true, message: '请输入发件人名称', trigger: 'blur' }
  ],
  subject: [
    { required: true, message: '请输入邮件主题', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入邮件内容', trigger: 'blur' }
  ],
  scheduleTime: [
    { 
      required: true, 
      message: '请选择发送时间', 
      trigger: 'change',
      validator: (rule, value, callback) => {
        if (isScheduled.value && !value) {
          callback(new Error('请选择发送时间'))
        } else {
          callback()
        }
      }
    }
  ],
  weekDays: [
    {
      required: true,
      message: '请选择重复的星期',
      trigger: 'change',
      validator: (rule, value, callback) => {
        if (isScheduled.value && formData.value.repeat === 'weekly' && value.length === 0) {
          callback(new Error('请至少选择一天'))
        } else {
          callback()
        }
      }
    }
  ],
  monthDay: [
    {
      required: true,
      message: '请选择每月几号发送',
      trigger: 'change',
      validator: (rule, value, callback) => {
        if (isScheduled.value && formData.value.repeat === 'monthly' && !value) {
          callback(new Error('请选择发送日期'))
        } else {
          callback()
        }
      }
    }
  ]
}

const handleSend = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    sending.value = true

    // 处理收件人列表
    const recipients = formData.value.recipients.split(',').map(email => email.trim())

    // 构建发送数据
    const sendData = {
      recipients: recipients.join(','),
      from: formData.value.from,
      subject: formData.value.subject,
      content: formData.value.content
    }

    // 添加调试日志
    console.log('发送数据:', sendData)

    // 发送邮件
    const response = await sendEmail(sendData)
    
    ElMessage.success('邮件发送成功')
    resetForm()
  } catch (error) {
    console.error('发送邮件失败:', error)
    ElMessage.error(error.response?.data?.message || '发送失败')
  } finally {
    sending.value = false
  }
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
    isScheduled.value = false
    formData.value.scheduleTime = null
    formData.value.repeat = 'none'
    formData.value.weekDays = []
    formData.value.monthDay = null
  }
}

const loadTemplate = async () => {
  const templateId = route.query.templateId
  if (!templateId) return
  
  try {
    const { data } = await getTemplateDetail(templateId)
    formData.value.subject = data.subject
    formData.value.content = data.content
    
    ElMessage.success(`已加载模板：${data.name}`)
  } catch (error) {
    console.error('加载模板失败:', error)
    ElMessage.error('加载模板失败')
  }
}

// 在组件挂载时检查是否需要加载模板
onMounted(() => {
  if (route.query.templateId) {
    loadTemplate()
  }
})
</script>

<style scoped lang="scss">
.send-container {
  padding: 24px;
  min-height: calc(100vh - 120px);
  background-color: var(--el-fill-color-blank);

  .send-card {
    height: 100%;
    box-shadow: var(--el-box-shadow-light);
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin: 0;
      padding: 0;

      h3 {
        margin: 0;
        font-size: 18px;
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--el-text-color-primary);
        
        .el-icon {
          font-size: 20px;
          color: var(--el-color-primary);
        }
      }
    }

    .send-form {
      padding: 20px 0;

      .form-tips {
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
        color: var(--el-text-color-secondary);
        font-size: 12px;

        .el-icon {
          font-size: 14px;
          color: var(--el-color-warning);
        }
      }

      .schedule-settings {
        padding: 16px;
        background-color: var(--el-fill-color-light);
        border-radius: 4px;

        .mt-4 {
          margin-top: 16px;
        }

        :deep(.el-checkbox-group) {
          display: flex;
          flex-wrap: wrap;
          gap: 16px;
        }
      }

      :deep(.el-form-item__label) {
        font-weight: 500;
        padding-bottom: 8px;
      }

      :deep(.el-input__wrapper) {
        box-shadow: 0 0 0 1px var(--el-border-color) inset;
        
        &:hover {
          box-shadow: 0 0 0 1px var(--el-border-color-hover) inset;
        }
        
        &.is-focus {
          box-shadow: 0 0 0 1px var(--el-color-primary) inset;
        }
      }

      :deep(.el-textarea__inner) {
        font-family: var(--el-font-family);
        padding: 12px;
        
        &::placeholder {
          color: var(--el-text-color-placeholder);
        }
      }
    }
  }

  .tips-card {
    height: 100%;
    box-shadow: var(--el-box-shadow-light);
    
    .card-header {
      h3 {
        margin: 0;
        font-size: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--el-text-color-primary);
        
        .el-icon {
          font-size: 18px;
          color: var(--el-color-primary);
        }
      }
    }

    .tips-content {
      h4 {
        margin: 0 0 12px;
        font-size: 14px;
        color: var(--el-text-color-primary);
      }

      ul {
        margin: 0;
        padding-left: 20px;
        
        li {
          margin-bottom: 8px;
          color: var(--el-text-color-regular);
          font-size: 13px;
          
          &:last-child {
            margin-bottom: 0;
          }
        }
      }

      .quick-actions {
        display: flex;
        gap: 12px;
        margin-top: 16px;
        
        .el-button {
          flex: 1;
          justify-content: center;
          
          .el-icon {
            margin-right: 4px;
          }
        }
      }
    }
  }
}

// 响应式布局
@media (max-width: 1200px) {
  .send-container {
    :deep(.el-row) {
      flex-direction: column;
      
      .el-col {
        width: 100%;
        margin-bottom: 20px;
        
        &:last-child {
          margin-bottom: 0;
        }
      }
    }
  }
}
</style> 