import os
import time
import hashlib
from collections import OrderedDict
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from gradio_client import Client, handle_file
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed
from pydantic import BaseModel
import uvicorn
import asyncio
import httpx # 导入 httpx 用于发送 HTTP 请求

load_dotenv()

app = FastAPI()

GRADIO_URL = os.getenv("GRADIO_URL", "http://127.0.0.1:7860/")

gradio_client = None

# --- 内存缓存配置 ---
MAX_CACHE_SIZE = int(os.getenv("MAX_CACHE_SIZE", "100")) # 最大缓存条目数
# 使用 OrderedDict 实现 LRU 缓存
# 键是请求的哈希，值是音频内容的bytes
in_memory_cache = OrderedDict()

MODEL_PROMPT_MAP = {
    "chixiaotu": "model_wav/chixiaotu.wav",
    "chixiaotu2" : "model_wav/chixiaotushanghaijiguanqiang.wav",
    "chixiaotu3" : "model_wav/chixiaotu3.wav",   #上海话+普通话合集
    "chixiaotu5" : "model_wav/cxt5.wav",   #上海话+普通话合集abs
    "chixiaotu6" : "model_wav/cxt6.wav",   #上海话+普通话合集
    "chixiaotu4" : "model_wav/cxt4.wav"   #上海话+普通话合集
}

DEFAULT_PROMPT_AUDIO_PATH = "model_wav/default_prompt.wav"

class SpeechRequest(BaseModel):
    model: str
    input: str

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def call_gradio_with_retry(client, *args, **kwargs):
    return client.predict(*args, **kwargs)

@app.on_event("startup")
def initialize():
    global gradio_client
    print("🚀 尝试连接 Gradio 后端服务...")
    for attempt in range(5):
        try:
            gradio_client = Client(GRADIO_URL)
            print(f"✅ Gradio 客户端连接成功！尝试次数: {attempt + 1}")
            break
        except Exception as e:
            print(f"❌ Gradio 客户端连接失败 (尝试 {attempt + 1}/5): {e}")
            time.sleep(2)
    if not gradio_client:
        print("🚨 警告：Gradio 客户端初始化失败，服务可能无法正常工作。")

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
                raise HTTPException(status_code=400, detail=f"不支持的模型 '{speech_request.model}' 且默认参考语音文件 '{DEFAULT_PROMPT_AUDIO_PATH}' 未找到。请确保 'model_wav' 目录存在且包含该文件。")
        
        full_prompt_path = os.path.join(os.getcwd(), prompt_file_path)
        if not os.path.exists(full_prompt_path):
            # 这个检查在上面已经做了一部分，这里可以更具体地提示
            raise HTTPException(status_code=500, detail=f"模型 '{speech_request.model}' 的参考语音文件 '{full_prompt_path}' 未找到。")
        
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
            raise HTTPException(status_code=500, detail="Gradio 返回结果路径无效或文件不存在。")
    except HTTPException:
        raise # 重新抛出已处理的HTTPException
    except Exception as e:
        print(f"💥 处理请求时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")

@app.get('/health')
async def health_check():
    cache_info = {
        "cache_type": "in_memory",
        "current_entries": len(in_memory_cache),
        "max_entries": MAX_CACHE_SIZE
    }
    
    if gradio_client:
        return {"status": "ok", "gradio_connected": True, "cache_info": cache_info, "message": "服务运行正常，Gradio 客户端已连接。"}
    else:
        return {"status": "degraded", "gradio_connected": False, "cache_info": cache_info, "message": "Gradio 客户端未连接，部分功能可能受限。"}

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
    
    # 构造请求体
    payload = {
        "model": "chixiaotu6", 
        "input": "您好。"
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
    loop = asyncio.get_event_loop()
    
    config = uvicorn.Config(app, host="0.0.0.0", port=8010, log_level="info")
    server = uvicorn.Server(config)
    
    async def main():
        server_task = asyncio.create_task(server.serve())
        request_task = asyncio.create_task(send_startup_request())
        
        await asyncio.gather(server_task, request_task)

    loop.run_until_complete(main())
    