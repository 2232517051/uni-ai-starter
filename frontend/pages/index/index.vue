<template>
  <view class="page-wrapper">
    <!-- Sidebar Mask -->
    <view class="sidebar-mask" v-if="showSidebar" @click="showSidebar = false"></view>

    <!-- Sidebar -->
    <view class="sidebar" :class="{ 'sidebar-open': showSidebar }">
      <view class="sidebar-header">
        <text class="sidebar-title">历史会话</text>
        <view class="sidebar-new-btn" @click="createConversation">+ 新对话</view>
      </view>
      <view class="sidebar-search">
        <input class="sidebar-search-input" type="text" v-model="searchKeyword" placeholder="搜索会话..." />
      </view>
      <scroll-view class="sidebar-list" scroll-y>
        <view class="conv-item" v-for="conv in filteredConversations" :key="conv.id"
          :class="{ 'conv-active': conv.id === currentConvId }" @click="switchConversation(conv.id)">
          <text class="conv-pin-icon" v-if="conv.pinned">📌</text>
          <view class="conv-info">
            <text class="conv-title">{{ conv.title }}</text>
            <text class="conv-date">{{ conv.created_at }}</text>
          </view>
          <view class="conv-actions">
            <view class="conv-pin" @click.stop="togglePin(conv.id)">{{ conv.pinned ? '📌' : '📍' }}</view>
            <view class="conv-del" @click.stop="deleteConversation(conv.id)">x</view>
          </view>
        </view>
        <view v-if="conversations.length === 0" class="conv-empty">
          <text>还没有会话，点击上方新建</text>
        </view>
      </scroll-view>
    </view>

    <!-- Main Chat Area -->
    <view class="chat-container">
      <!-- Header -->
      <view class="header">
        <view class="menu-btn" @click="showSidebar = !showSidebar">
          <view class="menu-line"></view><view class="menu-line"></view><view class="menu-line"></view>
        </view>
        <view class="header-center" @click="showModelPicker = !showModelPicker">
          <view class="header-texts">
            <text class="title">AI Chat</text>
            <text class="subtitle">{{ currentModelLabel }}</text>
          </view>
        </view>
        <view class="header-balance" @click="goProfile">
          <text class="balance-icon">⚡</text>
          <text class="balance-num">{{ headerBalance }}</text>
        </view>
      </view>

      <!-- Model Picker -->
      <view class="model-picker" v-if="showModelPicker">
        <view class="model-option" v-for="m in modelOptions" :key="m.id"
          :class="{'model-active': currentModel === m.id}" @click="switchModel(m.id)">
          <text class="model-option-icon">{{ m.icon }}</text>
          <view class="model-option-info">
            <text class="model-option-name">{{ m.name }}</text>
            <text class="model-option-desc">{{ m.desc }}</text>
          </view>
          <text class="model-check" v-if="currentModel === m.id">✓</text>
        </view>
      </view>

      <!-- Messages -->
      <scroll-view class="chat-box" scroll-y :scroll-top="scrollTop" scroll-with-animation @click="closeMenu">
        <view class="message" v-for="(msg, index) in messages" :key="index"
          :class="msg.role === 'user' ? 'msg-user' : 'msg-ai'" v-show="msg.role !== 'system'">
          <view v-if="msg.role === 'ai'" class="avatar avatar-ai">AI</view>
          <view v-else class="avatar avatar-user">我</view>
          <view class="msg-body">
            <view class="content" @longpress="onLongPress(index, msg)">
              <image v-if="msg.image && msg.role === 'user'" :src="msg.image" class="chat-img" mode="widthFix" />
              <img v-if="msg.aiImage" :src="msg.aiImage" referrerpolicy="no-referrer" class="chat-img" />
              <video v-if="msg.video" :src="msg.video" controls class="chat-video"></video>
              <view v-if="msg.role === 'ai' && !msg.content && isLoading" class="typing-indicator">
                <view class="dot"></view><view class="dot"></view><view class="dot"></view>
              </view>
              <rich-text v-if="msg.content" :nodes="renderMarkdown(msg.content)"></rich-text>
              <text v-if="msg.role === 'ai' && isLoading && index === messages.length - 1 && msg.content" class="typing-cursor">▍</text>
            </view>
            <!-- Action bar -->
            <view class="msg-action-bar" v-if="msg.role === 'ai' && msg.content && !isLoading">
              <view class="msg-action-item" @click.stop="copyText(msg.content)"><text>📋</text></view>
            </view>
            <!-- Long press menu -->
            <view class="longpress-menu" v-if="menuIndex === index" @click.stop>
              <view class="menu-opt" @click="copyText(msg.content); closeMenu();"><text>📋 复制</text></view>
              <view class="menu-opt menu-danger" @click="deleteMsg(index)"><text>🗑️ 删除</text></view>
            </view>
          </view>
        </view>
        <view style="height: 10px;"></view>
      </scroll-view>

      <!-- Scroll to bottom -->
      <view class="scroll-bottom-btn" v-if="showScrollBtn" @click="scrollToBottom"><text>↓</text></view>

      <!-- Quick tools -->
      <view class="tools-toggle" @click="showTools = !showTools" v-if="!isLoading">
        <text>{{ showTools ? '▼ 收起工具' : '▲ 展开工具' }}</text>
      </view>
      <view class="interactive-zone" v-if="!isLoading && showTools">
        <scroll-view class="tools-scroll" scroll-x>
          <view class="tools-scroll-inner">
            <view class="tool-chip" @click="sendQuick('帮我总结一下重点')">⚡ 总结</view>
            <view class="tool-chip" @click="chooseImage">🔍 拍题</view>
            <view class="tool-chip tool-chip-warn" @click="sendQuick('帮我生成一段视频：赛博朋克城市夜景')">🎥 视频</view>
            <view class="tool-chip" @click="sendQuick('画一张日落海边风景画')">🎨 画图</view>
          </view>
        </scroll-view>
      </view>

      <!-- Image preview -->
      <view class="image-preview-zone" v-if="selectedImagePreview">
        <view class="preview-box">
          <image :src="selectedImagePreview" mode="aspectFill" class="preview-img" />
          <view class="remove-img-btn" @click="removeImage">×</view>
        </view>
      </view>

      <!-- Input area -->
      <view class="input-area">
        <view class="input-capsule">
          <button class="action-btn" @click="chooseImage">🖼️</button>
          <input class="real-input" type="text" v-model="inputText" placeholder="输入消息..." @confirm="sendMessage" />
          <view class="send-btn" @click="sendMessage" :class="{'disabled': isLoading}">
            <text class="send-icon">➤</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, nextTick, computed } from 'vue';
import { onLoad, onShow } from '@dcloudio/uni-app';
import { marked } from 'marked';
import { API_BASE } from '../../config.js';

const inputText = ref('');
const isLoading = ref(false);
const scrollTop = ref(0);
const userId = ref(null);
const selectedImagePreview = ref('');
const selectedImageBase64 = ref(null);
const showSidebar = ref(false);
const conversations = ref([]);
const currentConvId = ref(0);
const searchKeyword = ref('');
const showTools = ref(true);
const showScrollBtn = ref(false);
const menuIndex = ref(-1);
const headerBalance = ref(0);

// Model switching
const showModelPicker = ref(false);
const currentModel = ref('deepseek');
const modelOptions = [
  { id: 'deepseek', icon: '🧠', name: 'DeepSeek', desc: '强推理、写代码' },
  { id: 'qwen', icon: '🌟', name: 'Qwen-Max', desc: '通义千问，均衡全能' },
];
const currentModelLabel = computed(() => {
  const m = modelOptions.find(o => o.id === currentModel.value);
  return m ? m.name : '';
});
const switchModel = (id) => {
  currentModel.value = id;
  showModelPicker.value = false;
  uni.showToast({ title: `已切换：${modelOptions.find(o => o.id === id).name}`, icon: 'none' });
};

const filteredConversations = computed(() => {
  const kw = searchKeyword.value.trim().toLowerCase();
  if (!kw) return conversations.value;
  return conversations.value.filter(c => c.title.toLowerCase().includes(kw));
});

// Markdown rendering
const renderer = new marked.Renderer();
renderer.code = function(tokenOrCode, language) {
  let codeText = typeof tokenOrCode === 'object' ? tokenOrCode.text : tokenOrCode;
  let lang = typeof tokenOrCode === 'object' ? (tokenOrCode.lang || 'text') : (language || 'text');
  const safe = (codeText || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const formatted = safe.replace(/\n/g, '<br/>').replace(/ /g, '&nbsp;');
  const raw = (codeText || '').replace(/"/g, '&quot;');
  return `<div style="background:#1e1e1e;border-radius:8px;margin:12px 0;overflow:hidden;">
    <div style="display:flex;justify-content:space-between;align-items:center;background:#2d2d2d;padding:8px 14px;">
      <div style="display:flex;gap:6px;">
        <div style="width:12px;height:12px;border-radius:50%;background:#ff5f56;"></div>
        <div style="width:12px;height:12px;border-radius:50%;background:#ffbd2e;"></div>
        <div style="width:12px;height:12px;border-radius:50%;background:#27c93f;"></div>
      </div>
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="color:#a0a0a0;font-size:12px;">${lang}</span>
        <span class="code-copy-btn" data-code="${raw}" style="color:#8f8f8f;font-size:11px;cursor:pointer;padding:2px 8px;border:1px solid #555;border-radius:4px;">复制</span>
      </div>
    </div>
    <div style="padding:14px;overflow-x:auto;">
      <div style="font-family:'Fira Code',Consolas,monospace;font-size:14px;color:#d4d4d4;line-height:1.5;">${formatted}</div>
    </div>
  </div>`;
};
marked.setOptions({ renderer });

const renderMarkdown = (text) => {
  if (!text) return '';
  let t = text.replace(/\[IMAGE:[^\]]*$/, '').replace(/\[VIDEO:[^\]]*$/, '').replace(/@@@[\s\S]*?(@@@|$)/g, '');
  let html = marked.parse(t);
  html = html.replace(/<table/g, '<table style="border-collapse:collapse;width:100%;margin:12px 0;font-size:14px;"');
  html = html.replace(/<th/g, '<th style="border:1px solid #ebeef5;padding:8px;background:#f4f4f5;text-align:left;"');
  html = html.replace(/<td/g, '<td style="border:1px solid #ebeef5;padding:8px;"');
  html = html.replace(/<blockquote/g, '<blockquote style="border-left:4px solid var(--primary-color,#3370ff);margin:0;padding-left:10px;color:#666;"');
  return html;
};

// System & welcome messages
const systemPrompt = { role: 'system', content: 'You are AI Assistant.' };
const welcomeMsg = { role: 'ai', content: '你好！我是 AI Assistant。支持文字对话、图片识别、AI 绘画和视频生成。有什么可以帮你的？' };
const messages = ref([systemPrompt, { ...welcomeMsg }]);

// Scroll
const scrollToBottom = () => {
  nextTick(() => { scrollTop.value = scrollTop.value === 99999 ? 99998 : 99999; });
};

// Menu
const onLongPress = (index, msg) => {
  if (msg.role === 'system' || !msg.content) return;
  menuIndex.value = index;
};
const closeMenu = () => { menuIndex.value = -1; };
const deleteMsg = (index) => { messages.value.splice(index, 1); closeMenu(); };
const copyText = (text) => {
  if (!text) return;
  uni.setClipboardData({ data: text, success: () => uni.showToast({ title: '已复制', icon: 'success' }) });
};

// Image
const chooseImage = () => {
  uni.chooseImage({
    count: 1, sizeType: ['compressed'],
    success: (res) => {
      selectedImagePreview.value = res.tempFilePaths[0];
      const reader = new FileReader();
      fetch(res.tempFilePaths[0]).then(r => r.blob()).then(blob => {
        reader.onload = () => { selectedImageBase64.value = reader.result; };
        reader.readAsDataURL(blob);
      });
    }
  });
};
const removeImage = () => { selectedImagePreview.value = ''; selectedImageBase64.value = null; };

// Balance
const fetchBalance = async () => {
  if (!userId.value) return;
  try {
    const res = await uni.request({ url: `${API_BASE}/user/balance/${userId.value}` });
    if (res.data.code === 200) headerBalance.value = res.data.balance;
  } catch (e) {}
};
const goProfile = () => { uni.switchTab({ url: '/pages/profile/profile' }); };

// Conversations
const loadConversations = async () => {
  try {
    const res = await uni.request({ url: `${API_BASE}/conversations/${userId.value}` });
    if (res.data.code === 200) conversations.value = res.data.data;
  } catch (e) {}
};

const createConversation = async () => {
  try {
    const res = await uni.request({ url: `${API_BASE}/conversation/create/${userId.value}`, method: 'POST' });
    if (res.data.code === 200) {
      currentConvId.value = res.data.conversation_id;
      messages.value = [systemPrompt, { ...welcomeMsg }];
      await loadConversations();
      showSidebar.value = false;
    }
  } catch (e) {}
};

const switchConversation = async (convId) => {
  currentConvId.value = convId;
  showSidebar.value = false;
  messages.value = [systemPrompt];
  await loadHistory();
};

const togglePin = async (convId) => {
  try {
    await uni.request({ url: `${API_BASE}/conversation/pin/${convId}`, method: 'PUT' });
    await loadConversations();
  } catch (e) {}
};

const deleteConversation = async (convId) => {
  uni.showModal({
    title: '删除会话', content: '确认删除？',
    success: async (res) => {
      if (!res.confirm) return;
      await uni.request({ url: `${API_BASE}/conversation/${convId}`, method: 'DELETE' });
      await loadConversations();
      if (convId === currentConvId.value) {
        conversations.value.length > 0 ? await switchConversation(conversations.value[0].id) : await createConversation();
      }
    }
  });
};

// History
const loadHistory = async () => {
  try {
    const res = await uni.request({ url: `${API_BASE}/history/${userId.value}?conversation_id=${currentConvId.value}` });
    if (res.data.code === 200 && res.data.data.length > 0) {
      const data = res.data.data.map(item => {
        if (item.role === 'assistant') item.role = 'ai';
        if (item.content) {
          const vm = item.content.match(/\[VIDEO:([\s\S]+?)\]/);
          if (vm) { item.video = vm[1].trim(); item.content = item.content.replace(/\[VIDEO:[\s\S]+?\]/g, '').trim(); }
          const im = item.content.match(/\[IMAGE:([\s\S]+?)\]/);
          if (im) { item.aiImage = im[1].trim(); item.content = item.content.replace(/\[IMAGE:[\s\S]+?\]/g, '').trim(); }
          item.content = item.content.replace(/@@@[\s\S]*?(@@@|$)/g, '').trim();
        }
        return item;
      });
      messages.value = [systemPrompt, ...data];
      scrollToBottom();
    } else {
      messages.value = [systemPrompt, { ...welcomeMsg }];
    }
  } catch (e) {}
};

// Send message
const sendQuick = (text) => { inputText.value = text; sendMessage(); };

const sendMessage = async () => {
  const text = inputText.value.trim();
  if ((!text && !selectedImageBase64.value) || isLoading.value) return;

  const userMsg = { role: 'user', content: text, image: selectedImagePreview.value || null };
  messages.value.push(userMsg);
  inputText.value = '';
  const imgBase64 = selectedImageBase64.value;
  removeImage();

  messages.value.push({ role: 'ai', content: '' });
  isLoading.value = true;
  scrollToBottom();

  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId.value,
        message: text,
        image_base64: imgBase64,
        conversation_id: currentConvId.value,
        model: currentModel.value,
      }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    const aiIndex = messages.value.length - 1;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      messages.value[aiIndex].content += chunk;

      // Parse special tags
      const content = messages.value[aiIndex].content;
      const imgMatch = content.match(/\[IMAGE:([\s\S]+?)\]/);
      if (imgMatch) {
        messages.value[aiIndex].aiImage = imgMatch[1].trim();
        messages.value[aiIndex].content = content.replace(/\[IMAGE:[\s\S]+?\]/g, '').trim();
      }
      const vidMatch = content.match(/\[VIDEO:([\s\S]+?)\]/);
      if (vidMatch) {
        messages.value[aiIndex].video = vidMatch[1].trim();
        messages.value[aiIndex].content = content.replace(/\[VIDEO:[\s\S]+?\]/g, '').trim();
      }
      scrollToBottom();
    }

    // Clean suggested questions tags
    const finalContent = messages.value[aiIndex].content;
    messages.value[aiIndex].content = finalContent.replace(/@@@[\s\S]*?(@@@|$)/g, '').trim();
    fetchBalance();
  } catch (e) {
    const aiIndex = messages.value.length - 1;
    messages.value[aiIndex].content = '网络错误，请检查后端服务是否运行。';
  } finally {
    isLoading.value = false;
    scrollToBottom();
  }
};

// Lifecycle
onLoad(() => {
  const storedId = uni.getStorageSync('user_id');
  if (!storedId) { uni.redirectTo({ url: '/pages/login/login' }); return; }
  userId.value = storedId;
  initApp();

  // Code copy button handler
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.code-copy-btn');
    if (btn) {
      const code = btn.getAttribute('data-code');
      if (code) {
        const decoded = code.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&').replace(/&quot;/g, '"');
        navigator.clipboard.writeText(decoded).then(() => {
          btn.innerText = '已复制';
          setTimeout(() => { btn.innerText = '复制'; }, 1500);
        });
      }
    }
  });
});

onShow(() => {
  fetchBalance();
  const pending = uni.getStorageSync('pending_prompt');
  if (pending) {
    uni.removeStorageSync('pending_prompt');
    inputText.value = pending;
    nextTick(() => sendMessage());
  }
});

const initApp = async () => {
  await fetchBalance();
  await loadConversations();
  if (conversations.value.length > 0) {
    currentConvId.value = conversations.value[0].id;
    await loadHistory();
  } else {
    await createConversation();
  }
};
</script>

<style scoped>
/* Layout */
.page-wrapper { width: 100vw; height: 100vh; position: relative; overflow: hidden; }
.sidebar-mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); z-index: 100; }
.sidebar { position: fixed; top: 0; left: -280px; width: 280px; height: 100vh; background-color: var(--bg-sidebar); z-index: 101; transition: left 0.3s; display: flex; flex-direction: column; box-shadow: 2px 0 12px rgba(0,0,0,0.1); }
.sidebar-open { left: 0; }
.sidebar-header { display: flex; justify-content: space-between; align-items: center; padding: 16px; border-bottom: 1px solid var(--border-color); }
.sidebar-title { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.sidebar-new-btn { font-size: 13px; color: var(--primary-color, #3370ff); padding: 6px 12px; border: 1px solid var(--primary-color, #3370ff); border-radius: 16px; }
.sidebar-search { padding: 10px 16px; }
.sidebar-search-input { width: 100%; height: 36px; background-color: var(--bg-input); border-radius: 18px; padding: 0 14px; font-size: 13px; color: var(--text-primary); }
.sidebar-list { flex: 1; }
.conv-item { display: flex; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--border-color); cursor: pointer; }
.conv-item:active, .conv-active { background-color: var(--bg-input); }
.conv-info { flex: 1; overflow: hidden; margin: 0 8px; }
.conv-title { font-size: 14px; color: var(--text-primary); display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.conv-date { font-size: 11px; color: var(--text-tertiary); }
.conv-pin-icon { font-size: 12px; flex-shrink: 0; }
.conv-actions { display: flex; gap: 6px; flex-shrink: 0; }
.conv-pin, .conv-del { font-size: 14px; padding: 2px 6px; cursor: pointer; }
.conv-empty { text-align: center; padding: 30px; color: var(--text-tertiary); font-size: 13px; }

/* Chat container */
.chat-container { display: flex; flex-direction: column; height: 100vh; background-color: var(--bg-chat); }

/* Header */
.header { display: flex; align-items: center; padding: 12px 16px; background-color: var(--bg-header); backdrop-filter: blur(10px); border-bottom: 1px solid var(--border-color); flex-shrink: 0; }
.menu-btn { width: 36px; height: 36px; display: flex; flex-direction: column; justify-content: center; gap: 5px; cursor: pointer; }
.menu-line { width: 20px; height: 2px; background-color: var(--text-primary); border-radius: 2px; }
.header-center { flex: 1; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.header-texts { display: flex; flex-direction: column; align-items: center; }
.title { font-size: 17px; font-weight: 700; color: var(--text-primary); }
.subtitle { font-size: 11px; color: var(--text-tertiary); }
.header-balance { display: flex; align-items: center; gap: 4px; padding: 4px 10px; background-color: var(--bg-input); border-radius: 16px; cursor: pointer; }
.balance-icon { font-size: 14px; }
.balance-num { font-size: 13px; font-weight: 600; color: var(--text-primary); }

/* Model picker */
.model-picker { background-color: var(--bg-card); border-bottom: 1px solid var(--border-color); padding: 8px 16px; }
.model-option { display: flex; align-items: center; padding: 10px; border-radius: 12px; margin-bottom: 4px; cursor: pointer; }
.model-option:active, .model-active { background-color: var(--bg-input); }
.model-option-icon { font-size: 22px; margin-right: 12px; }
.model-option-info { flex: 1; }
.model-option-name { font-size: 14px; font-weight: 600; color: var(--text-primary); display: block; }
.model-option-desc { font-size: 12px; color: var(--text-secondary); }
.model-check { color: var(--primary-color, #3370ff); font-weight: bold; }

/* Chat box */
.chat-box { flex: 1; padding: 16px; }
.message { display: flex; margin-bottom: 16px; align-items: flex-start; }
.msg-user { flex-direction: row-reverse; }
.avatar { width: 36px; height: 36px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 14px; font-weight: bold; flex-shrink: 0; }
.avatar-ai { background: linear-gradient(135deg, var(--primary-color, #3370ff), #5c8dff); color: white; }
.avatar-user { background-color: var(--bg-input); color: var(--text-primary); }
.msg-body { max-width: 78%; margin: 0 10px; }
.content { padding: 12px 16px; border-radius: 18px; font-size: 15px; line-height: 1.6; word-break: break-word; }
.msg-ai .content { background-color: var(--bg-bubble-ai); color: var(--text-primary); box-shadow: var(--shadow-msg); border-top-left-radius: 4px; }
.msg-user .content { background: var(--bg-bubble-user); color: var(--text-inverse); border-top-right-radius: 4px; }
.chat-img { max-width: 100%; border-radius: 12px; margin: 8px 0; }
.chat-video { max-width: 100%; border-radius: 12px; margin: 8px 0; }

/* Typing indicator */
.typing-indicator { display: flex; gap: 4px; padding: 4px 0; }
.dot { width: 8px; height: 8px; border-radius: 50%; background-color: var(--text-tertiary); animation: bounce 1.4s infinite ease-in-out; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
.typing-cursor { color: var(--primary-color, #3370ff); animation: blink 1s step-end infinite; }
@keyframes blink { 50% { opacity: 0; } }

/* Action bar */
.msg-action-bar { display: flex; gap: 6px; margin-top: 4px; }
.msg-action-item { padding: 2px 6px; cursor: pointer; font-size: 14px; opacity: 0.6; }
.msg-action-item:hover { opacity: 1; }

/* Long press menu */
.longpress-menu { position: absolute; background-color: var(--bg-card); border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.15); padding: 4px; z-index: 50; }
.menu-opt { padding: 10px 16px; font-size: 14px; color: var(--text-primary); cursor: pointer; border-radius: 8px; }
.menu-opt:active { background-color: var(--bg-input); }
.menu-danger { color: #e74c3c; }

/* Scroll button */
.scroll-bottom-btn { position: absolute; bottom: 160px; right: 16px; width: 36px; height: 36px; border-radius: 50%; background-color: var(--bg-card); box-shadow: var(--shadow-card); display: flex; justify-content: center; align-items: center; cursor: pointer; z-index: 10; }

/* Tools */
.tools-toggle { text-align: center; padding: 6px; font-size: 12px; color: var(--text-tertiary); cursor: pointer; }
.interactive-zone { padding: 0 16px 8px; flex-shrink: 0; }
.tools-scroll { white-space: nowrap; }
.tools-scroll-inner { display: inline-flex; gap: 10px; }
.tool-chip { display: inline-flex; align-items: center; padding: 8px 16px; background: var(--bg-card); border-radius: 20px; font-size: 13px; color: var(--text-primary); box-shadow: var(--shadow-card); cursor: pointer; }
.tool-chip:active { transform: scale(0.95); }
.tool-chip-warn { border: 1px solid #ff9900; }

/* Image preview */
.image-preview-zone { padding: 8px 16px; flex-shrink: 0; }
.preview-box { position: relative; display: inline-block; }
.preview-img { width: 80px; height: 80px; border-radius: 12px; }
.remove-img-btn { position: absolute; top: -6px; right: -6px; width: 22px; height: 22px; border-radius: 50%; background: #e74c3c; color: white; font-size: 14px; display: flex; justify-content: center; align-items: center; cursor: pointer; }

/* Input area */
.input-area { padding: 8px 12px 12px; background-color: var(--bg-header); border-top: 1px solid var(--border-color); flex-shrink: 0; }
.input-capsule { display: flex; align-items: center; background-color: var(--bg-input); border-radius: 25px; padding: 4px 6px; gap: 4px; }
.action-btn { width: 36px; height: 36px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 18px; background: none; border: none; padding: 0; cursor: pointer; }
.real-input { flex: 1; height: 40px; font-size: 15px; color: var(--text-primary); padding: 0 8px; }
.send-btn { width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, var(--primary-color, #3370ff), #5c8dff); display: flex; justify-content: center; align-items: center; cursor: pointer; flex-shrink: 0; }
.send-btn.disabled { opacity: 0.5; pointer-events: none; }
.send-icon { color: white; font-size: 18px; }
</style>
