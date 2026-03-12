"""
uni-ai-starter Backend
Full-stack AI Chat API with multi-model support, streaming, user system, and balance.
"""
import os
import json
import time
import random
import string
import hashlib
import sqlite3
import requests
import traceback
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import uvicorn

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ===========================================
# Configuration (from .env)
# ===========================================
DS_API_KEY = os.environ.get("DS_API_KEY", "")
DS_API_URL = os.environ.get("DS_API_URL", "https://api.deepseek.com/chat/completions")
DS_MODEL_NAME = os.environ.get("DS_MODEL_NAME", "deepseek-chat")
QWEN_API_KEY = os.environ.get("QWEN_API_KEY", "")
QWEN_API_URL = os.environ.get("QWEN_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
QWEN_MODEL_NAME = os.environ.get("QWEN_MODEL_NAME", "qwen-vl-max")
QWEN_TEXT_MODEL = os.environ.get("QWEN_TEXT_MODEL", "qwen-max")
DB_PATH = os.environ.get("DB_PATH", "app.db")
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", "60"))
RATE_LIMIT_MAX = int(os.environ.get("RATE_LIMIT_MAX", "30"))

# ===========================================
# Database Setup
# ===========================================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        balance INTEGER DEFAULT 150,
        last_sign_date TEXT,
        sign_streak INTEGER DEFAULT 0,
        nickname TEXT DEFAULT '',
        invite_code TEXT DEFAULT '',
        invited_by INTEGER DEFAULT 0,
        created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT DEFAULT '新对话',
        pinned INTEGER DEFAULT 0,
        created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        conversation_id INTEGER DEFAULT 0,
        role TEXT NOT NULL,
        content TEXT,
        image TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS balance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount INTEGER,
        reason TEXT,
        created_at TEXT
    )''')
    # Indexes
    c.execute("CREATE INDEX IF NOT EXISTS idx_msg_user_conv ON messages(user_id, conversation_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_conv_user ON conversations(user_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_balance_user ON balance_logs(user_id)")
    conn.commit()
    conn.close()

init_db()

# ===========================================
# App Setup
# ===========================================
app = FastAPI(title="uni-ai-starter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================================
# Models & Helpers
# ===========================================
class UserAuth(BaseModel):
    username: str
    password: str
    invite_code: str = ""

class ChatRequest(BaseModel):
    user_id: int
    message: str = ""
    messages: list = []
    image_base64: str | None = None
    conversation_id: int = 0
    model: str = "deepseek"

def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def generate_invite_code() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def deduct_balance(user_id: int, amount: int, reason: str = "对话"):
    conn = get_db()
    conn.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, user_id))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO balance_logs (user_id, amount, reason, created_at) VALUES (?, ?, ?, ?)",
                 (user_id, -amount, reason, now))
    conn.commit()
    conn.close()

def add_balance(user_id: int, amount: int, reason: str = "签到"):
    conn = get_db()
    conn.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO balance_logs (user_id, amount, reason, created_at) VALUES (?, ?, ?, ?)",
                 (user_id, amount, reason, now))
    conn.commit()
    conn.close()

# Rate limiting
rate_limit_store = defaultdict(list)

def check_rate_limit(user_id: int) -> bool:
    now = time.time()
    rate_limit_store[user_id] = [t for t in rate_limit_store[user_id] if now - t < RATE_LIMIT_WINDOW]
    if len(rate_limit_store[user_id]) >= RATE_LIMIT_MAX:
        return True
    rate_limit_store[user_id].append(now)
    return False

# ===========================================
# Auth Routes
# ===========================================
@app.post("/register")
async def register(user: UserAuth):
    conn = get_db()
    try:
        code = generate_invite_code()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO users (username, password, balance, invite_code, created_at) VALUES (?, ?, 150, ?, ?)",
            (user.username, hash_password(user.password), code, now)
        )
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        # Handle invite code
        if user.invite_code:
            row = conn.execute("SELECT id FROM users WHERE invite_code = ? AND id != ?",
                              (user.invite_code.upper(), new_id)).fetchone()
            if row:
                conn.execute("UPDATE users SET invited_by = ? WHERE id = ?", (row[0], new_id))
                conn.commit()
                conn.close()
                add_balance(row[0], 100, f"邀请好友({user.username})")
                add_balance(new_id, 50, "受邀奖励")
                return {"code": 200, "msg": "注册成功！邀请奖励已发放"}
        conn.close()
        return {"code": 200, "msg": "注册成功！"}
    except Exception:
        conn.close()
        return {"code": 400, "msg": "用户名已存在"}

@app.post("/login")
async def login(user: UserAuth):
    conn = get_db()
    row = conn.execute("SELECT id, password FROM users WHERE username = ?", (user.username,)).fetchone()
    conn.close()
    if row and row[1] == hash_password(user.password):
        return {"code": 200, "user_id": row[0]}
    return {"code": 401, "msg": "认证失败"}

# ===========================================
# User Routes
# ===========================================
@app.get("/user/info/{user_id}")
async def get_user_info(user_id: int):
    conn = get_db()
    row = conn.execute(
        "SELECT username, balance, last_sign_date, nickname, invite_code, sign_streak FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    if not row:
        return {"code": 404}
    today = datetime.now().strftime("%Y-%m-%d")
    return {
        "code": 200,
        "username": row[0],
        "balance": row[1],
        "has_signed_today": row[2] == today,
        "nickname": row[3] or "",
        "invite_code": row[4] or "",
        "sign_streak": row[5] or 0,
    }

@app.post("/user/sign/{user_id}")
async def daily_sign(user_id: int):
    conn = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    row = conn.execute("SELECT last_sign_date, sign_streak FROM users WHERE id = ?", (user_id,)).fetchone()
    if row and row[0] == today:
        conn.close()
        return {"code": 400, "msg": "今天已经签到过了"}
    old_streak = row[1] if row and row[1] else 0
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    new_streak = (old_streak + 1) if (row and row[0] == yesterday) else 1
    bonus = min(50 + (new_streak - 1) * 5, 100)
    conn.execute("UPDATE users SET last_sign_date = ?, sign_streak = ? WHERE id = ?", (today, new_streak, user_id))
    conn.commit()
    conn.close()
    add_balance(user_id, bonus, f"连续签到第{new_streak}天")
    return {"code": 200, "msg": f"连签第{new_streak}天！算力 +{bonus}", "streak": new_streak, "bonus": bonus}

@app.get("/user/balance/{user_id}")
async def get_balance(user_id: int):
    conn = get_db()
    row = conn.execute("SELECT balance FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return {"code": 200, "balance": row[0] if row else 0}

@app.get("/user/balance_logs/{user_id}")
async def get_balance_logs(user_id: int):
    conn = get_db()
    rows = conn.execute(
        "SELECT amount, reason, created_at FROM balance_logs WHERE user_id = ? ORDER BY id DESC LIMIT 50",
        (user_id,)
    ).fetchall()
    conn.close()
    return {"code": 200, "data": [{"amount": r[0], "reason": r[1], "created_at": r[2]} for r in rows]}

@app.post("/user/update_profile/{user_id}")
async def update_profile(user_id: int, data: dict):
    conn = get_db()
    nickname = data.get("nickname", "").strip()
    if nickname:
        conn.execute("UPDATE users SET nickname = ? WHERE id = ?", (nickname, user_id))
    conn.commit()
    conn.close()
    return {"code": 200, "msg": "更新成功"}

# ===========================================
# Conversation Routes
# ===========================================
@app.post("/conversation/create/{user_id}")
async def create_conversation(user_id: int):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn.execute("INSERT INTO conversations (user_id, title, created_at) VALUES (?, ?, ?)", (user_id, "新对话", now))
    conv_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    conn.close()
    return {"code": 200, "conversation_id": conv_id}

@app.get("/conversations/{user_id}")
async def get_conversations(user_id: int):
    conn = get_db()
    rows = conn.execute(
        "SELECT id, title, created_at, pinned FROM conversations WHERE user_id = ? ORDER BY pinned DESC, id DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return {"code": 200, "data": [{"id": r[0], "title": r[1], "created_at": r[2], "pinned": r[3] or 0} for r in rows]}

@app.put("/conversation/pin/{conv_id}")
async def toggle_pin(conv_id: int):
    conn = get_db()
    row = conn.execute("SELECT pinned FROM conversations WHERE id = ?", (conv_id,)).fetchone()
    new_val = 0 if (row and row[0]) else 1
    conn.execute("UPDATE conversations SET pinned = ? WHERE id = ?", (new_val, conv_id))
    conn.commit()
    conn.close()
    return {"code": 200, "pinned": new_val}

@app.delete("/conversation/{conv_id}")
async def delete_conversation(conv_id: int):
    conn = get_db()
    conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
    conn.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
    conn.commit()
    conn.close()
    return {"code": 200, "msg": "已删除"}

# ===========================================
# Chat History Routes
# ===========================================
@app.get("/history/{user_id}")
async def get_history(user_id: int, conversation_id: int = 0, limit: int = 50, offset: int = 0):
    conn = get_db()
    total = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE user_id = ? AND conversation_id = ?",
        (user_id, conversation_id)
    ).fetchone()[0]
    if offset == 0 and total > limit:
        rows = list(reversed(conn.execute(
            "SELECT role, content, image FROM messages WHERE user_id = ? AND conversation_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, conversation_id, limit)
        ).fetchall()))
    else:
        rows = conn.execute(
            "SELECT role, content, image FROM messages WHERE user_id = ? AND conversation_id = ? ORDER BY id ASC LIMIT ? OFFSET ?",
            (user_id, conversation_id, limit, offset)
        ).fetchall()
    conn.close()
    return {"code": 200, "data": [{"role": r[0], "content": r[1], "image": r[2]} for r in rows], "total": total}

@app.delete("/clear/{user_id}")
async def clear_chat(user_id: int, conversation_id: int = 0):
    conn = get_db()
    conn.execute("DELETE FROM messages WHERE user_id = ? AND conversation_id = ?", (user_id, conversation_id))
    conn.commit()
    conn.close()
    return {"code": 200, "msg": "已清空"}

# ===========================================
# AI Tool Definitions
# ===========================================
AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "draw_image",
            "description": "Generate a static image based on prompt description.",
            "parameters": {"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for real-time information.",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_video",
            "description": "Generate a video clip based on prompt description.",
            "parameters": {
                "type": "object",
                "properties": {"prompt": {"type": "string", "description": "Detailed video description"}},
                "required": ["prompt"]
            }
        }
    }
]

VIDEO_KEYWORDS = ["视频", "动态", "动画", "video", "影片", "短片", "clip"]

def detect_video_intent(message: str) -> bool:
    return any(kw in message.lower() for kw in VIDEO_KEYWORDS)

# ===========================================
# Chat Endpoint (Streaming SSE)
# ===========================================
@app.post("/chat")
async def chat(req: ChatRequest):
    conn = get_db()
    user_row = conn.execute("SELECT balance FROM users WHERE id = ?", (req.user_id,)).fetchone()
    conn.close()
    current_balance = user_row[0] if user_row else 0

    if current_balance < 1:
        async def no_balance():
            yield "余额不足，请签到或充值后继续使用。"
        return StreamingResponse(no_balance(), media_type="text/plain")

    user_message = req.message or "请处理请求"

    # Save user message
    conn = get_db()
    conn.execute(
        "INSERT INTO messages (user_id, role, content, image, conversation_id) VALUES (?, ?, ?, ?, ?)",
        (req.user_id, 'user', user_message, req.image_base64, req.conversation_id)
    )
    conn.commit()

    # Load conversation history
    rows = conn.execute(
        "SELECT role, content FROM messages WHERE user_id = ? AND conversation_id = ? ORDER BY id ASC",
        (req.user_id, req.conversation_id)
    ).fetchall()
    conn.close()

    formatted = [{"role": r[0], "content": r[1]} for r in rows]

    sys_prompt = """你是 AI Assistant，拥有调用外部工具的能力。
规则：
1. 用户要求图片/画 → 调用 draw_image
2. 用户要求视频/动画 → 调用 generate_video
3. 用户要搜索实时信息 → 调用 web_search
4. 回复结尾带 @@@问题1|问题2|问题3@@@ 作为推荐追问"""

    formatted.insert(0, {"role": "system", "content": sys_prompt})
    user_wants_video = detect_video_intent(user_message)

    def generate_stream():
        nonlocal current_balance
        full_response = ""

        if check_rate_limit(req.user_id):
            yield "请求过于频繁，请稍后再试。"
            return

        deduct_balance(req.user_id, 1, "AI对话")
        current_balance -= 1

        # Vision model for image input
        if req.image_base64:
            img_data = req.image_base64 if req.image_base64.startswith("data:image") else f"data:image/jpeg;base64,{req.image_base64}"
            vl_msgs = formatted[:-1]
            vl_msgs.append({"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": img_data}},
                {"type": "text", "text": user_message}
            ]})
            resp = requests.post(
                QWEN_API_URL,
                headers={"Authorization": f"Bearer {QWEN_API_KEY}"},
                json={"model": QWEN_MODEL_NAME, "messages": vl_msgs, "stream": True}
            )
            for line in resp.iter_lines():
                if line:
                    s = line.decode('utf-8')
                    if s.startswith("data: ") and "[DONE]" not in s:
                        chunk = json.loads(s[6:])["choices"][0]["delta"].get("content", "")
                        full_response += chunk
                        yield chunk
        else:
            # Text model with tool calling
            use_model = req.model
            if use_model == "qwen":
                api_url, api_key, model_name = QWEN_API_URL, QWEN_API_KEY, QWEN_TEXT_MODEL
            else:
                api_url, api_key, model_name = DS_API_URL, DS_API_KEY, DS_MODEL_NAME

            max_loops = 5
            for loop_i in range(max_loops):
                body = {"model": model_name, "messages": formatted, "tools": AGENT_TOOLS, "stream": True}
                if loop_i == 0 and user_wants_video:
                    body["tool_choice"] = {"type": "function", "function": {"name": "generate_video"}}

                resp = requests.post(api_url, headers={"Authorization": f"Bearer {api_key}"}, json=body)
                tool_calls = []
                is_tool_call = False

                for line in resp.iter_lines():
                    if not line:
                        continue
                    s = line.decode('utf-8')
                    if not s.startswith("data: ") or "[DONE]" in s:
                        continue
                    data = json.loads(s[6:])
                    delta = data["choices"][0]["delta"]

                    if "tool_calls" in delta and delta["tool_calls"]:
                        is_tool_call = True
                        for tc in delta["tool_calls"]:
                            idx = tc["index"]
                            while len(tool_calls) <= idx:
                                tool_calls.append({"name": "", "arguments": ""})
                            if "function" in tc:
                                if "name" in tc["function"]:
                                    tool_calls[idx]["name"] += tc["function"]["name"]
                                if "arguments" in tc["function"]:
                                    tool_calls[idx]["arguments"] += tc["function"]["arguments"]
                    elif "content" in delta and not is_tool_call:
                        chunk = delta.get("content", "")
                        if chunk:
                            full_response += chunk
                            yield chunk

                if not is_tool_call or not tool_calls:
                    break

                # Execute tool
                func_name = tool_calls[0]["name"]
                args = json.loads(tool_calls[0]["arguments"])
                observation = ""

                if func_name == "web_search":
                    query = args.get("query", "")
                    yield f"\n\n> 🔍 搜索中：「{query}」...\n\n"
                    try:
                        import dashscope
                        res = dashscope.Generation.call(
                            model='qwen-max',
                            messages=[{'role': 'user', 'content': f"搜索并总结：{query}"}],
                            result_format='message',
                            api_key=QWEN_API_KEY,
                            enable_search=True
                        )
                        observation = res.output.choices[0].message.content
                    except Exception as e:
                        observation = f"搜索失败: {e}"

                elif func_name == "draw_image":
                    if current_balance < 10:
                        yield "\n\n余额不足：绘画需要 10 点算力。\n"
                        break
                    deduct_balance(req.user_id, 10, "AI绘画")
                    current_balance -= 10
                    prompt = args.get("prompt", "")
                    yield f"\n\n> 🎨 生成图片中：「{prompt[:30]}...」\n\n"
                    try:
                        from dashscope import ImageSynthesis
                        task = ImageSynthesis.call(
                            model="wanx-v1", prompt=prompt, n=1,
                            size='1024*1024', api_key=QWEN_API_KEY
                        )
                        if task.status_code == 200:
                            url = task.output.results[0].url
                            yield f"[IMAGE:{url}]\n\n"
                            observation = f"图片已生成：{url}"
                        else:
                            yield f"\n\n图片生成失败：{task.message}\n"
                            observation = f"失败：{task.message}"
                    except Exception as e:
                        yield f"\n\n绘画异常：{e}\n"
                        observation = f"失败: {e}"

                elif func_name == "generate_video":
                    if current_balance < 50:
                        yield "\n\n余额不足：视频需要 50 点算力。\n"
                        break
                    deduct_balance(req.user_id, 50, "AI视频")
                    current_balance -= 50
                    prompt = args.get("prompt", "")
                    yield f"\n\n> 🎬 生成视频中：「{prompt[:30]}...」\n\n"
                    try:
                        from dashscope import VideoSynthesis
                        task = VideoSynthesis.call(
                            model="wanx2.1-t2v-turbo", prompt=prompt, api_key=QWEN_API_KEY
                        )
                        if task.status_code == 200 and task.output and task.output.task_id:
                            task_id = task.output.task_id
                            yield "> 任务已提交，生成中...\n\n"
                            for _ in range(60):
                                time.sleep(5)
                                status = VideoSynthesis.fetch(task_id, api_key=QWEN_API_KEY)
                                ts = status.output.task_status if status.output else "UNKNOWN"
                                if ts == "SUCCEEDED":
                                    video_url = status.output.video_url
                                    yield f"[VIDEO:{video_url}]\n\n"
                                    observation = f"视频已生成：{video_url}"
                                    break
                                elif ts in ("FAILED", "UNKNOWN"):
                                    yield "\n\n视频生成失败。\n"
                                    observation = "视频生成失败"
                                    break
                            else:
                                yield "\n\n视频生成超时。\n"
                                observation = "超时"
                        else:
                            yield f"\n\n视频任务提交失败：{task.message}\n"
                            observation = f"失败：{task.message}"
                    except Exception as e:
                        yield f"\n\n视频异常：{e}\n"
                        observation = f"失败: {e}"

                # Feed observation back to model
                formatted.append({"role": "assistant", "content": None,
                                  "tool_calls": [{"id": "call_0", "type": "function",
                                                  "function": {"name": func_name, "arguments": json.dumps(args)}}]})
                formatted.append({"role": "tool", "tool_call_id": "call_0", "content": observation})

        # Save AI response
        if full_response:
            conn2 = get_db()
            conn2.execute(
                "INSERT INTO messages (user_id, role, content, conversation_id) VALUES (?, ?, ?, ?)",
                (req.user_id, 'ai', full_response, req.conversation_id)
            )
            # Auto-title: set conversation title from first exchange
            conn2.execute(
                "UPDATE conversations SET title = ? WHERE id = ? AND title = '新对话'",
                (user_message[:20], req.conversation_id)
            )
            conn2.commit()
            conn2.close()

    return StreamingResponse(generate_stream(), media_type="text/plain")

# ===========================================
# Entry Point
# ===========================================
if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    print(f"🚀 Server starting at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
