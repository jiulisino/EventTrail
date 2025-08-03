import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const isLoggedIn = computed(() => !!user.value)

  // 检查登录状态
  const checkAuth = async () => {
    try {
      const response = await api.get('/auth/profile')
      if (response.data.user) {
        user.value = response.data.user
      }
    } catch (error) {
      // 用户未登录，清除状态
      user.value = null
    }
  }

  // 发送验证码
  const sendCode = async (phone) => {
    try {
      await api.post('/auth/send-code', { phone })
      ElMessage.success('验证码发送成功')
      return true
    } catch (error) {
      ElMessage.error(error.response?.data?.error || '发送验证码失败')
      return false
    }
  }

  // 用户注册
  const register = async (phone, code) => {
    try {
      const response = await api.post('/auth/register', { phone, code })
      user.value = response.data.user
      ElMessage.success('注册成功')
      return true
    } catch (error) {
      ElMessage.error(error.response?.data?.error || '注册失败')
      return false
    }
  }

  // 用户登录
  const login = async (phone, code) => {
    try {
      const response = await api.post('/auth/login', { phone, code })
      user.value = response.data.user
      ElMessage.success('登录成功')
      return true
    } catch (error) {
      ElMessage.error(error.response?.data?.error || '登录失败')
      return false
    }
  }

  // 用户登出
  const logout = async () => {
    try {
      await api.post('/auth/logout')
      user.value = null
      ElMessage.success('登出成功')
      return true
    } catch (error) {
      ElMessage.error('登出失败')
      return false
    }
  }

  return {
    user,
    isLoggedIn,
    checkAuth,
    sendCode,
    register,
    login,
    logout
  }
}) 