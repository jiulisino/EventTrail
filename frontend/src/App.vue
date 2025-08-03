<template>
  <div id="app">
    <el-container class="app-container">
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo">
            <el-icon class="logo-icon"><Search /></el-icon>
            <h1>来龙去脉事件追踪器</h1>
          </div>
          <div class="nav-menu">
            <el-menu
              :default-active="$route.path"
              mode="horizontal"
              router
              background-color="transparent"
              text-color="#fff"
              active-text-color="#409EFF"
            >
              <el-menu-item index="/">
                <el-icon><House /></el-icon>
                <span>首页</span>
              </el-menu-item>
              <el-menu-item index="/favorites" v-if="userStore.isLoggedIn">
                <el-icon><Star /></el-icon>
                <span>收藏</span>
              </el-menu-item>
              <el-menu-item index="/user">
                <el-icon><User /></el-icon>
                <span>用户</span>
              </el-menu-item>
            </el-menu>
          </div>
        </div>
      </el-header>
      
      <el-main class="app-main">
        <router-view />
      </el-main>
      
      <el-footer class="app-footer">
        <p>&copy; 2024 来龙去脉事件追踪器. All rights reserved.</p>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from './stores/user'

const userStore = useUserStore()

onMounted(() => {
  // 检查用户登录状态
  userStore.checkAuth()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
}

.app-container {
  min-height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 24px;
}

.logo h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.nav-menu {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-menu .el-menu {
  border: none;
}

.nav-menu .el-menu-item {
  color: white !important;
  font-size: 16px;
}

.nav-menu .el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.nav-menu .el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.2) !important;
  color: #409EFF !important;
}

.app-main {
  flex: 1;
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.app-footer {
  background-color: #2c3e50;
  color: white;
  text-align: center;
  padding: 20px;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 10px;
    padding: 10px 20px;
  }
  
  .logo h1 {
    font-size: 20px;
  }
  
  .nav-menu {
    width: 100%;
  }
  
  .app-main {
    padding: 10px;
  }
}
</style> 