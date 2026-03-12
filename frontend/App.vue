<script>
export default {
  onLaunch: function () {
    const dark = uni.getStorageSync('dark_mode');
    if (dark) {
      document.documentElement.classList.add('dark');
    }
  },
  onShow: function () {},
  onHide: function () {}
}
</script>

<style>
:root {
  --bg-page: #f0f2f5;
  --bg-chat: #f5f7fa;
  --bg-card: #ffffff;
  --bg-input: #f4f5f7;
  --bg-bubble-ai: #ffffff;
  --bg-bubble-user: linear-gradient(135deg, #1f65d6, #3370ff);
  --bg-sidebar: #ffffff;
  --bg-header: rgba(255,255,255,0.95);
  --text-primary: #1a1d24;
  --text-secondary: #6b7280;
  --text-tertiary: #9ca3af;
  --text-inverse: #ffffff;
  --border-color: #eef0f3;
  --border-light: #e5e7eb;
  --shadow-card: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
  --shadow-msg: 0 1px 4px rgba(0,0,0,0.06);
  --code-bg: #1e1e1e;
  --primary-color: #3370ff;
}

.dark {
  --bg-page: #0b0f14;
  --bg-chat: #0d1117;
  --bg-card: #151b23;
  --bg-input: #1a2232;
  --bg-bubble-ai: #151b23;
  --bg-bubble-user: linear-gradient(135deg, #1a4fad, #2563eb);
  --bg-sidebar: #151b23;
  --bg-header: rgba(21,27,35,0.95);
  --text-primary: #e5e7eb;
  --text-secondary: #9ca3af;
  --text-tertiary: #6b7280;
  --text-inverse: #ffffff;
  --border-color: #1e2733;
  --border-light: #2d3748;
  --shadow-card: 0 1px 3px rgba(0,0,0,0.3), 0 4px 12px rgba(0,0,0,0.2);
  --shadow-msg: 0 2px 6px rgba(0,0,0,0.3);
  --code-bg: #0b0f14;
}

page { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; -webkit-font-smoothing: antialiased; }
* { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background-color: rgba(0,0,0,0.15); border-radius: 4px; }
.dark ::-webkit-scrollbar-thumb { background-color: rgba(255,255,255,0.1); }
::selection { background-color: rgba(51,112,255,0.2); color: inherit; }
html { scroll-behavior: smooth; }
input:focus, textarea:focus { outline: none; }
img { -webkit-user-drag: none; user-select: none; }
.dark img { filter: brightness(0.95); }
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
</style>
