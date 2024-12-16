<template>
  <div class="users-container">
    <transition-group 
      v-if="isMobile" 
      name="list" 
      tag="div" 
      class="user-cards"
    >
      <el-card v-for="user in userList" :key="user.id" class="user-card">
        <div class="user-card-header">
          <el-avatar :size="32">{{ user.username.charAt(0).toUpperCase() }}</el-avatar>
          <span class="username">{{ user.username }}</span>
        </div>
        <div class="user-card-content">
          <p><el-tag :type="user.isAdmin ? 'danger' : 'success'">
            {{ user.isAdmin ? '管理员' : '普通用户' }}
          </el-tag></p>
          <p>{{ user.email }}</p>
          <p>{{ user.createTime }}</p>
        </div>
        <div class="user-card-actions">
          <el-button-group>
            <el-button type="primary" @click="handleEdit(user)">编辑</el-button>
            <el-button type="danger" @click="handleDelete(user)">删除</el-button>
          </el-button-group>
        </div>
      </el-card>
    </transition-group>
    
    <el-table v-else :data="userList" style="width: 100%">
      <transition-group name="list" tag="tbody">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="isAdmin" label="角色">
          <template #default="{ row }">
            <el-tag :type="row.isAdmin ? 'danger' : 'success'">
              {{ row.isAdmin ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" @click="handleEdit(row)">
                编辑
              </el-button>
              <el-button type="danger" @click="handleDelete(row)">
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </transition-group>
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
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 模拟用户数据
const userList = ref([
  {
    id: 1,
    username: '管理员',
    email: 'admin@example.com',
    isAdmin: true,
    createTime: '2024-03-20 10:00:00'
  },
  {
    id: 2,
    username: '测试用户',
    email: 'user@example.com',
    isAdmin: false,
    createTime: '2024-03-20 11:00:00'
  }
])

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(2)

// 判断是否为移动端
const isMobile = computed(() => {
  return window.innerWidth <= 768
})

const handleAdd = () => {
  ElMessage.info('添加用户功能开发中')
}

const handleEdit = (row) => {
  ElMessage.info('编辑用户功能开发中')
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除用户 ${row.username} 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.success('删除成功')
  }).catch(() => {
    // 取消删除
  })
}

const handleSizeChange = (val) => {
  pageSize.value = val
  // 重新加载数据
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  // 重新加载数据
}
</script>

<style scoped>
.users-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: var(--text-primary);
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-button-group) {
  display: flex;
  gap: 8px;
}

.user-cards {
  display: grid;
  gap: 16px;
}

.user-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.user-card-content {
  margin-bottom: 16px;
}

.user-card-content p {
  margin: 8px 0;
}

.user-card-actions {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .users-container {
    padding: 16px;
  }
}
</style> 