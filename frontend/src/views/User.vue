<template>
  <div class="user-page">
    <div class="page-header">
      <h2>用户中心</h2>
      <p>管理您的账户信息</p>
    </div>

    <div class="user-container">
      <!-- 未登录状态 -->
      <div v-if="!userStore.isLoggedIn" class="login-section">
        <el-card class="login-card">
          <template #header>
            <div class="card-header">
              <h3>登录 / 注册</h3>
            </div>
          </template>

          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            label-width="80px"
            class="login-form"
          >
            <el-form-item label="手机号" prop="phone">
              <el-input
                v-model="loginForm.phone"
                placeholder="请输入手机号"
                clearable
              >
                <template #prepend>+86</template>
              </el-input>
            </el-form-item>

            <el-form-item label="验证码" prop="code">
              <div class="code-input">
                <el-input
                  v-model="loginForm.code"
                  placeholder="请输入验证码"
                  clearable
                />
                <el-button
                  type="primary"
                  :disabled="!canSendCode || countdown > 0"
                  @click="sendCode"
                  :loading="sendingCode"
                >
                  {{ countdown > 0 ? `${countdown}s` : '发送验证码' }}
                </el-button>
              </div>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                @click="handleLogin"
                :loading="loginLoading"
                style="width: 100%"
              >
                登录
              </el-button>
            </el-form-item>

            <el-form-item>
              <el-button
                type="success"
                size="large"
                @click="handleRegister"
                :loading="registerLoading"
                style="width: 100%"
              >
                注册
              </el-button>
            </el-form-item>
          </el-form>

          <div class="login-tips">
            <el-alert
              title="提示"
              type="info"
              :closable="false"
              show-icon
            >
              <p>• 首次使用请先注册</p>
              <p>• 验证码有效期为5分钟</p>
              <p>• 同一手机号1分钟内只能发送一次验证码</p>
            </el-alert>
          </div>
        </el-card>
      </div>

      <!-- 已登录状态 -->
      <div v-else class="profile-section">
        <el-card class="profile-card">
          <template #header>
            <div class="card-header">
              <h3>用户信息</h3>
              <el-button type="danger" @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-button>
            </div>
          </template>

          <div class="profile-info">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="用户ID">
                {{ userStore.user.id }}
              </el-descriptions-item>
              <el-descriptions-item label="手机号">
                {{ userStore.user.phone }}
              </el-descriptions-item>
              <el-descriptions-item label="注册时间">
                {{ formatDate(userStore.user.created_at) }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="profile-actions">
            <el-button type="primary" @click="$router.push('/favorites')">
              <el-icon><Star /></el-icon>
              查看收藏
            </el-button>
            <el-button type="success" @click="$router.push('/')">
              <el-icon><Search /></el-icon>
              搜索事件
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

const loginFormRef = ref()
const loginForm = ref({
  phone: '',
  code: ''
})

const loginRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '验证码为6位数字', trigger: 'blur' }
  ]
}

const loginLoading = ref(false)
const registerLoading = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)

const canSendCode = computed(() => {
  return loginForm.value.phone && /^1[3-9]\d{9}$/.test(loginForm.value.phone)
})

// 发送验证码
const sendCode = async () => {
  if (!canSendCode.value) {
    ElMessage.warning('请输入正确的手机号')
    return
  }

  sendingCode.value = true
  try {
    const success = await userStore.sendCode(loginForm.value.phone)
    if (success) {
      startCountdown()
    }
  } finally {
    sendingCode.value = false
  }
}

// 开始倒计时
const startCountdown = () => {
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

// 登录
const handleLogin = async () => {
  try {
    await loginFormRef.value.validate()
    
    loginLoading.value = true
    const success = await userStore.login(loginForm.value.phone, loginForm.value.code)
    
    if (success) {
      loginForm.value = { phone: '', code: '' }
    }
  } catch (error) {
    // 表单验证失败
  } finally {
    loginLoading.value = false
  }
}

// 注册
const handleRegister = async () => {
  try {
    await loginFormRef.value.validate()
    
    registerLoading.value = true
    const success = await userStore.register(loginForm.value.phone, loginForm.value.code)
    
    if (success) {
      loginForm.value = { phone: '', code: '' }
    }
  } catch (error) {
    // 表单验证失败
  } finally {
    registerLoading.value = false
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    await userStore.logout()
  } catch (error) {
    // 处理错误
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  // 页面加载时的初始化
})
</script>

<style scoped>
.user-page {
  max-width: 800px;
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

.user-container {
  margin-bottom: 30px;
}

.login-card, .profile-card {
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

.login-form {
  margin-bottom: 20px;
}

.code-input {
  display: flex;
  gap: 10px;
}

.code-input .el-input {
  flex: 1;
}

.code-input .el-button {
  width: 120px;
}

.login-tips {
  margin-top: 20px;
}

.login-tips p {
  margin: 5px 0;
  font-size: 14px;
}

.profile-info {
  margin-bottom: 30px;
}

.profile-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-page {
    padding: 0 20px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .code-input {
    flex-direction: column;
  }
  
  .code-input .el-button {
    width: 100%;
  }
  
  .profile-actions {
    flex-direction: column;
  }
}
</style> 