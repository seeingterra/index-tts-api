import os
import time
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from gradio_client import Client, handle_file
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed
from pydantic import BaseModel
import uvicorn

load_dotenv()

app = FastAPI()

GRADIO_URL = os.getenv("GRADIO_URL", "http://127.0.0.1:7860/")

gradio_client = None

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
    for attempt in range(5):
        try:
            gradio_client = Client(GRADIO_URL)
            break
        except Exception:
            time.sleep(2)

@app.post('/v1/audio/speech')
async def create_speech(speech_request: SpeechRequest):
    try:
        if not gradio_client:
            raise HTTPException(status_code=503, detail="Gradio 后端服务未连接或初始化失败")
        
        prompt_file_path = MODEL_PROMPT_MAP.get(speech_request.model)
        if not prompt_file_path:
            prompt_file_path = DEFAULT_PROMPT_AUDIO_PATH
            if not os.path.exists(os.path.join(os.getcwd(), prompt_file_path)):
                raise HTTPException(status_code=400, detail=f"不支持的模型 '{speech_request.model}' 且默认参考语音文件未找到")
        
        full_prompt_path = os.path.join(os.getcwd(), prompt_file_path)
        if not os.path.exists(full_prompt_path):
            raise HTTPException(status_code=500, detail=f"模型 '{speech_request.model}' 的参考语音文件未找到")
        
        file_data = handle_file(full_prompt_path)
        
        print(f"要转换为语音的文本是:\n{speech_request.input}")

        result = call_gradio_with_retry(
            gradio_client,
            prompt=file_data,
            text=speech_request.input,
            #infer_mode="批次推理",
            infer_mode="普通推理",
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
            
            try:
                os.remove(result_path)
            except Exception:
                pass
                
            return Response(content=audio_content, media_type="audio/wav")
        else:
            raise HTTPException(status_code=500, detail="无法访问生成的音频文件")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")

@app.get('/health')
async def health_check():
    if gradio_client:
        return {"status": "ok", "gradio_connected": True}
    else:
        return {"status": "degraded", "gradio_connected": False}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)
