<template>
  <div class="template-container">
    <div class="page-header">
      <div class="header-left">
        <h2>邮件模板</h2>
        <el-input
          v-model="searchKey"
          placeholder="搜索模板..."
          :prefix-icon="Search"
          clearable
          class="search-input"
          @input="handleSearch"
        />
      </div>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新建模板
      </el-button>
    </div>

    <div class="template-grid">
      <el-empty v-if="!templateList.length" description="暂无模板" />
      <template v-else>
        <div v-for="item in templateList" :key="item.id" class="template-item">
          <div class="template-card" :class="{ 'is-selected': selectedId === item.id }">
            <div class="card-header">
              <el-tag size="small" effect="plain">{{ item.categoryInfo.label }}</el-tag>
              <el-dropdown trigger="click">
                <el-icon class="more-icon"><More /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="handleEdit(item)">
                      <el-icon><Edit /></el-icon>编辑
                    </el-dropdown-item>
                    <el-dropdown-item @click="handlePreview(item)">
                      <el-icon><View /></el-icon>预览
                    </el-dropdown-item>
                    <el-dropdown-item @click="handleCopy(item)">
                      <el-icon><CopyDocument /></el-icon>复制
                    </el-dropdown-item>
                    <el-dropdown-item divided @click="handleDelete(item)" class="text-danger">
                      <el-icon><Delete /></el-icon>删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
            <div class="card-body" @click="handleSelect(item)">
              <h3 class="template-name">{{ item.name }}</h3>
              <p class="template-desc">{{ item.description || '暂无描述' }}</p>
              <div class="template-meta">
                <span class="time">{{ formatDate(item.updated_at, 'YYYY-MM-DD') }}</span>
                <span class="usage">使用 {{ item.usage_count }} 次</span>
              </div>
            </div>
            <div class="card-footer">
              <el-button type="primary" @click.stop="handleUse(item)">使用模板</el-button>
              <el-button @click.stop="handlePreview(item)">预览</el-button>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新建模板' : '编辑模板'"
      width="800px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="formData.category" placeholder="请选择分类">
            <el-option label="通知" value="notice" />
            <el-option label="营销" value="marketing" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="2"
            placeholder="请输入模板描述"
          />
        </el-form-item>
        <el-form-item label="邮件主题" prop="subject">
          <el-input v-model="formData.subject" placeholder="请输入邮件主题">
            <template #append>
              <el-button @click="insertVariable('subject')">插入变量</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="邮件内容" prop="content">
          <div class="editor-wrapper">
            <div class="editor-toolbar">
              <el-button-group>
                <el-button @click="insertVariable('content')">插入变量</el-button>
                <el-button @click="insertImage">插入图片</el-button>
              </el-button-group>
            </div>
            <el-input
              v-model="formData.content"
              type="textarea"
              :rows="12"
              placeholder="请输入邮件内容"
            />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      title="模板预览"
      width="600px"
      destroy-on-close
    >
      <div class="preview-content">
        <div class="preview-header">
          <h3>{{ previewData.subject }}</h3>
          <div class="preview-meta">
            <span>发件人：系统邮件 &lt;system@example.com&gt;</span>
            <span>收件人：{{ userStore.email }}</span>
          </div>
        </div>
        <div class="preview-body" v-html="formattedPreviewContent"></div>
      </div>
    </el-dialog>

    <!-- 变量选择对话框 -->
    <el-dialog
      v-model="variableVisible"
      title="插入变量"
      width="400px"
    >
      <div class="variable-list">
        <div
          v-for="item in variables"
          :key="item.key"
          class="variable-item"
          @click="handleInsertVariable(item)"
        >
          <span class="label">{{ item.label }}</span>
          <span class="key">{{ item.key }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Edit,
  View,
  More,
  Delete,
  CopyDocument
} from '@element-plus/icons-vue'
import { formatDate } from '@/utils/format'
import {
  getTemplateList,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  copyTemplate,
  getTemplateDetail
} from '@/api/template'
import { uploadImage } from '@/api/upload'

const router = useRouter()
const userStore = useUserStore()

// 模板列表
const templateList = ref([])
const loading = ref(false)

// 搜索和选择
const searchKey = ref('')
const selectedId = ref(null)

// 对话框控制
const dialogVisible = ref(false)
const dialogType = ref('add')
const previewVisible = ref(false)
const variableVisible = ref(false)
const submitting = ref(false)

// 当前编辑的字段
const currentField = ref('')

// 表单数据
const formRef = ref(null)
const formData = ref({
  name: '',
  category: 'other',
  subject: '',
  content: ''
})

const previewData = ref({
  subject: '',
  content: ''
})

// 变量列表
const variables = [
  { label: '用户名', key: '{username}' },
  { label: '邮箱', key: '{email}' },
  { label: '日期', key: '{date}' },
  { label: '时间', key: '{time}' },
  { label: '公司称', key: '{company}' },
  { label: '网站链接', key: '{website}' }
]

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  subject: [
    { required: true, message: '请输入邮件主题', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入邮件内容', trigger: 'blur' }
  ]
}

// 分类标签配置
const categoryConfig = {
  notice: {
    label: '通知',
    type: 'primary'
  },
  marketing: {
    label: '营销',
    type: 'success'
  },
  other: {
    label: '其他',
    type: 'info'
  }
}

// 获取分类显示信息
const getCategoryInfo = (category) => {
  return categoryConfig[category] || categoryConfig.other
}

// 初始化加载
onMounted(async () => {
  await loadTemplates()
})

// 加载模板列表
const loadTemplates = async () => {
  try {
    loading.value = true
    const response = await getTemplateList({ search: searchKey.value })
    templateList.value = response.data.results.map(template => ({
      ...template,
      categoryInfo: getCategoryInfo(template.category)
    }))
  } catch (error) {
    console.error('加载模板列表失败:', error)
    ElMessage.error('加载模板列表失败')
  } finally {
    loading.value = false
  }
}

// 处理搜索
const handleSearch = async () => {
  await loadTemplates()
}

// 选择模板
const handleSelect = (item) => {
  selectedId.value = item.id
}

// 使用模板
const handleUse = (item) => {
  router.push({
    path: '/send',
    query: { 
      templateId: item.id,
      templateName: item.name
    }
  })
}

// 添加模板
const handleAdd = () => {
  dialogType.value = 'add'
  formData.value = {
    name: '',
    category: 'other',
    subject: '',
    content: ''
  }
  dialogVisible.value = true
}

// 编辑模板
const handleEdit = async (item) => {
  try {
    const { data } = await getTemplateDetail(item.id)
    dialogType.value = 'edit'
    formData.value = { ...data }
    dialogVisible.value = true
  } catch (error) {
    console.error('获取模板详情失败:', error)
    ElMessage.error('获取模板详情失败')
  }
}

// 预览模板
const handlePreview = (item) => {
  previewData.value = {
    subject: item.subject,
    content: item.content
  }
  previewVisible.value = true
}

// 复制模板
const handleCopy = async (item) => {
  try {
    await copyTemplate(item.id)
    ElMessage.success('复制成功')
    loadTemplates()
  } catch (error) {
    console.error('复制模板失败:', error)
    ElMessage.error('复制模板失败')
  }
}

// 删除模板
const handleDelete = async (item) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除该模板吗？删除后无法恢复。',
      '删除确认',
      {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    )
    
    await deleteTemplate(item.id)
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除模板失败:', error)
      ElMessage.error('删除模板失败')
    }
  }
}

// 打开变量选择
const insertVariable = (field) => {
  currentField.value = field
  variableVisible.value = true
}

// 插入变量
const handleInsertVariable = (variable) => {
  const textarea = formData.value[currentField.value]
  const cursorPosition = document.activeElement.selectionStart
  
  if (cursorPosition !== undefined) {
    formData.value[currentField.value] = 
      textarea.slice(0, cursorPosition) + 
      variable.key + 
      textarea.slice(cursorPosition)
  } else {
    formData.value[currentField.value] += variable.key
  }
  
  variableVisible.value = false
}

// 插入图片
const insertImage = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (file) {
      try {
        loading.value = true
        ElMessage.info('正在上传图片，请稍候...')
        
        const uploadFormData = new FormData()
        uploadFormData.append('image', file)
        const { data } = await uploadImage(uploadFormData)
        
        // 检查响应中是否包含 url
        if (data?.url) {
          const imageUrl = data.url
          const imgTag = `<img src="${imageUrl}" alt="${file.name}" style="max-width: 100%; height: auto;" />`
          
          // 在当前内容后面添加图片
          formData.value = {
            ...formData.value,
            content: (formData.value.content || '') + imgTag
          }
          
          ElMessage.success(data.message || '图片插入成功')
        } else {
          throw new Error('上传失败：未获取到图片URL')
        }
      } catch (error) {
        console.error('图片上传失败:', error)
        ElMessage.error(error.response?.data?.message || error.message || '图片上传失败，请重试')
      } finally {
        loading.value = false
      }
    }
  }
  input.click()
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    submitting.value = true
    if (dialogType.value === 'add') {
      await createTemplate(formData.value)
      ElMessage.success('创建成功')
    } else {
      await updateTemplate(formData.value.id, formData.value)
      ElMessage.success('更新成功')
    }
    
    dialogVisible.value = false
    loadTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('保存模板失败:', error)
      ElMessage.error('保存模板失败')
    }
  } finally {
    submitting.value = false
  }
}

// 格式化预览内容
const formattedPreviewContent = computed(() => {
  if (!previewData.value.content) return ''
  
  // 替换变量为示例值
  let content = previewData.value.content
  content = content.replace(/{username}/g, userStore.username || '用户名')
  content = content.replace(/{email}/g, userStore.email || 'email@example.com')
  content = content.replace(/{date}/g, formatDate(new Date(), 'YYYY-MM-DD'))
  content = content.replace(/{time}/g, formatDate(new Date(), 'HH:mm:ss'))
  content = content.replace(/{company}/g, '示例公司')
  content = content.replace(/{website}/g, 'https://example.com')
  
  return content
})
</script>

<style scoped lang="scss">
.template-container {
  padding: 24px;
  min-height: calc(100vh - 120px);
  background-color: var(--el-fill-color-blank);

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;

      h2 {
        margin: 0;
        font-size: 24px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }

      .search-input {
        width: 240px;
      }
    }
  }

  .template-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 24px;
    margin-top: 24px;

    .template-item {
      .template-card {
        background-color: var(--el-bg-color);
        border-radius: 8px;
        box-shadow: var(--el-box-shadow-light);
        transition: all 0.3s ease;
        border: 2px solid transparent;

        &:hover {
          transform: translateY(-2px);
          box-shadow: var(--el-box-shadow);
        }

        &.is-selected {
          border-color: var(--el-color-primary);
        }

        .card-header {
          padding: 16px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-bottom: 1px solid var(--el-border-color-light);

          .more-icon {
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
            color: var(--el-text-color-secondary);

            &:hover {
              background-color: var(--el-fill-color-light);
              color: var(--el-text-color-primary);
            }
          }
        }

        .card-body {
          padding: 16px;
          cursor: pointer;

          .template-name {
            margin: 0 0 8px;
            font-size: 16px;
            font-weight: 600;
            color: var(--el-text-color-primary);
          }

          .template-desc {
            margin: 0 0 16px;
            font-size: 14px;
            color: var(--el-text-color-regular);
            line-height: 1.5;
          }

          .template-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: var(--el-text-color-secondary);

            .time {
              display: flex;
              align-items: center;
              gap: 4px;
            }

            .usage {
              display: flex;
              align-items: center;
              gap: 4px;
            }
          }
        }

        .card-footer {
          padding: 16px;
          display: flex;
          gap: 12px;
          border-top: 1px solid var(--el-border-color-light);
        }
      }
    }
  }
}

.editor-wrapper {
  border: 1px solid var(--el-border-color);
  border-radius: 4px;

  .editor-toolbar {
    padding: 8px;
    border-bottom: 1px solid var(--el-border-color);
    background-color: var(--el-fill-color-light);
  }

  :deep(.el-textarea__inner) {
    border: none;
    border-radius: 0;
  }
}

.preview-content {
  .preview-header {
    margin-bottom: 24px;

    h3 {
      margin: 0 0 16px;
      font-size: 18px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }

    .preview-meta {
      display: flex;
      flex-direction: column;
      gap: 8px;
      font-size: 14px;
      color: var(--el-text-color-regular);
    }
  }

  .preview-body {
    padding: 16px;
    background-color: var(--el-fill-color-light);
    border-radius: 4px;
    min-height: 200px;
  }
}

.variable-list {
  display: flex;
  flex-direction: column;
  gap: 8px;

  .variable-item {
    padding: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: var(--el-fill-color-light);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      background-color: var(--el-color-primary-light-9);
    }

    .label {
      font-weight: 500;
      color: var(--el-text-color-primary);
    }

    .key {
      color: var(--el-text-color-secondary);
      font-family: monospace;
    }
  }
}

// 响应式布局
@media (max-width: 768px) {
  .template-container {
    .page-header {
      flex-direction: column;
      gap: 16px;
      align-items: stretch;

      .header-left {
        flex-direction: column;
        gap: 12px;

        .search-input {
          width: 100%;
        }
      }
    }

    .template-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style> 