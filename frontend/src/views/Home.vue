<template>
  <div class="home">
    <div class="search-section">
      <div class="search-container">
        <h2 class="search-title">追踪事件来龙去脉</h2>
        <p class="search-subtitle">输入事件名称，获取完整的事件分析报告</p>
        
        <div class="search-box">
          <el-input
            v-model="searchInput"
            placeholder="请输入事件名称，如：九子夺嫡事件"
            size="large"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button 
                type="primary" 
                size="large" 
                :loading="loading"
                @click="handleSearch"
              >
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
            </template>
          </el-input>
        </div>
      </div>
    </div>

    <!-- 事件分析结果 -->
    <div v-if="eventData" class="event-section">
      <el-card class="event-card">
        <template #header>
          <div class="card-header">
            <h3>{{ eventData.event_name }}</h3>
            <el-button 
              v-if="userStore.isLoggedIn" 
              type="primary" 
              @click="addToFavorites"
              :loading="favoriteLoading"
            >
              <el-icon><Star /></el-icon>
              收藏事件
            </el-button>
          </div>
        </template>

        <!-- 事件基本信息 -->
        <div class="event-info">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="info-item">
                <h4>核心人物</h4>
                <p>{{ eventData.key_men }}</p>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <h4>最新进展</h4>
                <p>{{ eventData.latest }}</p>
              </div>
            </el-col>
          </el-row>

          <div class="info-item">
            <h4>事件总览</h4>
            <p>{{ eventData.event_overview }}</p>
          </div>

          <div class="info-item">
            <h4>关键讨论点</h4>
            <p>{{ eventData.key_point }}</p>
          </div>
        </div>

        <!-- 事件详细分析 -->
        <el-divider />
        <div class="event-analysis">
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="analysis-item">
                <h4>事件起因</h4>
                <p>{{ eventData.event_cause }}</p>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="analysis-item">
                <h4>事件经过</h4>
                <p>{{ eventData.event_process }}</p>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="analysis-item">
                <h4>事件结果</h4>
                <p>{{ eventData.event_result }}</p>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 时间线 -->
        <el-divider />
        <div class="timeline-section">
          <h4>事件时间线</h4>
          <el-timeline>
            <el-timeline-item
              v-for="(item, index) in eventData.timeline"
              :key="index"
              :timestamp="item.time"
              placement="top"
            >
              <el-card>
                <h5>{{ item.event_phase }}</h5>
                <p><strong>涉及人物：</strong>{{ item.involved_people }}</p>
                <p><strong>事件描述：</strong>{{ item.plot_description }}</p>
                <p v-if="item.evidence"><strong>证明材料：</strong>{{ item.evidence }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-card>
    </div>

    <!-- 新闻列表 -->
    <div v-if="newsList.length > 0" class="news-section">
      <h3>新闻来源</h3>
      <el-card v-for="(news, index) in newsList" :key="index" class="news-card">
        <p class="news-text">{{ news }}</p>
      </el-card>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'
import api from '../utils/api'

const userStore = useUserStore()

const searchInput = ref('')
const loading = ref(false)
const favoriteLoading = ref(false)
const eventData = ref(null)
const newsList = ref([])

const handleSearch = async () => {
  if (!searchInput.value.trim()) {
    ElMessage.warning('请输入事件名称')
    return
  }

  loading.value = true
  eventData.value = null
  newsList.value = []

  try {
    const response = await api.post('/events/search', {
      input: searchInput.value
    })

    const data = response.data.data
    eventData.value = data
    newsList.value = data.news_list || []

    ElMessage.success('搜索成功')
  } catch (error) {
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
    }
  } finally {
    loading.value = false
  }
}

const addToFavorites = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }

  favoriteLoading.value = true

  try {
    await api.post('/favorites', eventData.value)
    ElMessage.success('收藏成功')
  } catch (error) {
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
    }
  } finally {
    favoriteLoading.value = false
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.search-section {
  text-align: center;
  padding: 40px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  margin-bottom: 30px;
}

.search-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 0 20px;
}

.search-title {
  font-size: 32px;
  margin-bottom: 10px;
  font-weight: 600;
}

.search-subtitle {
  font-size: 16px;
  margin-bottom: 30px;
  opacity: 0.9;
}

.search-box {
  max-width: 500px;
  margin: 0 auto;
}

.news-section {
  margin-bottom: 30px;
}

.news-section h3 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.news-card {
  margin-bottom: 15px;
}

.news-text {
  line-height: 1.6;
  color: #555;
}

.event-section {
  margin-bottom: 30px;
}

.event-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #2c3e50;
}

.event-info {
  margin-bottom: 20px;
}

.info-item {
  margin-bottom: 20px;
}

.info-item h4 {
  color: #409EFF;
  margin-bottom: 8px;
  font-size: 16px;
}

.info-item p {
  line-height: 1.6;
  color: #555;
  margin: 0;
}

.event-analysis {
  margin-bottom: 20px;
}

.analysis-item {
  margin-bottom: 20px;
}

.analysis-item h4 {
  color: #409EFF;
  margin-bottom: 8px;
  font-size: 16px;
}

.analysis-item p {
  line-height: 1.6;
  color: #555;
  margin: 0;
}

.timeline-section h4 {
  color: #409EFF;
  margin-bottom: 20px;
  font-size: 18px;
}

.timeline-section .el-card {
  margin-bottom: 10px;
}

.timeline-section h5 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 16px;
}

.timeline-section p {
  margin-bottom: 5px;
  line-height: 1.5;
  color: #555;
}

.timeline-section strong {
  color: #409EFF;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-title {
    font-size: 24px;
  }
  
  .search-subtitle {
    font-size: 14px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .el-col {
    margin-bottom: 20px;
  }
}
</style>