<template>
  <view class="auth-container">
    <view class="auth-header">
      <view class="logo-circle">AI</view>
      <text class="app-name">AI Chat</text>
      <text class="app-desc">Multi-modal AI Assistant</text>
    </view>

    <view class="auth-card">
      <text class="card-title">账号登录</text>
      <view class="form-wrapper">
        <view class="input-group">
          <text class="icon">👤</text>
          <input class="styled-input" type="text" v-model="username" placeholder="请输入账号" />
        </view>
        <view class="input-group">
          <text class="icon">🔒</text>
          <input class="styled-input" type="password" v-model="password" placeholder="请输入密码" @confirm="handleLogin" />
        </view>
        <view class="submit-btn" @click="handleLogin" :class="{ 'loading': isLoading }">
          {{ isLoading ? '请稍候...' : '立即登录' }}
        </view>
      </view>
      <view class="register-link">
        还没有账号？<text class="link" @click="goRegister">立即注册</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { API_BASE } from '../../config.js';

const username = ref('');
const password = ref('');
const isLoading = ref(false);

const handleLogin = async () => {
  if (!username.value || !password.value) {
    uni.showToast({ title: '账号和密码不能为空', icon: 'none' });
    return;
  }
  isLoading.value = true;
  try {
    const res = await uni.request({
      url: `${API_BASE}/login`,
      method: 'POST',
      data: { username: username.value, password: password.value }
    });
    if (res.data.code === 200) {
      uni.setStorageSync('user_id', res.data.user_id);
      uni.setStorageSync('username', username.value);
      uni.showToast({ title: '登录成功', icon: 'none' });
      setTimeout(() => { uni.switchTab({ url: '/pages/index/index' }); }, 800);
    } else {
      uni.showToast({ title: res.data.msg || '登录失败', icon: 'none' });
    }
  } catch (e) {
    uni.showToast({ title: '网络连接失败', icon: 'none' });
  } finally {
    isLoading.value = false;
  }
};

const goRegister = () => { uni.navigateTo({ url: '/pages/register/register' }); };
</script>

<style scoped>
.auth-container { min-height: 100vh; background-color: var(--bg-page); display: flex; flex-direction: column; align-items: center; }
.auth-header { margin-top: 12vh; display: flex; flex-direction: column; align-items: center; margin-bottom: 40px; }
.logo-circle { width: 72px; height: 72px; background: linear-gradient(135deg, var(--primary-color, #3370ff), #5c8dff); border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 24px; color: white; font-weight: bold; box-shadow: 0 8px 24px rgba(51, 112, 255, 0.3); margin-bottom: 16px; }
.app-name { font-size: 24px; font-weight: 700; color: var(--text-primary); }
.app-desc { font-size: 13px; color: var(--text-secondary); margin-top: 6px; }
.auth-card { width: 85%; max-width: 400px; background-color: var(--bg-card); border-radius: 24px; padding: 30px 24px; box-shadow: var(--shadow-card); }
.card-title { font-size: 20px; font-weight: 600; color: var(--text-primary); display: block; margin-bottom: 24px; }
.form-wrapper { display: flex; flex-direction: column; gap: 16px; }
.input-group { display: flex; align-items: center; background-color: var(--bg-input); border-radius: 16px; padding: 4px 16px; border: 1px solid transparent; transition: border-color 0.2s; }
.input-group:focus-within { border-color: var(--primary-color, #3370ff); background-color: var(--bg-card); }
.icon { font-size: 18px; margin-right: 12px; color: var(--text-tertiary); }
.styled-input { flex: 1; height: 48px; font-size: 15px; color: var(--text-primary); }
.submit-btn { margin-top: 10px; height: 50px; border-radius: 25px; background: linear-gradient(90deg, #1f65d6, var(--primary-color, #3370ff)); color: white; font-size: 16px; font-weight: 600; display: flex; justify-content: center; align-items: center; box-shadow: 0 6px 16px rgba(51, 112, 255, 0.25); transition: all 0.2s; }
.submit-btn:active { transform: scale(0.97); }
.submit-btn.loading { opacity: 0.7; pointer-events: none; }
.register-link { margin-top: 20px; text-align: center; font-size: 14px; color: var(--text-secondary); }
.link { color: var(--primary-color, #3370ff); font-weight: 500; }
</style>
