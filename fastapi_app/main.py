import os
import time
import hashlib
from collections import OrderedDict
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from gradio_client import Client, handle_file
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed
from pydantic import BaseModel
import uvicorn
import asyncio
import httpx # 导入 httpx 用于发送 HTTP 请求
from fastapi.middleware.cors import CORSMiddleware

# 1. 导入新的 WebSocket 管理器
from websocket_manager import router as websocket_router, manager as websocket_manager

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global gradio_client, MODEL_PROMPT_MAP
    print("🚀 正在初始化服务...")
    
    # 动态加载模型参考语音
    print("🔍 开始加载模型参考语音...")
    MODEL_PROMPT_MAP = load_model_prompt_map()
    print("✅ 模型参考语音加载完成。")

    # 打印 API 和 WebSocket 地址
    host = os.getenv("UVICORN_HOST", "127.0.0.1")
    port = int(os.getenv("UVICORN_PORT", "8010"))
    print(f"\n🎉 服务已启动！")
    print(f"🔗 API 文档 (Swagger UI): http://{host}:{port}/docs")
    print(f"🔌 WebSocket 连接地址: ws://{host}:{port}/ws\n")

    for attempt in range(5):
        try:
            gradio_client = Client(GRADIO_URL)
            print(f"✅ Gradio 客户端连接成功！尝试次数: {attempt + 1}")
            # 连接成功后，作为后台任务启动自动请求
            asyncio.create_task(send_startup_request())
            break
        except Exception as e:
            print(f"❌ Gradio 客户端连接失败 (尝试 {attempt + 1}/5): {e}")
            await asyncio.sleep(2)
    if not gradio_client:
        print("🚨 警告：Gradio 客户端初始化失败，服务可能无法正常工作。" )
    
    # 启动后台监控任务
    monitor_task = asyncio.create_task(monitor_inactivity())
    
    yield
    
    # Shutdown
    print("🔌 正在关闭服务...")
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        print("✅ 后台监控任务已成功取消。")


app = FastAPI(lifespan=lifespan)

# --- 新增：用于记录被拒绝的 WebSocket 连接的中间件 ---
ALLOWED_ORIGINS = {"http://localhost:19100", "http://hdcotd--8010.ap-shanghai.cloudstudio.work"}

@app.middleware("http")
async def log_denied_websocket_connections(request: Request, call_next):
    if request.scope["type"] == "websocket":
        origin = request.headers.get("origin")
        if origin not in ALLOWED_ORIGINS:
            print(f"[CORS] ❌ 拒绝了来自未经授权的源 <{origin}> 的 WebSocket 连接请求。", flush=True)
    
    response = await call_next(request)
    return response
# --- 中间件结束 ---

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:19100", "http://hdcotd--8010.ap-shanghai.cloudstudio.work"],  # 允许来自指定源的请求
    allow_credentials=True, # 允许携带 cookie
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 请求头
)

# 2. 将 WebSocket 路由集成到主应用中
app.include_router(websocket_router)

GRADIO_URL = os.getenv("GRADIO_URL", "http://127.0.0.1:7860/")

gradio_client = None

# --- 内存缓存配置 ---
MAX_CACHE_SIZE = int(os.getenv("MAX_CACHE_SIZE", "100")) # 最大缓存条目数
# 使用 OrderedDict 实现 LRU 缓存
# 键是请求的哈希，值是音频内容的bytes
in_memory_cache = OrderedDict()

MODEL_PROMPT_MAP = {}
def load_model_prompt_map():
    """
    动态加载 model_wav 目录下的所有 .wav 和 .m4a 文件，并生成 MODEL_PROMPT_MAP。
    键是文件名（不含扩展名），值是文件的相对路径。
    """
    model_wav_dir = "model_wav"
    supported_extensions = (".wav", ".m4a")  # 支持的文件扩展名
    if not os.path.isdir(model_wav_dir):
        print(f"⚠️ 警告：'{model_wav_dir}' 目录不存在，无法加载任何模型参考语音。")
        return {}

    prompt_map = {}
    for filename in os.listdir(model_wav_dir):
        if filename.lower().endswith(supported_extensions):
            model_name = os.path.splitext(filename)[0]
            prompt_map[model_name] = os.path.join(model_wav_dir, filename)
            print(f"  - 发现模型: '{model_name}' -> '{prompt_map[model_name]}'")
    
    if not prompt_map:
        print(f"⚠️ 警告：在 '{model_wav_dir}' 目录中没有找到任何支持的音频文件 ({', '.join(supported_extensions)})。")
        
    return prompt_map

DEFAULT_PROMPT_AUDIO_PATH = "model_wav/default_prompt.wav"

class SpeechRequest(BaseModel):
    model: str
    input: str

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def call_gradio_with_retry(client, *args, **kwargs):
    return client.predict(*args, **kwargs)

@app.post('/v1/audio/speech')
async def create_speech(speech_request: SpeechRequest):
    try:
        if not gradio_client:
            raise HTTPException(status_code=503, detail="Gradio 后端服务未连接或初始化失败")
        
        # --- 内存缓存逻辑 ---
        # 生成缓存键：使用模型名和输入文本的哈希值
        cache_key_content = f"{speech_request.model}:{speech_request.input}"
        cache_key = hashlib.md5(cache_key_content.encode()).hexdigest()

        # 尝试从内存缓存获取
        if cache_key in in_memory_cache:
            # 将访问的键移动到 OrderedDict 的末尾，表示最近使用
            in_memory_cache.move_to_end(cache_key)
            print(f"🎯 命中内存缓存: {cache_key} (模型: {speech_request.model}, 文本长度: {len(speech_request.input)})")
            return Response(content=in_memory_cache[cache_key], media_type="audio/wav")
        # --- 缓存逻辑结束 ---
        
        # 缓存未命中，继续生成新音频
        prompt_file_path = MODEL_PROMPT_MAP.get(speech_request.model)
        if not prompt_file_path:
            prompt_file_path = DEFAULT_PROMPT_AUDIO_PATH
            # 注意：这里需要检查文件是否存在，如果不存在，即使是默认路径也应报错
            if not os.path.exists(os.path.join(os.getcwd(), prompt_file_path)):
                raise HTTPException(status_code=400, detail=f"不支持的模型 '{speech_request.model}' 且默认参考语音文件 '{DEFAULT_PROMPT_AUDIO_PATH}' 未找到。请确保 'model_wav' 目录存在且包含该文件。" )
        
        full_prompt_path = os.path.join(os.getcwd(), prompt_file_path)
        if not os.path.exists(full_prompt_path):
            # 这个检查在上面已经做了一部分，这里可以更具体地提示
            raise HTTPException(status_code=500, detail=f"模型 '{speech_request.model}' 的参考语音文件 '{full_prompt_path}' 未找到。" )
        
        file_data = handle_file(full_prompt_path)
        
        print(f"📝 收到请求：要转换为语音的文本是: '{speech_request.input}'，模型是: '{speech_request.model}'")
        print(f"🔄 内存缓存未命中，开始生成新音频...")

        result = call_gradio_with_retry(
            gradio_client,
            prompt=file_data,
            text=speech_request.input,
            infer_mode="普通推理", # 保持与原代码一致
            max_text_tokens_per_sentence=80,
            sentences_bucket_max_size=6,
            param_5=True, param_6=0.9, param_7=70, param_8=1.5, param_9=0, param_10=5, param_11=8, param_12=600,
            api_name="/gen_single"
        )
        
        result_path = None
        if isinstance(result, dict):
            if 'value' in result:
                result_path = result['value']
            elif 'path' in result:
                result_path = result['path']
        elif isinstance(result, str):
            result_path = result
            
        if result_path and os.path.exists(result_path):
            with open(result_path, "rb") as audio_file:
                audio_content = audio_file.read()
            
            # --- 内存缓存逻辑：保存新生成的音频 ---
            if len(in_memory_cache) >= MAX_CACHE_SIZE:
                # 缓存达到上限，移除最旧的（LRU）
                oldest_key, _ = in_memory_cache.popitem(last=False) # last=False 移除最旧的
                print(f"🧹 内存缓存达到上限，移除最旧条目: {oldest_key}")
            
            in_memory_cache[cache_key] = audio_content
            print(f"💾 音频已加入内存缓存: {cache_key}, 当前缓存条目数: {len(in_memory_cache)}")
            # --- 缓存逻辑结束 ---

            try:
                os.remove(result_path)
                print(f"🗑️ 成功删除临时音频文件: {result_path}")
            except Exception as e:
                print(f"⚠️ 删除临时音频文件失败 {result_path}: {e}")
                pass # 不影响主流程
                
            return Response(content=audio_content, media_type="audio/wav")
        else:
            print(f"🚨 错误：Gradio 返回结果路径无效或文件不存在。Result: {result}")
            raise HTTPException(status_code=500, detail="Gradio 返回结果路径无效或文件不存在。" )
    except HTTPException:
        raise # 重新抛出已处理的HTTPException
    except Exception as e:
        print(f"💥 处理请求时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")

@app.get('/health')
def health_check():
    cache_info = {
        "cache_type": "in_memory",
        "current_entries": len(in_memory_cache),
        "max_entries": MAX_CACHE_SIZE
    }
    
    if gradio_client:
        return {"status": "ok", "gradio_connected": True, "cache_info": cache_info, "message": "服务运行正常，Gradio 客户端已连接。"}
    else:
        return {"status": "degraded", "gradio_connected": False, "cache_info": cache_info, "message": "Gradio 客户端未连接，部分功能可能受限。"}

# --- 新增：服务活动监控 ---
INACTIVITY_TIMEOUT = 1800  # 30分钟的秒数
# 4. 移除不再需要的 NOTIFICATION_URL
# NOTIFICATION_URL = "http://127.0.0.1:8082/notify"
last_activity_time = time.time()

@app.middleware("http")
async def update_activity_timestamp(request: Request, call_next):
    """中间件，在每个请求处理后更新活动时间戳。"""
    global last_activity_time
    last_activity_time = time.time()
    print(f"\n\n 🚨 当前 last_activity_time 的值为： {last_activity_time} \n\n")
    response = await call_next(request)
    return response

async def monitor_inactivity():
    """后台任务，监控并处理服务长时间无活动的情况。"""
    global last_activity_time
    while True:
        await asyncio.sleep(60)  # 每60秒检查一次
        idle_time = time.time() - last_activity_time
        
        if idle_time > INACTIVITY_TIMEOUT:
            print(f"🚨 服务已空闲超过 {INACTIVITY_TIMEOUT} 秒，触发通知...")
            # 3. 直接调用 websocket_manager 的广播方法
            await websocket_manager.broadcast("stop edge")
            print(f"✅ 已通过 WebSocket 管理器发送通知。" )
            # 重置计时器，防止在下一个周期立即重复发送
            last_activity_time = time.time()
        else:
             print(f"🚨 服务已记录空闲时间 {idle_time:.2f} 秒 (当前连接数: {len(websocket_manager.active_connections)}) ======", flush=True)

# --- 新增部分：自动发送请求 ---

async def send_startup_request():
    """
    在服务启动后发送一个测试请求。
    """
    await asyncio.sleep(2) # 等待5秒，确保服务完全启动并监听
    print("\n🌟 服务启动成功！尝试发送一个自动请求...")
    
    # 获取当前运行的Uvicorn地址和端口
    # 注意：在实际部署中，可能需要根据环境变量或配置来确定HOST和PORT
    host = os.getenv("UVICORN_HOST", "127.0.0.1")
    port = os.getenv("UVICORN_PORT", "8010")
    
    request_url = f"http://{host}:{port}/v1/audio/speech"
    headers = {"Content-Type": "application/json"}
    
    # 动态构造请求体
    # 检查 MODEL_PROMPT_MAP 是否有已加载的模型
    if MODEL_PROMPT_MAP:
        # 使用列表中的第一个模型
        first_model_name = next(iter(MODEL_PROMPT_MAP))
    else:
        # 如果没有找到任何模型，则使用一个默认的备用名称
        first_model_name = "default_model"
        print("⚠️ 警告：未在 model_wav 目录中找到任何模型，将使用默认模型名进行启动测试。")

    payload = {
        "model": first_model_name, 
        "input": "您好，欢迎使用。"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"发送第一次请求: {payload['input']}")
            response = await client.post(request_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ 第一次自动请求发送成功！状态码: {response.status_code}, 响应内容类型: {response.headers.get('Content-Type')}")
                # 等待一小段时间，再次发送相同的请求，验证缓存
                await asyncio.sleep(1) 
                print(f"发送第二次请求 (期望命中缓存): {payload['input']}")
                response_cached = await client.post(request_url, headers=headers, json=payload, timeout=30)
                if response_cached.status_code == 200:
                    print(f"✅ 第二次自动请求发送成功！(期望命中缓存) 状态码: {response_cached.status_code}")
                else:
                    print(f"❌ 第二次自动请求失败！状态码: {response_cached.status_code}, 响应体: {response_cached.text}")
            else:
                print(f"❌ 第一次自动请求失败！状态码: {response.status_code}, 响应体: {response.text}")
    except httpx.RequestError as e:
        print(f"💥 自动请求发送过程中发生网络错误: {e}")
    except Exception as e:
        print(f"🚨 自动请求处理过程中发生未知错误: {e}")
    print("--- 自动请求任务完成 ---")

if __name__ == "__main__":
    config = uvicorn.Config(app, host="0.0.0.0", port=8010, log_level="info")
    server = uvicorn.Server(config)
    asyncio.run(server.serve())
    