<template>
  <div>
    <div class="admin-header">
      <h2>仪表板</h2>
      <p>系统概览与统计信息</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-spinner">
      <span>加载中...</span>
    </div>

    <!-- Stats Cards -->
    <div v-else class="dashboard-stats">
      <div class="stat-card primary" @click="navigateTo('/manage/admin/users')">
        <div class="stat-label">总用户数</div>
        <div class="stat-value">{{ stats.total_users || 0 }}</div>
        <div class="stat-icon">👥</div>
      </div>

      <div class="stat-card success" @click="navigateTo('/manage/admin/entries')">
        <div class="stat-label">总内容数</div>
        <div class="stat-value">{{ stats.total_contents || 0 }}</div>
        <div class="stat-icon">📝</div>
      </div>

      <div class="stat-card warning" @click="navigateTo('/manage/review')">
        <div class="stat-label">待审核</div>
        <div class="stat-value">{{ stats.pending_reviews || 0 }}</div>
        <div class="stat-icon">⏳</div>
      </div>

      <div class="stat-card info" @click="navigateTo('/manage/publish')">
        <div class="stat-label">今日发布</div>
        <div class="stat-value">{{ stats.published_today || 0 }}</div>
        <div class="stat-icon">🚀</div>
      </div>
    </div>

    <!-- Status Distribution -->
    <div class="status-bar-container">
      <h3>内容状态分布</h3>
      <div class="status-bar">
        <div
          class="status-segment draft"
          :style="{ flex: statusDistribution.draft }"
        >
          草稿 {{ statusCounts.draft }}
        </div>
        <div
          class="status-segment pending"
          :style="{ flex: statusDistribution.pending }"
        >
          待审核 {{ statusCounts.pending }}
        </div>
        <div
          class="status-segment reviewed"
          :style="{ flex: statusDistribution.reviewed }"
        >
          已审核 {{ statusCounts.reviewed }}
        </div>
        <div
          class="status-segment rejected"
          :style="{ flex: statusDistribution.rejected }"
        >
          已拒绝 {{ statusCounts.rejected }}
        </div>
        <div
          class="status-segment published"
          :style="{ flex: statusDistribution.published }"
        >
          已发布 {{ statusCounts.published }}
        </div>
      </div>
      <div class="status-legend">
        <div class="legend-item">
          <div class="legend-color draft"></div>
          <span>草稿</span>
        </div>
        <div class="legend-item">
          <div class="legend-color pending"></div>
          <span>待审核</span>
        </div>
        <div class="legend-item">
          <div class="legend-color reviewed"></div>
          <span>已审核</span>
        </div>
        <div class="legend-item">
          <div class="legend-color rejected"></div>
          <span>已拒绝</span>
        </div>
        <div class="legend-item">
          <div class="legend-color published"></div>
          <span>已发布</span>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <!-- <div class="quick-actions">
      <div class="action-card" @click="navigateTo('/manage/admin/users')">
        <i>👥</i>
        <h4>用户管理</h4>
        <p>管理系统用户与权限</p>
      </div>

      <div class="action-card" @click="navigateTo('/manage/admin/deadlines')">
        <i>📅</i>
        <h4>截止日期</h4>
        <p>设置内容截止日期</p>
      </div>

      <div class="action-card" @click="navigateTo('/manage/admin/entries')">
        <i>📝</i>
        <h4>条目管理</h4>
        <p>管理所有内容条目</p>
      </div>

      <div class="action-card" @click="navigateTo('/manage/review')">
        <i>✅</i>
        <h4>内容审核</h4>
        <p>审核待发布内容</p>
      </div>
    </div> -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAdminData } from '../../api/user'

const router = useRouter()

// State
const loading = ref(true)
const stats = ref({
  total_users: 0,
  total_contents: 0,
  pending_reviews: 0,
  published_today: 0,
  status_counts: {
    draft: 0,
    pending: 0,
    reviewed: 0,
    rejected: 0,
    published: 0,
    terminated: 0
  }
})

// 状态计数（直接使用后端返回的数据）
const statusCounts = computed(() => stats.value.status_counts)

// 状态分布（flex values）
const statusDistribution = computed(() => {
  const total = stats.value.total_contents
  if (total === 0) {
    return { draft: 1, pending: 1, reviewed: 1, rejected: 1, published: 1 }
  }
  const counts = statusCounts.value
  return {
    draft: counts.draft / total || 0.2,
    pending: counts.pending / total || 0.2,
    reviewed: counts.reviewed / total || 0.2,
    rejected: counts.rejected / total || 0.2,
    published: counts.published / total || 0.2
  }
})

// Fetch admin dashboard data
async function fetchDashboardData() {
  try {
    loading.value = true

    // Get all dashboard data from admin API (包含状态统计)
    const adminData = await getAdminData()
    if (adminData.success && adminData.stats) {
      stats.value = adminData.stats
    }
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  } finally {
    loading.value = false
  }
}

function navigateTo(path) {
  router.push(path)
}

onMounted(fetchDashboardData)
</script>

<style scoped>
@import '../../styles/admin.css';
</style>
