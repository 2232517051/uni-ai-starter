<template>
  <view class="discover-container">
    <view class="banner-section">
      <view class="banner-content">
        <text class="banner-title">探索无限可能</text>
        <text class="banner-subtitle">点击灵感卡片，一键体验 AI 多模态能力</text>
      </view>
      <view class="glow-circle"></view>
    </view>

    <view class="content-section">
      <scroll-view class="tab-bar" scroll-x>
        <view class="tab-item" v-for="(tab, i) in tabs" :key="i" :class="{'tab-active': activeTab === i}" @click="activeTab = i">{{ tab.label }}</view>
      </scroll-view>

      <view class="card-grid">
        <view class="prompt-card" v-for="(card, j) in currentCards" :key="j" @click="usePrompt(card.prompt)">
          <view class="card-icon" :class="card.iconClass">{{ card.icon }}</view>
          <view class="card-text">
            <text class="card-title">{{ card.title }}</text>
            <text class="card-desc">{{ card.desc }}</text>
          </view>
          <text class="card-cost">{{ card.cost }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';

const activeTab = ref(0);

const tabs = [
  { label: '全部', filter: 'all' },
  { label: '创意绘画', filter: 'art' },
  { label: '视频制作', filter: 'video' },
  { label: '编程开发', filter: 'code' },
  { label: '学习助手', filter: 'study' },
  { label: '生活实用', filter: 'life' },
];

const allCards = [
  { icon: '💻', iconClass: 'ic-code', title: '代码助手', desc: 'AI 编程辅助', cost: '-1', cat: 'code',
    prompt: '用 Python 写一个快速排序算法，附详细注释' },
  { icon: '🎨', iconClass: 'ic-art', title: 'AI 绘画', desc: '文字生成图片', cost: '-10', cat: 'art',
    prompt: '画一幅日落时分的海边灯塔，油画风格，暖色调' },
  { icon: '🎬', iconClass: 'ic-video', title: 'AI 视频', desc: '文字生成视频', cost: '-50', cat: 'video',
    prompt: '帮我生成一段视频：樱花飘落的日本街道，春天的氛围' },
  { icon: '📝', iconClass: 'ic-study', title: '作文批改', desc: '逐段点评', cost: '-1', cat: 'study',
    prompt: '请帮我批改以下作文，逐段点评并给出改进建议' },
  { icon: '🌍', iconClass: 'ic-life', title: '旅行规划', desc: '定制行程', cost: '-1', cat: 'life',
    prompt: '帮我规划一个 5 天 4 晚的旅行攻略，包含美食和景点' },
  { icon: '📊', iconClass: 'ic-code', title: 'Excel 公式', desc: '一句话搞定', cost: '-1', cat: 'code',
    prompt: '我需要一个 Excel 公式来查找重复值并统计出现次数' },
  { icon: '🧮', iconClass: 'ic-study', title: '数学解题', desc: '详细推导', cost: '-1', cat: 'study',
    prompt: '请详细解答：求不定积分 ∫x²·e^x dx' },
  { icon: '🔍', iconClass: 'ic-life', title: '热点速递', desc: '联网搜索', cost: '-1', cat: 'life',
    prompt: '搜索今天最重要的 5 条新闻，每条用一句话总结' },
  { icon: '🏠', iconClass: 'ic-art', title: '室内设计', desc: 'AI 效果图', cost: '-10', cat: 'art',
    prompt: '画一张现代简约风格的客厅效果图，大落地窗，自然光照' },
  { icon: '🎵', iconClass: 'ic-video', title: 'MV 短片', desc: 'AI 音乐视频', cost: '-50', cat: 'video',
    prompt: '帮我生成一段视频：日落海边，一个人弹着吉他，电影感' },
];

const currentCards = computed(() => {
  const f = tabs[activeTab.value].filter;
  if (f === 'all') return allCards;
  return allCards.filter(c => c.cat === f);
});

const usePrompt = (text) => {
  uni.setStorageSync('pending_prompt', text);
  uni.switchTab({ url: '/pages/index/index' });
};
</script>

<style scoped>
.discover-container { min-height: 100vh; background-color: var(--bg-page); padding-bottom: 70px; }
.banner-section { position: relative; background: linear-gradient(135deg, var(--primary-color, #3370ff), #5c8dff); height: 160px; display: flex; align-items: center; padding: 0 25px; overflow: hidden; }
.banner-content { position: relative; z-index: 2; }
.banner-title { color: #fff; font-size: 24px; font-weight: bold; display: block; margin-bottom: 8px; }
.banner-subtitle { color: rgba(255,255,255,0.8); font-size: 13px; }
.glow-circle { position: absolute; right: -30px; top: -40px; width: 150px; height: 150px; background: radial-gradient(circle, rgba(255,255,255,0.25) 0%, transparent 70%); border-radius: 50%; }
.content-section { padding: 0 16px; margin-top: -20px; position: relative; z-index: 3; }
.tab-bar { display: flex; white-space: nowrap; padding: 0 0 14px; }
.tab-item { display: inline-block; padding: 8px 18px; font-size: 13px; font-weight: 500; color: var(--text-secondary); background-color: var(--bg-card); border-radius: 20px; margin-right: 10px; box-shadow: var(--shadow-card); }
.tab-active { background: linear-gradient(90deg, var(--primary-color, #3370ff), #5c8dff); color: #fff; }
.card-grid { display: flex; flex-direction: column; gap: 12px; }
.prompt-card { background-color: var(--bg-card); border-radius: 16px; padding: 18px; display: flex; align-items: center; box-shadow: var(--shadow-card); transition: transform 0.2s; }
.prompt-card:active { transform: scale(0.98); }
.card-icon { width: 46px; height: 46px; border-radius: 12px; display: flex; justify-content: center; align-items: center; font-size: 22px; margin-right: 14px; flex-shrink: 0; }
.ic-code { background-color: #f4f0ff; }
.ic-art { background-color: #fff0f6; }
.ic-video { background-color: #e6fffb; }
.ic-study { background-color: #fff7e6; }
.ic-life { background-color: #f0f5ff; }
.card-text { display: flex; flex-direction: column; flex: 1; overflow: hidden; }
.card-title { font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 3px; }
.card-desc { font-size: 12px; color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card-cost { font-size: 12px; font-weight: 700; color: var(--text-tertiary); flex-shrink: 0; margin-left: 8px; }
</style>
