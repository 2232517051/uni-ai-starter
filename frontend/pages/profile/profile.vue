<template>
  <view class="profile-container">
    <!-- Header -->
    <view class="header-section">
      <view class="user-info">
        <view class="avatar">{{ displayName.charAt(0) }}</view>
        <view class="info-text">
          <text class="username">{{ displayName }}</text>
          <text class="tag">AI Explorer</text>
        </view>
      </view>
    </view>

    <!-- Balance Card -->
    <view class="assets-card">
      <view class="asset-item">
        <text class="asset-num" :class="{'low-balance': balance < 20}">{{ balance }}</text>
        <text class="asset-name">算力余额</text>
      </view>
      <view class="divider"></view>
      <view class="asset-item" @click="handleSign">
        <view class="sign-btn" :class="{'disabled-btn': hasSignedToday}">
          {{ hasSignedToday ? '今日已签' : '签到领取' }}
        </view>
        <text class="asset-name">每日福利</text>
      </view>
    </view>

    <!-- Balance History -->
    <view class="section-card">
      <view class="section-header" @click="showBalanceLogs = !showBalanceLogs">
        <text class="section-title">⚡ 算力明细</text>
        <text class="section-arrow">{{ showBalanceLogs ? '▲' : '▼' }}</text>
      </view>
      <view v-if="showBalanceLogs">
        <view v-if="balanceLogs.length === 0" class="empty-text">暂无记录</view>
        <view class="log-item" v-for="(log, i) in balanceLogs" :key="i">
          <text class="log-reason">{{ log.reason }}</text>
          <text class="log-amount" :class="log.amount > 0 ? 'amount-plus' : 'amount-minus'">
            {{ log.amount > 0 ? '+' : '' }}{{ log.amount }}
          </text>
          <text class="log-time">{{ log.created_at }}</text>
        </view>
      </view>
    </view>

    <!-- Settings -->
    <view class="section-card">
      <text class="section-title">设置</text>
      <view class="setting-item" @click="toggleDarkMode">
        <text>🌙 深色模式</text>
        <text class="setting-val">{{ isDark ? '开' : '关' }}</text>
      </view>
      <view class="setting-item" @click="handleLogout">
        <text>🚪 退出登录</text>
      </view>
    </view>

    <!-- Footer -->
    <view class="footer">
      <text class="footer-text">uni-ai-starter v1.0</text>
      <text class="footer-text">Powered by DeepSeek & Qwen</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { API_BASE } from '../../config.js';

const userId = ref(null);
const username = ref('');
const nickname = ref('');
const balance = ref(0);
const hasSignedToday = ref(false);
const isDark = ref(!!uni.getStorageSync('dark_mode'));
const showBalanceLogs = ref(false);
const balanceLogs = ref([]);

const displayName = computed(() => nickname.value || username.value || 'User');

const fetchUserInfo = async () => {
  if (!userId.value) return;
  try {
    const res = await uni.request({ url: `${API_BASE}/user/info/${userId.value}` });
    if (res.data.code === 200) {
      username.value = res.data.username;
      balance.value = res.data.balance;
      hasSignedToday.value = res.data.has_signed_today;
      nickname.value = res.data.nickname || '';
    }
  } catch (e) {}
};

const handleSign = async () => {
  if (hasSignedToday.value) {
    uni.showToast({ title: '今天已签到', icon: 'none' }); return;
  }
  try {
    const res = await uni.request({ url: `${API_BASE}/user/sign/${userId.value}`, method: 'POST' });
    if (res.data.code === 200) {
      uni.showToast({ title: res.data.msg, icon: 'none' });
      hasSignedToday.value = true;
      fetchUserInfo();
    } else {
      uni.showToast({ title: res.data.msg, icon: 'none' });
    }
  } catch (e) {
    uni.showToast({ title: '签到失败', icon: 'none' });
  }
};

const fetchBalanceLogs = async () => {
  try {
    const res = await uni.request({ url: `${API_BASE}/user/balance_logs/${userId.value}` });
    if (res.data.code === 200) balanceLogs.value = res.data.data;
  } catch (e) {}
};

const toggleDarkMode = () => {
  isDark.value = !isDark.value;
  if (isDark.value) {
    document.documentElement.classList.add('dark');
    uni.setStorageSync('dark_mode', true);
  } else {
    document.documentElement.classList.remove('dark');
    uni.removeStorageSync('dark_mode');
  }
};

const handleLogout = () => {
  uni.showModal({
    title: '退出登录', content: '确认退出？',
    success: (res) => {
      if (!res.confirm) return;
      uni.removeStorageSync('user_id');
      uni.removeStorageSync('username');
      uni.redirectTo({ url: '/pages/login/login' });
    }
  });
};

onShow(() => {
  userId.value = uni.getStorageSync('user_id');
  if (!userId.value) { uni.redirectTo({ url: '/pages/login/login' }); return; }
  fetchUserInfo();
  fetchBalanceLogs();
});
</script>

<style scoped>
.profile-container { min-height: 100vh; background-color: var(--bg-page); padding-bottom: 80px; }
.header-section { background: linear-gradient(135deg, var(--primary-color, #3370ff), #5c8dff); padding: 40px 20px 30px; }
.user-info { display: flex; align-items: center; gap: 16px; }
.avatar { width: 60px; height: 60px; border-radius: 50%; background: rgba(255,255,255,0.2); color: white; font-size: 24px; font-weight: bold; display: flex; justify-content: center; align-items: center; }
.info-text { display: flex; flex-direction: column; }
.username { font-size: 20px; font-weight: 700; color: white; }
.tag { font-size: 12px; color: rgba(255,255,255,0.8); margin-top: 4px; }

.assets-card { margin: -20px 16px 16px; background-color: var(--bg-card); border-radius: 20px; padding: 20px; display: flex; align-items: center; box-shadow: var(--shadow-card); position: relative; z-index: 2; }
.asset-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; }
.asset-num { font-size: 28px; font-weight: 700; color: var(--text-primary); }
.low-balance { color: #e74c3c; }
.asset-name { font-size: 12px; color: var(--text-secondary); }
.divider { width: 1px; height: 40px; background-color: var(--border-color); }
.sign-btn { padding: 8px 20px; border-radius: 20px; background: linear-gradient(90deg, #1f65d6, var(--primary-color, #3370ff)); color: white; font-size: 14px; font-weight: 600; }
.disabled-btn { background: var(--bg-input); color: var(--text-tertiary); }

.section-card { margin: 16px; background-color: var(--bg-card); border-radius: 16px; padding: 16px; box-shadow: var(--shadow-card); }
.section-header { display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
.section-title { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 12px; }
.section-arrow { color: var(--text-tertiary); }
.empty-text { text-align: center; color: var(--text-tertiary); font-size: 13px; padding: 16px; }
.log-item { display: flex; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--border-color); }
.log-reason { flex: 1; font-size: 14px; color: var(--text-primary); }
.log-amount { font-size: 14px; font-weight: 600; margin: 0 12px; }
.amount-plus { color: #27c93f; }
.amount-minus { color: #e74c3c; }
.log-time { font-size: 11px; color: var(--text-tertiary); }

.setting-item { display: flex; justify-content: space-between; align-items: center; padding: 14px 0; border-bottom: 1px solid var(--border-color); font-size: 15px; color: var(--text-primary); cursor: pointer; }
.setting-val { color: var(--text-secondary); font-size: 14px; }

.footer { text-align: center; padding: 24px; }
.footer-text { display: block; font-size: 12px; color: var(--text-tertiary); margin: 2px 0; }
</style>
