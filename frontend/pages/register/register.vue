<template>
  <view class="auth-container">
    <view class="auth-header">
      <view class="logo-circle">AI</view>
      <text class="app-name">创建账号</text>
      <text class="app-desc">注册后即可开始使用</text>
    </view>

    <view class="auth-card">
      <view class="form-wrapper">
        <view class="input-group">
          <text class="icon">👤</text>
          <input class="styled-input" type="text" v-model="username" placeholder="设置用户名" />
        </view>
        <view class="input-group">
          <text class="icon">🔒</text>
          <input class="styled-input" type="password" v-model="password" placeholder="设置密码（至少6位）" />
        </view>
        <view class="input-group">
          <text class="icon">🔒</text>
          <input class="styled-input" type="password" v-model="confirmPassword" placeholder="再次确认密码" />
        </view>
        <view class="input-group">
          <text class="icon">🎁</text>
          <input class="styled-input" type="text" v-model="inviteCode" placeholder="邀请码（选填）" maxlength="6" />
        </view>
        <view class="submit-btn" @click="handleRegister" :class="{ 'loading': isLoading }">
          {{ isLoading ? '注册中...' : '立即注册' }}
        </view>
      </view>
    </view>
    <view class="footer-tips">
      已有账号？<text class="link" @click="goLogin">返回登录</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { API_BASE } from '../../config.js';

const username = ref('');
const password = ref('');
const confirmPassword = ref('');
const inviteCode = ref('');
const isLoading = ref(false);

const handleRegister = async () => {
  if (!username.value.trim() || username.value.trim().length < 2) {
    uni.showToast({ title: '用户名至少2个字符', icon: 'none' }); return;
  }
  if (password.value.length < 6) {
    uni.showToast({ title: '密码至少6位', icon: 'none' }); return;
  }
  if (password.value !== confirmPassword.value) {
    uni.showToast({ title: '两次密码不一致', icon: 'none' }); return;
  }
  isLoading.value = true;
  try {
    const res = await uni.request({
      url: `${API_BASE}/register`,
      method: 'POST',
      data: { username: username.value.trim(), password: password.value, invite_code: inviteCode.value.trim() }
    });
    if (res.data.code === 200) {
      uni.showToast({ title: '注册成功！', icon: 'success' });
      setTimeout(() => { uni.navigateBack(); }, 1500);
    } else {
      uni.showToast({ title: res.data.msg || '注册失败', icon: 'none' });
    }
  } catch (e) {
    uni.showToast({ title: '网络连接失败', icon: 'none' });
  } finally {
    isLoading.value = false;
  }
};

const goLogin = () => { uni.navigateBack(); };
</script>

<style scoped>
.auth-container { min-height: 100vh; background-color: var(--bg-page); display: flex; flex-direction: column; align-items: center; }
.auth-header { margin-top: 8vh; display: flex; flex-direction: column; align-items: center; margin-bottom: 30px; }
.logo-circle { width: 64px; height: 64px; background: linear-gradient(135deg, var(--primary-color, #3370ff), #5c8dff); border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 20px; color: white; font-weight: bold; box-shadow: 0 8px 24px rgba(51, 112, 255, 0.3); margin-bottom: 14px; }
.app-name { font-size: 22px; font-weight: 700; color: var(--text-primary); }
.app-desc { font-size: 13px; color: var(--text-secondary); margin-top: 6px; }
.auth-card { width: 85%; max-width: 400px; background-color: var(--bg-card); border-radius: 24px; padding: 28px 24px; box-shadow: var(--shadow-card); }
.form-wrapper { display: flex; flex-direction: column; gap: 14px; }
.input-group { display: flex; align-items: center; background-color: var(--bg-input); border-radius: 16px; padding: 4px 16px; border: 1px solid transparent; transition: border-color 0.2s; }
.input-group:focus-within { border-color: var(--primary-color, #3370ff); background-color: var(--bg-card); }
.icon { font-size: 16px; margin-right: 12px; color: var(--text-tertiary); }
.styled-input { flex: 1; height: 46px; font-size: 15px; color: var(--text-primary); }
.submit-btn { margin-top: 8px; height: 50px; border-radius: 25px; background: linear-gradient(90deg, #1f65d6, var(--primary-color, #3370ff)); color: white; font-size: 16px; font-weight: 600; display: flex; justify-content: center; align-items: center; box-shadow: 0 6px 16px rgba(51, 112, 255, 0.25); }
.submit-btn:active { transform: scale(0.97); }
.submit-btn.loading { opacity: 0.7; pointer-events: none; }
.footer-tips { margin-top: 30px; font-size: 14px; color: var(--text-tertiary); }
.link { color: var(--primary-color, #3370ff); font-weight: 500; }
</style>
