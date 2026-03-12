# uni-ai-starter

开箱即用的全栈 AI 对话模板。基于 **uni-app (Vue 3)** + **FastAPI (Python)**。

Full-stack AI Chat template. Built with **uni-app (Vue 3)** + **FastAPI (Python)**.

[中文](#chinese) | [English](#english)

---

<a id="chinese"></a>

# 中文文档

## 功能特性

- **多模型切换** — DeepSeek (推理/代码) + Qwen-Max (通用) + Qwen-VL (视觉)
- **流式输出** — SSE 实时逐字显示 AI 回复
- **AI 绘画** — 文本生成图片 (Wanx)
- **AI 视频** — 文本生成视频 (Wanx 2.1)
- **联网搜索** — DashScope 搜索增强
- **图片识别** — 上传图片 + 多模态理解
- **多轮对话** — 多会话管理、置顶、删除、搜索
- **用户体系** — 注册/登录、邀请码裂变
- **算力系统** — 每日签到、连签递增奖励
- **Markdown** — 完整渲染 + 代码高亮 + 一键复制
- **暗色模式** — CSS Variables 一键切换
- **跨平台** — H5 / 微信小程序 / App (uni-app)

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | uni-app + Vue 3 Composition API |
| 后端 | FastAPI + SQLite |
| AI 模型 | DeepSeek API + 阿里云 DashScope |
| 部署 | Nginx 反向代理 + HTTPS |

## 快速开始

### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填入你的 API Key
python main.py
```

或使用一键启动脚本：
```bash
# Linux/Mac
chmod +x deploy/start.sh && ./deploy/start.sh

# Windows
deploy\start.bat
```

服务运行在 `http://localhost:8000`，API 文档在 `http://localhost:8000/docs`。

### 2. 启动前端

1. 安装 [HBuilderX](https://www.dcloud.io/hbuilderx.html)
2. 将 `frontend/` 文件夹作为项目打开
3. 修改 `frontend/config.js` 中的 `API_BASE` 为你的后端地址
4. 运行 → 浏览器 (H5)

```js
// frontend/config.js
export const API_BASE = 'http://localhost:8000';
```

### 3. 生产部署

#### 架构图

```
客户端 (浏览器/App)
    ↓ HTTPS
Nginx (443 端口)
    ├── 静态文件 → /path/to/h5/
    └── API 请求 → proxy_pass → FastAPI (8000 端口)
```

#### 前端构建

HBuilderX 中：**发行 → 网站-H5** → 产物在 `unpackage/dist/build/h5/`

上传到服务器：
```bash
scp -r unpackage/dist/build/h5/* user@server:/var/www/ai-chat/
```

#### 后端部署

```bash
cd /opt/ai-chat/backend
pip install -r requirements.txt
cp .env.example .env
vim .env  # 填入 API Key

# 简单方式
nohup python main.py > server.log 2>&1 &

# 推荐：systemd 管理
sudo systemctl enable ai-chat && sudo systemctl start ai-chat
```

#### 配置 Nginx

```bash
sudo cp deploy/nginx.conf /etc/nginx/conf.d/ai-chat.conf
# 编辑：替换 YOUR_DOMAIN、SSL 路径、H5 路径
sudo nginx -t && sudo nginx -s reload
```

#### Windows 服务器

```batch
REM 复制 H5 文件
xcopy /E /Y unpackage\dist\build\h5\* C:\web\h5\

REM 启动后端
cd C:\ai-chat\backend
python main.py

REM Nginx
taskkill /F /IM nginx.exe
cd C:\nginx && start nginx
```

## API Key 获取

| 服务商 | 获取地址 | 用途 |
|--------|----------|------|
| **DeepSeek** | https://platform.deepseek.com/ | 文本对话、推理、代码 |
| **阿里云 DashScope** | https://dashscope.aliyun.com/ | Qwen 文本/视觉、图片/视频生成 |

两者都有免费额度。

## 配置说明

**后端** `backend/.env`：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DS_API_KEY` | — | DeepSeek API Key |
| `QWEN_API_KEY` | — | DashScope API Key |
| `DS_MODEL_NAME` | `deepseek-chat` | DeepSeek 模型 ID |
| `QWEN_TEXT_MODEL` | `qwen-max` | Qwen 文本模型 |
| `QWEN_MODEL_NAME` | `qwen-vl-max` | Qwen 视觉模型 |
| `HOST` | `0.0.0.0` | 服务绑定地址 |
| `PORT` | `8000` | 服务端口 |

**前端** `frontend/config.js`：

```js
export const API_BASE = 'https://your-domain.com'; // 改为你的服务器地址
```

## 项目结构

```
uni-ai-starter/
├── frontend/                  # uni-app Vue 3 前端
│   ├── pages/
│   │   ├── index/index.vue    # 💬 聊天主页 (流式输出、Markdown、工具)
│   │   ├── discover/          # 🔍 灵感发现 (分类 Prompt 卡片)
│   │   ├── profile/           # 👤 个人中心 (余额、签到、暗色模式)
│   │   ├── login/             # 🔑 登录
│   │   └── register/          # 📝 注册 (邀请码)
│   ├── static/tabbar/         # TabBar 图标
│   ├── config.js              # ⚙️ API 地址配置
│   ├── App.vue                # 全局样式 (亮/暗主题)
│   └── pages.json             # 路由 & tabBar 配置
├── backend/
│   ├── main.py                # 🐍 FastAPI 服务 (~350行)
│   ├── .env.example           # 🔐 环境变量模板
│   └── requirements.txt       # Python 依赖
├── deploy/
│   ├── nginx.conf             # 🌐 Nginx 配置模板
│   ├── start.sh               # 🚀 Linux/Mac 启动脚本
│   └── start.bat              # 🚀 Windows 启动脚本
├── screenshots/               # 📸 截图
├── .gitignore
├── LICENSE (MIT)
└── README.md
```

## 自定义

### 修改主题色

编辑 `frontend/App.vue`：
```css
:root {
  --primary-color: #3370ff;       /* 改这里 */
  --bg-bubble-user: linear-gradient(135deg, #1f65d6, #3370ff);
}
```

### 添加新模型

1. 后端：在 `.env` 添加 Key，在 `main.py` 添加路由
2. 前端：在 `index.vue` 的 `modelOptions` 添加选项

### 切换数据库

将 `main.py` 中的 `sqlite3` 替换为 SQLAlchemy 或其他 ORM。

## API 接口

| 方法 | 接口 | 说明 |
|------|------|------|
| POST | `/register` | 用户注册 |
| POST | `/login` | 用户登录 |
| GET | `/user/info/{id}` | 获取用户信息 |
| POST | `/user/sign/{id}` | 每日签到 |
| GET | `/user/balance/{id}` | 查询余额 |
| GET | `/user/balance_logs/{id}` | 余额明细 |
| POST | `/conversation/create/{id}` | 创建会话 |
| GET | `/conversations/{id}` | 会话列表 |
| PUT | `/conversation/pin/{id}` | 置顶/取消 |
| DELETE | `/conversation/{id}` | 删除会话 |
| GET | `/history/{id}` | 聊天记录 |
| DELETE | `/clear/{id}` | 清空会话 |
| POST | `/chat` | **AI 对话 (SSE 流式)** |

完整 API 文档：`http://localhost:8000/docs` (Swagger UI)

---

<a id="english"></a>

# English

## Features

- **Multi-Model** — DeepSeek (reasoning/code) + Qwen-Max (general) + Qwen-VL (vision)
- **Streaming** — SSE real-time token-by-token output
- **AI Drawing** — Text-to-image via Wanx model
- **AI Video** — Text-to-video via Wanx 2.1
- **Web Search** — DashScope enhanced search
- **Vision** — Upload image + multimodal understanding
- **Multi-conversation** — Create, pin, delete, search conversations
- **User System** — Register/login, invite code referral
- **Balance System** — Daily sign-in with streak bonus
- **Markdown** — Full rendering + code highlight + one-click copy
- **Dark Mode** — CSS Variables one-click toggle
- **Cross-platform** — H5 / WeChat Mini Program / App (uni-app)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | uni-app + Vue 3 Composition API |
| Backend | FastAPI + SQLite |
| AI Models | DeepSeek API + Alibaba DashScope |
| Deploy | Nginx reverse proxy + HTTPS |

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env — fill in your API keys
python main.py
```

Or use the start script:
```bash
# Linux/Mac
chmod +x deploy/start.sh && ./deploy/start.sh

# Windows
deploy\start.bat
```

Server runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### 2. Frontend

1. Install [HBuilderX](https://www.dcloud.io/hbuilderx.html)
2. Open `frontend/` folder as project
3. Edit `frontend/config.js` — set `API_BASE` to your backend URL
4. Run → Browser (H5)

```js
// frontend/config.js
export const API_BASE = 'http://localhost:8000';
```

### 3. Production Deployment

See the [Chinese deployment guide](#3-生产部署) above — the commands are the same.

## Project Structure

```
uni-ai-starter/
├── frontend/                  # uni-app Vue 3 frontend
│   ├── pages/
│   │   ├── index/index.vue    # Main chat page (streaming, markdown, tools)
│   │   ├── discover/          # Prompt discovery (categorized cards)
│   │   ├── profile/           # User profile (balance, sign-in, dark mode)
│   │   ├── login/             # Login page
│   │   └── register/          # Register (with invite code)
│   ├── static/tabbar/         # TabBar icons
│   ├── config.js              # API_BASE config (edit this!)
│   ├── App.vue                # Global CSS variables (light/dark theme)
│   └── pages.json             # Routes & tabBar config
├── backend/
│   ├── main.py                # FastAPI server (~350 lines, all-in-one)
│   ├── .env.example           # Environment template (copy to .env)
│   └── requirements.txt       # Python dependencies
├── deploy/
│   ├── nginx.conf             # Nginx config (HTTPS + reverse proxy)
│   ├── start.sh               # Linux/Mac start script
│   └── start.bat              # Windows start script
├── screenshots/               # Add your screenshots here
├── .gitignore
├── LICENSE (MIT)
└── README.md
```

## API Keys

| Provider | Get Key | Used For |
|----------|---------|----------|
| **DeepSeek** | https://platform.deepseek.com/ | Text chat, reasoning, code |
| **Alibaba DashScope** | https://dashscope.aliyun.com/ | Qwen text, vision, image & video gen |

Both have free tiers to get started.

## Configuration

**Backend** — `backend/.env`:

| Key | Default | Description |
|-----|---------|-------------|
| `DS_API_KEY` | — | DeepSeek API Key |
| `QWEN_API_KEY` | — | DashScope API Key |
| `DS_MODEL_NAME` | `deepseek-chat` | DeepSeek model ID |
| `QWEN_TEXT_MODEL` | `qwen-max` | Qwen text model |
| `QWEN_MODEL_NAME` | `qwen-vl-max` | Qwen vision model |
| `HOST` | `0.0.0.0` | Server bind host |
| `PORT` | `8000` | Server port |

**Frontend** — `frontend/config.js`:

```js
export const API_BASE = 'https://your-domain.com'; // Your production URL
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new user |
| POST | `/login` | User login |
| GET | `/user/info/{id}` | Get user info |
| POST | `/user/sign/{id}` | Daily sign-in |
| GET | `/user/balance/{id}` | Get balance |
| GET | `/user/balance_logs/{id}` | Balance history |
| POST | `/conversation/create/{id}` | Create conversation |
| GET | `/conversations/{id}` | List conversations |
| PUT | `/conversation/pin/{id}` | Toggle pin |
| DELETE | `/conversation/{id}` | Delete conversation |
| GET | `/history/{id}` | Get chat history |
| DELETE | `/clear/{id}` | Clear conversation |
| POST | `/chat` | **Chat (SSE streaming)** |

Full API docs at `http://localhost:8000/docs` (Swagger UI).

## Customization

### Change Theme Color

Edit `frontend/App.vue`:
```css
:root {
  --primary-color: #3370ff;       /* Change this */
  --bg-bubble-user: linear-gradient(135deg, #1f65d6, #3370ff);
}
```

### Add New AI Model

1. Backend: add env vars in `.env` and routing in `main.py`
2. Frontend: add option to `modelOptions` in `index.vue`

### Switch Database

Replace `sqlite3` in `main.py` with SQLAlchemy or any ORM.

---

## License

[MIT](LICENSE)

## Contributing

PRs and issues welcome! Feel free to fork and customize.

If this helps you, please give it a ⭐!
