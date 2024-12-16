<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in statistics" :key="stat.title">
        <el-card class="stat-card" :class="stat.type">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon>
                <component :is="stat.icon" />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-title">{{ stat.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>本周发送统计</h3>
            </div>
          </template>
          <div class="chart-container" ref="chartRef"></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="recent-tasks">
          <template #header>
            <div class="card-header">
              <h3>最近发送记录</h3>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="task in recentTasks"
              :key="task.id"
              :type="task.status === 'completed' ? 'success' : 'danger'"
              :timestamp="formatDate(task.send_time)"
            >
              <div class="task-item">
                <div class="task-header">
                  <h4>{{ task.subject }}</h4>
                  <div class="task-tags">
                    <el-tag 
                      :type="task.status === 'completed' ? 'success' : 'danger'"
                      size="small"
                    >
                      {{ task.status === 'completed' ? '发送成功' : '发送失败' }}
                    </el-tag>
                    <el-tag 
                      v-if="task.schedule"
                      type="warning" 
                      size="small"
                      class="ml-2"
                    >
                      定时任务
                    </el-tag>
                  </div>
                </div>
                <div class="task-info">
                  <p>收件人: {{ task.recipient }}</p>
                  <template v-if="task.schedule">
                    <p class="schedule-info">
                      <el-icon><Timer /></el-icon>
                      <span>发送时间: {{ formatDateTime(task.schedule.schedule_time) }}</span>
                    </p>
                    <p class="schedule-info">
                      <el-icon><Calendar /></el-icon>
                      <span>重复类型: {{ getRepeatTypeText(task.schedule.repeat_type) }}</span>
                    </p>
                    <p v-if="task.schedule.repeat_type === 'weekly'" class="schedule-info">
                      <el-icon><List /></el-icon>
                      <span>重复日期: {{ formatWeekDays(task.schedule.week_days) }}</span>
                    </p>
                    <p v-if="task.schedule.repeat_type === 'monthly'" class="schedule-info">
                      <el-icon><List /></el-icon>
                      <span>每月 {{ task.schedule.month_day }} 号发送</span>
                    </p>
                    <p class="schedule-info">
                      <el-icon><AlarmClock /></el-icon>
                      <span>下次执行: {{ formatDateTime(task.schedule.next_run) }}</span>
                    </p>
                  </template>
                </div>
                <p v-if="task.status === 'failed'" class="error-message">
                  <el-icon><Warning /></el-icon>
                  {{ task.error_message }}
                </p>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { getDashboardStats, getRecentTasks, getWeeklyStats } from '@/api/dashboard'
import { formatDate } from '@/utils/format'
import {
  Message,
  Check,
  Warning,
  Timer,
  Calendar,
  List,
  AlarmClock
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { useThemeStore } from '@/stores/theme'
import dayjs from 'dayjs'

const statistics = ref([
  { title: '总发送数', value: 0, icon: Message, type: 'total' },
  { title: '发送成功', value: 0, icon: Check, type: 'success' },
  { title: '发送失败', value: 0, icon: Warning, type: 'failed' },
  { title: '定时任务', value: 0, icon: Timer, type: 'scheduled' }
])

const recentTasks = ref([])
const weeklyData = ref([])
const chartRef = ref(null)
let chart = null

// 更新图表数据
const updateChart = () => {
  if (!chart) {
    console.warn('图表实例未初始化')
    return
  }
  
  console.log('周统计原始数据:', weeklyData.value)
  
  // 确保数据格式正确
  const xAxisData = weeklyData.value.map(item => item.day)
  const successData = weeklyData.value.map(item => item.success || 0)
  const failedData = weeklyData.value.map(item => item.failed || 0)
  
  console.log('处理后的数据:', {
    xAxis: xAxisData,
    success: successData,
    failed: failedData
  })
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'line',
        lineStyle: {
          color: '#409EFF',
          width: 2
        }
      }
    },
    legend: {
      data: ['发送成功', '发送失败'],
      bottom: '5%',
      icon: 'circle',
      itemWidth: 10,
      itemHeight: 10,
      textStyle: {
        fontSize: 12
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '8%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisLabel: {
        interval: 0,
        fontSize: 12,
        color: '#666'
      },
      axisLine: {
        lineStyle: {
          color: '#ddd'
        }
      },
      axisTick: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLabel: {
        fontSize: 12,
        color: '#666'
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#eee'
        }
      },
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      }
    },
    series: [
      {
        name: '发送成功',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: {
          color: '#67C23A'
        },
        lineStyle: {
          width: 3,
          shadowColor: 'rgba(103,194,58,0.3)',
          shadowBlur: 10
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: 'rgba(103,194,58,0.2)'
              },
              {
                offset: 1,
                color: 'rgba(103,194,58,0.02)'
              }
            ]
          }
        },
        data: successData
      },
      {
        name: '发送失败',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: {
          color: '#F56C6C'
        },
        lineStyle: {
          width: 3,
          shadowColor: 'rgba(245,108,108,0.3)',
          shadowBlur: 10
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: 'rgba(245,108,108,0.2)'
              },
              {
                offset: 1,
                color: 'rgba(245,108,108,0.02)'
              }
            ]
          }
        },
        data: failedData
      }
    ]
  }
  
  console.log('图表配置:', option)
  chart.setOption(option, true)
}

const fetchDashboardData = async () => {
  try {
    const [statsRes, tasksRes, weeklyRes] = await Promise.all([
      getDashboardStats(),
      getRecentTasks(),
      getWeeklyStats()
    ])
    
    console.log('获取到的周统计数据:', weeklyRes)
    
    // 更新统计数据
    statistics.value[0].value = statsRes.data.totalSent
    statistics.value[1].value = statsRes.data.successCount
    statistics.value[2].value = statsRes.data.failedCount
    statistics.value[3].value = statsRes.data.scheduledCount
    
    // 更新最近任务
    recentTasks.value = tasksRes.data
    
    // 更新周统计数据
    weeklyData.value = weeklyRes.data
    
    // 确保图表已初始化
    if (!chart && chartRef.value) {
      initChart()
    }
    
    // 更新图表
    updateChart()
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
  }
}

// 初始化图表
const initChart = () => {
  if (chart) {
    chart.dispose()
  }
  
  if (!chartRef.value) {
    console.warn('图表容器未找到')
    return
  }
  
  chart = echarts.init(chartRef.value)
  console.log('图表初始化完成')
  
  // 监听窗口大小变化
  const handleResize = () => {
    chart && chart.resize()
  }
  window.addEventListener('resize', handleResize)
  
  // 组件卸载时移除监听
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
    if (chart) {
      chart.dispose()
      chart = null
    }
  })
}

// 监听主题��化
const themeStore = useThemeStore()
watch(() => themeStore.isDark, (newValue) => {
  if (chart) {
    chart.dispose()
    chart = echarts.init(chartRef.value, newValue ? 'dark' : undefined)
    updateChart()
  }
})

// 格式化时间
const formatTime = (time) => {
  if (!time) return ''
  return time.substring(0, 5) // 只显示 HH:mm
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
  if (!days) return ''
  const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return days.map(day => weekDays[parseInt(day)]).join('、')
}

const formatDateTime = (time) => {
  if (!time) return '未设置'
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

onMounted(() => {
  initChart()
  fetchDashboardData()
})
</script>

<style scoped lang="scss">
.dashboard-container {
  padding: 20px;

  .stat-card {
    height: 100px;
    
    &.total {
      .stat-icon {
        background: linear-gradient(135deg, #1890ff, #36cfc9);
      }
    }
    
    &.success {
      .stat-icon {
        background: linear-gradient(135deg, #52c41a, #95de64);
      }
    }
    
    &.failed {
      .stat-icon {
        background: linear-gradient(135deg, #ff4d4f, #ff7875);
      }
    }
    
    &.scheduled {
      .stat-icon {
        background: linear-gradient(135deg, #722ed1, #b37feb);
      }
    }

    .stat-content {
      display: flex;
      align-items: center;
      height: 100%;
      padding: 0 20px;

      .stat-icon {
        width: 48px;
        height: 48px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;

        .el-icon {
          font-size: 24px;
          color: white;
        }
      }

      .stat-info {
        flex: 1;

        .stat-value {
          font-size: 24px;
          font-weight: 600;
          color: var(--el-text-color-primary);
          line-height: 1.2;
        }

        .stat-title {
          font-size: 14px;
          color: var(--el-text-color-secondary);
          margin-top: 4px;
        }
      }
    }
  }

  .chart-card {
    margin-bottom: 20px;

    .chart-container {
      height: 400px;
    }
  }

  .recent-tasks {
    .task-item {
      .task-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;

        h4 {
          margin: 0;
          color: var(--el-text-color-primary);
          font-size: 14px;
        }

        .task-tags {
          display: flex;
          gap: 8px;
        }
      }

      .task-info {
        margin: 10px 0;
        color: #666;

        .schedule-info {
          display: flex;
          align-items: center;
          margin: 5px 0;
          font-size: 14px;

          .el-icon {
            margin-right: 5px;
            color: #409EFF;
          }
        }

        .error-message {
          color: #F56C6C;
          margin-top: 10px;
          display: flex;
          align-items: center;

          .el-icon {
            margin-right: 5px;
          }
        }
      }
    }
  }

  .card-header {
    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 500;
    }
  }

  .mt-4 {
    margin-top: 20px;
  }

  .ml-2 {
    margin-left: 8px;
  }
}
</style> 