<template>
  <div class="dashboard-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="statistics-row">
      <el-col :span="6" v-for="(item, index) in statisticsData" :key="index">
        <el-card class="statistics-card" :body-style="{ padding: '20px' }">
          <div class="card-content">
            <div class="icon-wrapper" :style="{ background: item.bgColor }">
              <el-icon :size="24">
                <User v-if="item.type === 'user'" />
                <Message v-if="item.type === 'email'" />
                <Files v-if="item.type === 'template'" />
                <Document v-if="item.type === 'log'" />
              </el-icon>
            </div>
            <div class="statistics-info">
              <div class="value">{{ item.value }}</div>
              <div class="label">{{ item.label }}</div>
            </div>
          </div>
          <div class="trend">
            <span :class="['trend-value', item.trend > 0 ? 'up' : 'down']">
              {{ Math.abs(item.trend) }}%
            </span>
            <span class="trend-label">较上周</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表和活动列表 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>邮件发送趋势</span>
              <el-radio-group v-model="chartTimeRange" size="small">
                <el-radio-button label="week">本周</el-radio-button>
                <el-radio-button label="month">本月</el-radio-button>
                <el-radio-button label="year">全年</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container" ref="chartRef"></div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="activity-card">
          <template #header>
            <div class="card-header">
              <span>系统动态</span>
              <el-button text>查看全部</el-button>
            </div>
          </template>
          <div class="activity-list">
            <el-timeline>
              <el-timeline-item
                v-for="(activity, index) in activities"
                :key="index"
                :type="activity.type"
                :color="activity.color"
                :timestamp="activity.time"
              >
                {{ activity.content }}
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 用户和模板列表 -->
    <el-row :gutter="20" class="list-row">
      <el-col :span="12">
        <el-card class="list-card">
          <template #header>
            <div class="card-header">
              <span>最新用户</span>
              <el-button text @click="$router.push('/admin/users')">管理用户</el-button>
            </div>
          </template>
          <el-table :data="recentUsers" :show-header="false" style="width: 100%">
            <el-table-column width="50">
              <template #default="scope">
                <el-avatar :size="32" :src="scope.row.avatar">
                  {{ scope.row.username.charAt(0).toUpperCase() }}
                </el-avatar>
              </template>
            </el-table-column>
            <el-table-column prop="username" />
            <el-table-column prop="email" />
            <el-table-column prop="created_at" align="right" width="150">
              <template #default="scope">
                {{ formatDate(scope.row.created_at, 'MM-DD HH:mm') }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="list-card">
          <template #header>
            <div class="card-header">
              <span>热门模板</span>
              <el-button text @click="$router.push('/admin/templates')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="popularTemplates" :show-header="false" style="width: 100%">
            <el-table-column width="50">
              <template #default="scope">
                <el-icon :size="24" :style="{ color: scope.row.color }">
                  <Files />
                </el-icon>
              </template>
            </el-table-column>
            <el-table-column prop="name" />
            <el-table-column prop="category" width="100">
              <template #default="scope">
                <el-tag size="small" :type="scope.row.tagType">{{ scope.row.category }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="usage_count" align="right" width="100">
              <template #default="scope">
                已使用 {{ scope.row.usage_count }} 次
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { User, Message, Files, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { formatDate } from '@/utils/format'
import * as echarts from 'echarts'
import { 
  getAdminStats, 
  getAdminChartData, 
  getSystemActivities, 
  getRecentUsers, 
  getPopularTemplates 
} from '@/api/dashboard'

// 基础数据定义
const statisticsData = ref([])
const chartTimeRange = ref('week')
const activities = ref([])
const recentUsers = ref([])
const popularTemplates = ref([])
const chartRef = ref(null)
let chart = null

// 获取统计数据
const fetchStats = async () => {
  try {
    const { data } = await getAdminStats()
    statisticsData.value = [
      {
        label: '总用户数',
        value: data.total_users,
        type: 'user',
        trend: data.trends.user_growth,
        bgColor: 'rgb(var(--el-color-primary-rgb), 0.1)'
      },
      {
        label: '今日发送',
        value: data.today_sent,
        type: 'email',
        trend: data.trends.sent_growth,
        bgColor: 'rgb(var(--el-color-success-rgb), 0.1)'
      },
      {
        label: '模板数量',
        value: data.template_count,
        type: 'template',
        trend: data.trends.template_growth,
        bgColor: 'rgb(var(--el-color-warning-rgb), 0.1)'
      },
      {
        label: '系统日志',
        value: data.log_count,
        type: 'log',
        trend: data.trends.log_growth,
        bgColor: 'rgb(var(--el-color-info-rgb), 0.1)'
      }
    ]
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  }
}

const updateChart = (data) => {
  if (!chart) return
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['成功', '失败'],
      right: '5%',
      top: '2%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '40px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.labels,
      axisLine: {
        lineStyle: {
          color: '#eee'
        }
      }
    },
    yAxis: {
      type: 'value',
      splitLine: {
        lineStyle: {
          color: '#eee'
        }
      }
    },
    series: [
      {
        name: '成功',
        type: 'line',
        smooth: true,
        data: data.data[0],
        itemStyle: {
          color: '#10b981'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgba(16, 185, 129, 0.3)'
            },
            {
              offset: 1,
              color: 'rgba(16, 185, 129, 0.1)'
            }
          ])
        }
      },
      {
        name: '失败',
        type: 'line',
        smooth: true,
        data: data.data[1],
        itemStyle: {
          color: '#ef4444'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgba(239, 68, 68, 0.3)'
            },
            {
              offset: 1,
              color: 'rgba(239, 68, 68, 0.1)'
            }
          ])
        }
      }
    ]
  }
  
  chart.setOption(option)
}

// 获取图表数据
const fetchChartData = async () => {
  try {
    const { data } = await getAdminChartData({ range: chartTimeRange.value })
    console.log('图表数据:', data)  // 添加日志
    updateChart(data)
  } catch (error) {
    console.error('获取图表数据失败:', error)
    ElMessage.error('获取图表数据失败')
  }
}

// 获取系统动态
const fetchActivities = async () => {
  try {
    const { data } = await getSystemActivities()
    activities.value = data
  } catch (error) {
    console.error('获取系统动态失败:', error)
    ElMessage.error('获取系统动态失败')
  }
}

// 获取最新用户
const fetchRecentUsers = async () => {
  try {
    const { data } = await getRecentUsers()
    recentUsers.value = data
  } catch (error) {
    console.error('获取最新用户失败:', error)
    ElMessage.error('获取最新用户失败')
  }
}

// 获取热门模板
const fetchPopularTemplates = async () => {
  try {
    const { data } = await getPopularTemplates()
    popularTemplates.value = data
  } catch (error) {
    console.error('获取热门模板失败:', error)
    ElMessage.error('获取热门模板失败')
  }
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      axisLine: {
        lineStyle: {
          color: '#eee'
        }
      }
    },
    yAxis: {
      type: 'value',
      splitLine: {
        lineStyle: {
          color: '#eee'
        }
      }
    },
    series: [
      {
        name: '发送量',
        type: 'line',
        smooth: true,
        data: [120, 132, 101, 134, 90, 230, 210],
        itemStyle: {
          color: '#6366f1'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgba(99, 102, 241, 0.3)'
            },
            {
              offset: 1,
              color: 'rgba(99, 102, 241, 0.1)'
            }
          ])
        }
      }
    ]
  }
  
  chart.setOption(option)
}

// 监听图表时间范围变化
watch(chartTimeRange, () => {
  fetchChartData()
})

// 页面加载时获取数据
onMounted(() => {
  fetchStats()
  fetchChartData()
  fetchActivities()
  fetchRecentUsers()
  fetchPopularTemplates()
  
  initChart()
  window.addEventListener('resize', initChart)
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
  }
  window.removeEventListener('resize', initChart)
})
</script>

<style scoped lang="scss">
.dashboard-container {
  padding: 20px;
  
  .statistics-row {
    margin-bottom: 20px;
    
    .statistics-card {
      height: 100%;
      transition: all 0.3s;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      .card-content {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 16px;
        
        .icon-wrapper {
          width: 48px;
          height: 48px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          
          .el-icon {
            font-size: 24px;
            color: var(--el-color-primary);
          }
        }
        
        .statistics-info {
          flex: 1;
          
          .value {
            font-size: 24px;
            font-weight: 600;
            color: var(--el-text-color-primary);
            line-height: 1.2;
          }
          
          .label {
            font-size: 14px;
            color: var(--el-text-color-secondary);
            margin-top: 4px;
          }
        }
      }
      
      .trend {
        font-size: 13px;
        
        .trend-value {
          &.up {
            color: #10b981;
            &::before {
              content: '+';
            }
          }
          
          &.down {
            color: #ef4444;
            &::before {
              content: '-';
            }
          }
        }
        
        .trend-label {
          color: var(--el-text-color-secondary);
          margin-left: 8px;
        }
      }
    }
  }
  
  .chart-row {
    margin-bottom: 20px;
    
    .chart-card {
      .chart-container {
        height: 350px;
      }
    }
    
    .activity-card {
      .activity-list {
        padding: 0 12px;
        
        .el-timeline {
          padding-top: 8px;
        }
      }
    }
  }
  
  .list-row {
    .list-card {
      .el-table {
        --el-table-border-color: transparent;
        
        .el-table__cell {
          padding: 12px 0;
        }
      }
    }
  }
  
  :deep(.card-header) {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    span {
      font-size: 16px;
      font-weight: 500;
    }
  }
}
</style> 