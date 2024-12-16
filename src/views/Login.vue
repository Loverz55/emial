<template>
  <div class="login-container">
    <div class="decoration-area">
      <div class="content">
        <h1>邮件自动化系统</h1>
        <p>高效的邮件管理工具，帮助您轻松处理邮件发送、定时任务和模板管理。通过简单的操作即可实现复杂的邮件自动化需求。</p>
      </div>
    </div>
    
    <div class="login-area">
      <div class="login-box">
        <div class="header">
          <img src="@/assets/logo.svg" alt="Logo" class="logo">
          <h2>{{ isLogin ? '欢迎回来' : '注册账号' }}</h2>
          <p>{{ isLogin ? '请登录您的账号' : '创建一个新账号' }}</p>
        </div>
        
        <el-form ref="formRef" :model="formData" :rules="rules" class="login-form">
          <el-form-item prop="username">
            <el-input
              v-model="formData.username"
              :placeholder="isLogin ? '用户名' : '请输入用户名'"
              :prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item v-if="!isLogin" prop="email">
            <el-input
              v-model="formData.email"
              placeholder="请输入邮箱"
              :prefix-icon="Message"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="formData.password"
              type="password"
              :placeholder="isLogin ? '密码' : '请输入密码'"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleSubmit"
            />
          </el-form-item>
          
          <div v-if="isLogin" class="form-footer">
            <el-checkbox v-model="formData.remember">记住密码</el-checkbox>
            <el-link type="primary" :underline="false">忘记密码？</el-link>
          </div>
          
          <el-button
            type="primary"
            class="login-button"
            :loading="loading"
            @click="handleSubmit"
          >
            {{ isLogin ? '登录' : '注册' }}
          </el-button>
          
          <div class="switch-mode">
            <span>{{ isLogin ? '还没有账号？' : '已有账号？' }}</span>
            <el-link type="primary" @click="switchMode">
              {{ isLogin ? '立即注册' : '去登录' }}
            </el-link>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { login, register } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const isLogin = ref(true)
const loading = ref(false)
const formRef = ref(null)

const formData = ref({
  username: '',
  email: '',
  password: '',
  remember: false
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在 3 到 20 个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于 6 个字符', trigger: 'blur' }
  ]
}

// 页面加载时检查本地存储的登录信息
onMounted(() => {
  const savedCredentials = localStorage.getItem('userCredentials')
  if (savedCredentials) {
    const { username, password } = JSON.parse(savedCredentials)
    formData.value.username = username
    formData.value.password = password
    formData.value.remember = true
  }
})

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    if (isLogin.value) {
      // 登录逻辑
      const { data } = await login(formData.value)
      userStore.token = data.access
      userStore.username = data.username
      
      if (formData.value.remember) {
        localStorage.setItem('userCredentials', JSON.stringify({
          username: formData.value.username,
          password: formData.value.password
        }))
      } else {
        localStorage.removeItem('userCredentials')
      }
      
      // 根据用户角色决定跳转路径
      if (data.is_admin) {
        userStore.isAdmin = true
        router.push('/admin/dashboard')
      } else {
        userStore.isAdmin = false
        router.push('/dashboard')
      }
      
      ElMessage.success('登录成功')
    } else {
      // 注册逻辑
      await register({
        username: formData.value.username,
        email: formData.value.email,
        password: formData.value.password
      })
      ElMessage.success('注册成功，请登录')
      isLogin.value = true
      formData.value.password = ''
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error(error.response?.data?.detail || (isLogin.value ? '登录失败' : '注册失败'))
  } finally {
    loading.value = false
  }
}

const switchMode = () => {
  isLogin.value = !isLogin.value
  formData.value = {
    username: '',
    email: '',
    password: '',
    remember: false
  }
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}
</script>

<style scoped lang="scss">
.login-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  z-index: 100;

  .decoration-area {
    flex: 1;
    background: linear-gradient(135deg, #6366F1 0%, #818CF8 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px;
    
    .content {
      max-width: 480px;
      color: #fff;
      
      h1 {
        font-size: 36px;
        margin: 0 0 20px;
        font-weight: 600;
      }
      
      p {
        font-size: 16px;
        margin: 0;
        opacity: 0.9;
        line-height: 1.6;
      }
    }
  }

  .login-area {
    width: 500px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #fff;
    box-shadow: -4px 0 16px rgba(0, 0, 0, 0.05);
    position: relative;
    z-index: 1;
    
    .login-box {
      width: 360px;
      
      .header {
        text-align: center;
        margin-bottom: 40px;
        
        .logo {
          width: 64px;
          height: 64px;
          margin-bottom: 16px;
        }
        
        h2 {
          font-size: 24px;
          color: var(--el-text-color-primary);
          margin: 0 0 8px;
        }
        
        p {
          color: var(--el-text-color-secondary);
          font-size: 14px;
          margin: 0;
        }
      }
      
      .login-form {
        .el-input {
          margin-bottom: 20px;
          
          :deep(.el-input__wrapper) {
            box-shadow: 0 0 0 1px #e4e4e7 inset;
            
            &:hover {
              box-shadow: 0 0 0 1px #d4d4d8 inset;
            }
            
            &.is-focus {
              box-shadow: 0 0 0 1px #6366F1 inset;
            }
          }
        }
        
        .form-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 24px;
        }
        
        .login-button {
          width: 100%;
          height: 40px;
          font-size: 16px;
          background: linear-gradient(135deg, #6366F1 0%, #818CF8 100%);
          border: none;
          transition: all 0.3s ease;
          margin-bottom: 16px;
          
          &:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
          }
          
          &:active {
            transform: translateY(0);
          }
        }
        
        .switch-mode {
          text-align: center;
          color: var(--el-text-color-secondary);
          
          .el-link {
            margin-left: 8px;
          }
        }
      }
    }
  }
}</style> 