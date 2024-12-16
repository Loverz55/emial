<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">
        <img src="@/assets/logo.svg" alt="Logo">
        <h1>邮件系统</h1>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        class="menu"
        :router="true"
        :background-color="isDark ? 'var(--el-bg-color)' : '#fff'"
        :text-color="isDark ? 'var(--el-text-color-primary)' : '#303133'"
        :active-text-color="isDark ? 'var(--el-color-primary)' : 'var(--el-color-primary)'"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>工作台</span>
        </el-menu-item>
        
        <el-menu-item index="/send">
          <el-icon><Message /></el-icon>
          <span>发送邮件</span>
        </el-menu-item>
        
        <el-menu-item index="/templates">
          <el-icon><Files /></el-icon>
          <span>邮件模板</span>
        </el-menu-item>
        
        <el-menu-item index="/history">
          <el-icon><List /></el-icon>
          <span>发送记录</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="left">
          <h2>邮件自动化系统</h2>
        </div>
        <div class="right">
          <el-switch
            v-model="isDark"
            class="theme-switch"
            inline-prompt
            :active-icon="Moon"
            :inactive-icon="Sunny"
            @change="toggleTheme"
          />
          <el-dropdown trigger="click">
            <div class="user-info">
              <el-avatar :size="32" class="user-avatar">
                {{ userStore.username?.charAt(0)?.toUpperCase() || 'U' }}
              </el-avatar>
              <span class="username">{{ userStore.username || '用户' }}</span>
              <el-icon class="dropdown-icon"><CaretBottom /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'
import { ElMessageBox, ElMessage } from 'element-plus'
import {
  HomeFilled,
  Message,
  Files,
  List,
  CaretBottom,
  SwitchButton,
  Moon,
  Sunny
} from '@element-plus/icons-vue'
import { storeToRefs } from 'pinia'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()
const { isDark } = storeToRefs(themeStore)

const activeMenu = computed(() => route.path)

const toggleTheme = (value) => {
  themeStore.setTheme(value)
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await userStore.logoutAction()
    ElMessage.success('退出成功')
    router.push('/login')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '退出失败')
    }
  }
}
</script>

<style scoped lang="scss">
.layout {
  height: 100vh;
}

.aside {
  background-color: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-light);
  
  .logo {
    height: 60px;
    padding: 0 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid var(--el-border-color-light);
    background-color: var(--el-bg-color);
    
    img {
      height: 32px;
      width: 32px;
    }
    
    h1 {
      font-size: 16px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      margin: 0;
      white-space: nowrap;
    }
  }
  
  .menu {
    border-right: none;
    background-color: var(--el-bg-color);
    
    :deep(.el-menu) {
      background-color: var(--el-bg-color);
    }
    
    :deep(.el-menu-item) {
      height: 50px;
      line-height: 50px;
      margin: 4px 0;
      padding: 0 20px !important;
      border-radius: 4px;
      margin: 4px 10px;
      background-color: var(--el-bg-color);
      
      .el-icon {
        font-size: 18px;
      }

      &.is-active {
        background-color: var(--el-color-primary-light-9);
        color: var(--el-color-primary);
        
        &::before {
          display: none;
        }
      }

      &:hover {
        color: var(--el-color-primary);
        background-color: var(--el-color-primary-light-9);
      }
    }
  }
}

.header {
  background-color: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
  
  .left {
    h2 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }
  }
  
  .right {
    display: flex;
    align-items: center;
    gap: 20px;
    
    .theme-switch {
      margin-right: 8px;
    }
    
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 6px 12px;
      border-radius: 40px;
      background: var(--el-fill-color-light);
      transition: all 0.3s ease;
      border: 1px solid var(--el-border-color-lighter);
      
      &:hover {
        background: var(--el-fill-color);
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      }
      
      .user-avatar {
        background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-primary-light-3));
        color: white;
        font-weight: 600;
        box-shadow: 0 2px 6px rgba(var(--el-color-primary-rgb), 0.2);
      }
      
      .username {
        font-size: 14px;
        font-weight: 500;
        color: var(--el-text-color-primary);
      }
      
      .dropdown-icon {
        font-size: 12px;
        color: var(--el-text-color-secondary);
      }
    }
  }
}

.main {
  padding: 20px;
  background-color: var(--el-bg-color-page);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .user-info {
    padding: 6px;
    
    .username {
      display: none;
    }

    .dropdown-icon {
      display: none;
    }
  }
}
</style> 