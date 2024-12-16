import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue')
    },
    {
      path: '/admin',
      component: AdminLayout,
      redirect: '/admin/dashboard',
      meta: { requiresAuth: true, isAdmin: true },
      children: [
        {
          path: 'dashboard',
          name: 'AdminDashboard',
          component: () => import('@/views/admin/dashboard/index.vue'),
          meta: { title: '控制台' }
        },
        {
          path: 'users',
          name: 'Users',
          component: () => import('@/views/admin/users/index.vue'),
          meta: { title: '用户管理' }
        },
        {
          path: 'roles',
          name: 'Roles',
          component: () => import('@/views/admin/roles/index.vue'),
          meta: { title: '角色权限' }
        },
        {
          path: 'email-config',
          name: 'EmailConfig',
          component: () => import('@/views/admin/email-config/index.vue'),
          meta: { title: '邮箱配置' }
        },
        {
          path: 'logs',
          name: 'Logs',
          component: () => import('@/views/admin/logs/index.vue'),
          meta: { title: '系统日志' }
        }
      ]
    },
    {
      path: '/',
      component: DefaultLayout,
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/dashboard/index.vue'),
          meta: { title: '工作台' }
        },
        {
          path: 'send',
          name: 'Send',
          component: () => import('@/views/send/index.vue'),
          meta: { title: '发送邮件' }
        },
        {
          path: 'templates',
          name: 'Templates',
          component: () => import('@/views/templates/index.vue'),
          meta: { title: '邮件模板' }
        },
        {
          path: 'history',
          name: 'History',
          component: () => import('@/views/history/index.vue'),
          meta: {
            title: '发送记录',
            requiresAuth: true
          }
        }
      ]
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 如果有 token 但没有用户信息，尝试获取用户信息
  if (userStore.token && !userStore.username) {
    try {
      await userStore.getInfo()
    } catch (error) {
      userStore.clearUserInfo()
      next('/login')
      return
    }
  }
  
  if (to.path === '/login') {
    if (userStore.token) {
      next(userStore.isAdmin ? '/admin/dashboard' : '/dashboard')
    } else {
      next()
    }
    return
  }

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!userStore.token) {
      next('/login')
      return
    }
    
    // 检查管理员权限
    if (to.matched.some(record => record.meta.isAdmin) && !userStore.isAdmin) {
      next('/dashboard')
      return
    }
  }
  
  next()
})

export default router 