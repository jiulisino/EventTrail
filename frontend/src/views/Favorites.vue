<template>
  <div class="favorites">
    <div class="page-header">
      <h2>我的收藏</h2>
      <p>管理您收藏的事件，及时获取最新进展</p>
    </div>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="favorites.length === 0" class="empty-container">
      <el-empty description="暂无收藏事件">
        <el-button type="primary" @click="$router.push('/')">
          去搜索事件
        </el-button>
      </el-empty>
    </div>

    <div v-else class="favorites-container">
      <el-row :gutter="20">
        <!-- 左侧收藏列表 -->
        <el-col :span="8">
          <el-card class="favorites-list">
            <template #header>
              <div class="list-header">
                <span>收藏列表</span>
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="refreshAll"
                  :loading="refreshAllLoading"
                >
                  <el-icon><Refresh /></el-icon>
                  全部刷新
                </el-button>
              </div>
            </template>

            <div class="favorites-items">
              <div
                v-for="favorite in favorites"
                :key="favorite.id"
                class="favorite-item"
                :class="{ active: selectedFavorite?.id === favorite.id }"
                @click="selectFavorite(favorite)"
              >
                <div class="item-content">
                  <h4>{{ favorite.event_name }}</h4>
                  <p class="item-time">
                    收藏时间：{{ formatDate(favorite.created_at) }}
                  </p>
                  <p class="item-refresh">
                    最后更新：{{ formatDate(favorite.last_refresh) }}
                  </p>
                </div>
                <div class="item-actions">
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click.stop="deleteFavorite(favorite.id)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧事件详情 -->
        <el-col :span="16">
          <div v-if="selectedFavorite" class="favorite-detail">
            <el-card>
              <template #header>
                <div class="detail-header">
                  <h3>{{ selectedFavorite.event_name }}</h3>
                  <el-button 
                    type="primary" 
                    @click="refreshFavorite"
                    :loading="refreshLoading"
                  >
                    <el-icon><Refresh /></el-icon>
                    刷新进展
                  </el-button>
                </div>
              </template>

              <!-- 事件基本信息 -->
              <div class="event-info">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div class="info-item">
                      <h4>核心人物</h4>
                      <p>{{ selectedFavorite.key_men }}</p>
                    </div>
                  </el-col>
                  <el-col :span="12">
                    <div class="info-item">
                      <h4>最新进展</h4>
                      <p>{{ selectedFavorite.latest }}</p>
                    </div>
                  </el-col>
                </el-row>

                <div class="info-item">
                  <h4>事件总览</h4>
                  <p>{{ selectedFavorite.event_overview }}</p>
                </div>

                <div class="info-item">
                  <h4>关键讨论点</h4>
                  <p>{{ selectedFavorite.key_point }}</p>
                </div>
              </div>

              <!-- 事件详细分析 -->
              <el-divider />
              <div class="event-analysis">
                <el-row :gutter="20">
                  <el-col :span="8">
                    <div class="analysis-item">
                      <h4>事件起因</h4>
                      <p>{{ selectedFavorite.event_cause }}</p>
                    </div>
                  </el-col>
                  <el-col :span="8">
                    <div class="analysis-item">
                      <h4>事件经过</h4>
                      <p>{{ selectedFavorite.event_process }}</p>
                    </div>
                  </el-col>
                  <el-col :span="8">
                    <div class="analysis-item">
                      <h4>事件结果</h4>
                      <p>{{ selectedFavorite.event_result }}</p>
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
                    v-for="(item, index) in selectedFavorite.timeline"
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

          <div v-else class="no-selection">
            <el-empty description="请选择一个收藏事件查看详情" />
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/api'

const loading = ref(false)
const refreshAllLoading = ref(false)
const refreshLoading = ref(false)
const favorites = ref([])
const selectedFavorite = ref(null)

// 获取收藏列表
const fetchFavorites = async () => {
  loading.value = true
  try {
    const response = await api.get('/favorites')
    favorites.value = response.data.data
    if (favorites.value.length > 0 && !selectedFavorite.value) {
      selectedFavorite.value = favorites.value[0]
    }
  } catch (error) {
    ElMessage.error('获取收藏列表失败')
  } finally {
    loading.value = false
  }
}

// 选择收藏事件
const selectFavorite = (favorite) => {
  selectedFavorite.value = favorite
}

// 删除收藏
const deleteFavorite = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个收藏吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await api.delete(`/favorites/${id}`)
    ElMessage.success('删除成功')
    
    // 重新获取列表
    await fetchFavorites()
    
    // 如果删除的是当前选中的，清空选中状态
    if (selectedFavorite.value?.id === id) {
      selectedFavorite.value = null
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 刷新单个收藏
const refreshFavorite = async () => {
  if (!selectedFavorite.value) return

  refreshLoading.value = true
  try {
    const response = await api.post(`/favorites/${selectedFavorite.value.id}/refresh`)
    
    // 检查是否有新进展
    if (response.data.message === '没有新的进展') {
      ElMessage.info('没有新的进展')
    } else {
      selectedFavorite.value = response.data.data
      
      // 更新列表中的对应项
      const index = favorites.value.findIndex(f => f.id === selectedFavorite.value.id)
      if (index !== -1) {
        favorites.value[index] = selectedFavorite.value
      }
      
      ElMessage.success('刷新成功，已更新事件进展')
    }
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    refreshLoading.value = false
  }
}

// 刷新所有收藏
const refreshAll = async () => {
  refreshAllLoading.value = true
  try {
    // 这里可以调用批量刷新接口，或者逐个刷新
    for (const favorite of favorites.value) {
      try {
        const response = await api.post(`/favorites/${favorite.id}/refresh`)
        const index = favorites.value.findIndex(f => f.id === favorite.id)
        if (index !== -1) {
          favorites.value[index] = response.data.data
        }
      } catch (error) {
        console.error(`刷新收藏 ${favorite.event_name} 失败:`, error)
      }
    }
    
    // 更新当前选中的收藏
    if (selectedFavorite.value) {
      const updated = favorites.value.find(f => f.id === selectedFavorite.value.id)
      if (updated) {
        selectedFavorite.value = updated
      }
    }
    
    ElMessage.success('全部刷新完成')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    refreshAllLoading.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchFavorites()
})
</script>

<style scoped>
.favorites {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h2 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.page-header p {
  color: #7f8c8d;
  font-size: 16px;
}

.loading-container {
  padding: 40px;
}

.empty-container {
  padding: 60px 0;
}

.favorites-container {
  margin-bottom: 30px;
}

.favorites-list {
  height: 600px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.favorites-items {
  max-height: 500px;
  overflow-y: auto;
}

.favorite-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.favorite-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.favorite-item.active {
  border-color: #409EFF;
  background-color: #f0f9ff;
}

.item-content {
  flex: 1;
}

.item-content h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 14px;
}

.item-time, .item-refresh {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.item-actions {
  margin-left: 10px;
}

.favorite-detail {
  height: 600px;
  overflow-y: auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-header h3 {
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

.no-selection {
  height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .el-col {
    margin-bottom: 20px;
  }
  
  .detail-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .favorites-list, .favorite-detail {
    height: auto;
  }
}
</style>