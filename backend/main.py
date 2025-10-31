import os
import httpx
import structlog
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any

# --- Configuração do Logging Estruturado ---
# Configura o logging padrão do Python para ser o sink do structlog
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Configura o structlog para cuspir logs em JSON
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

log = structlog.get_logger()

app = FastAPI()

# --- Configuração dos Provedores ---
PROVIDER_CONFIG = {
    "openai": {
        "api_url": "https://api.openai.com/v1/chat/completions",
        "api_key_name": "OPENAI_API_KEY",
        "supported_models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    },
    "groq": {
        "api_url": "https://api.groq.com/openai/v1/chat/completions",
        "api_key_name": "GROQ_API_KEY",
        "supported_models": ["llama3-8b-8192", "llama3-70b-8192", "gemma-7b-it", "mixtral-8x7b-32768"],
    },
    "gemini": {
        "api_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:streamGenerateContent",
        "api_key_name": "GEMINI_API_KEY",
        "supported_models": ["gemini-pro"], # Exemplo
    },
    "openrouter": {
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_key_name": "OPENROUTER_API_KEY",
        "supported_models": ["openai/gpt-4o-mini", "google/gemini-flash-1.5", "meta-llama/llama-3-8b-instruct"], # Exemplos
    },
}

# --- Modelos de Requisição ---
class ChatRequest(BaseModel):
    provider: str
    model: str
    messages: List[Dict[str, str]]
    stream: bool = True

class TTSRequest(BaseModel):
    model: str
    voice: str
    input: str
    format: str = "mp3"

# --- Endpoints da API ---
@app.post("/api/v1/chat")
async def chat_proxy(request: ChatRequest):
    provider = request.provider.lower()
    logger = log.bind(provider=provider, model=request.model)
    logger.info("chat_request_received")

    if provider not in PROVIDER_CONFIG:
        logger.warn("unsupported_provider")
        raise HTTPException(status_code=400, detail=f"Provedor '{request.provider}' não é suportado.")

    config = PROVIDER_CONFIG[provider]

    # Validação: O modelo é suportado pelo provedor?
    if request.model not in config.get("supported_models", []):
        logger.warn("unsupported_model_for_provider", supported_models=config.get("supported_models", []))
        raise HTTPException(status_code=400, detail=f"Modelo '{request.model}' não é suportado pelo provedor '{provider}'.")

    api_key = os.getenv(config["api_key_name"])
    if not api_key:
        logger.error("api_key_not_configured")
        raise HTTPException(status_code=500, detail=f"A chave de API para {provider} não está configurada no servidor.")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": request.model, "messages": request.messages, "stream": request.stream}
    api_url = config["api_url"]

    async def stream_response():
        async with httpx.AsyncClient(timeout=300) as client:
            try:
                async with client.stream("POST", api_url, json=payload, headers=headers) as response:
                    if response.status_code != 200:
                        body = await response.aread()
                        logger.error(
                            "provider_api_error",
                            status_code=response.status_code,
                            response_body=body.decode(),
                        )
                        # Envia um erro estruturado para o cliente dentro do stream
                        yield f'{{"error": "PROVIDER_ERROR", "status_code": {response.status_code}, "detail": "{body.decode()}"}}\n'
                        return

                    async for chunk in response.aiter_bytes():
                        yield chunk
            except httpx.RequestError as e:
                logger.error("provider_connection_error", error=str(e))
                yield f'{{"error": "CONNECTION_ERROR", "detail": "Não foi possível conectar ao provedor de API: {e}"}}\n'

    return StreamingResponse(stream_response(), media_type="application/x-ndjson")

def chunk_text(text: str, max_length: int = 4000):
    parts, buffer = [], ""
    for para in text.split('\n\n'):
        if not para.strip(): continue
        if len(buffer) + len(para) + 2 > max_length:
            if buffer: parts.append(buffer)
            buffer = para[i:i+max_length] if len(para) > max_length else para
            if len(para) > max_length:
                for i in range(0, len(para), max_length): parts.append(para[i:i+max_length])
                buffer = ""
        else:
            buffer = f"{buffer}\n\n{para}" if buffer else para
    if buffer: parts.append(buffer)
    return parts

@app.post("/api/v1/tts")
async def tts_proxy(request: TTSRequest):
    logger = log.bind(model=request.model, voice=request.voice)
    logger.info("tts_request_received")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("openai_tts_api_key_not_configured")
        raise HTTPException(status_code=500, detail="A chave de API da OpenAI (para TTS) não está configurada.")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    text_chunks = chunk_text(request.input)
    base_payload = request.model_dump(); base_payload.pop("input", None)

    async def stream_audio():
        async with httpx.AsyncClient(timeout=180) as client:
            for i, chunk in enumerate(text_chunks):
                payload = {**base_payload, "input": chunk}
                try:
                    response = await client.post("https://api.openai.com/v1/audio/speech", json=payload, headers=headers)
                    if response.status_code != 200:
                        error_detail = await response.aread()
                        logger.error(
                            "openai_tts_api_error",
                            chunk_index=i,
                            status_code=response.status_code,
                            response_body=error_detail.decode(),
                        )
                        return
                    async for audio_chunk in response.aiter_bytes():
                        yield audio_chunk
                except httpx.RequestError as e:
                    logger.error("openai_tts_connection_error", chunk_index=i, error=str(e))
                    return

    media_type = f"audio/{request.format.lower()}" if request.format else "audio/mpeg"
    return StreamingResponse(stream_audio(), media_type=media_type)

@app.get("/")
def health_check():
    log.info("health_check_called")
    return {"status": "ok"}
