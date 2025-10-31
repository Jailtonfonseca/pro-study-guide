import os
import httpx
import structlog
import logging
import json
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any

# --- Configuração do Logging Estruturado ---
logging.basicConfig(level=logging.INFO, format="%(message)s")
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

# --- Constantes ---
API_KEYS_FILE = "api_keys.json"

# --- Funções Auxiliares para Chaves de API ---
def load_api_keys() -> Dict[str, str]:
    if not os.path.exists(API_KEYS_FILE):
        return {}
    try:
        with open(API_KEYS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.error("api_keys_file_read_error", error=str(e))
        return {}

def save_api_keys(keys: Dict[str, str]):
    try:
        with open(API_KEYS_FILE, "w") as f:
            json.dump(keys, f, indent=2)
    except IOError as e:
        log.error("api_keys_file_write_error", error=str(e))
        raise HTTPException(status_code=500, detail="Não foi possível salvar o arquivo de chaves de API.")

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
        "supported_models": ["gemini-pro"],
    },
    "openrouter": {
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_key_name": "OPENROUTER_API_KEY",
        "supported_models": ["openai/gpt-4o-mini", "google/gemini-flash-1.5", "meta-llama/llama-3-8b-instruct"],
    },
}

def get_api_key(provider: str) -> str | None:
    """Busca a chave de API, priorizando o arquivo JSON e depois variáveis de ambiente."""
    provider_lower = provider.lower()
    keys = load_api_keys()

    # Checa pelo nome do provedor (e.g., "openai")
    if provider_lower in keys and keys[provider_lower]:
        return keys[provider_lower]

    # Checa pelo nome da variável de ambiente (e.g., "OPENAI_API_KEY")
    api_key_name = PROVIDER_CONFIG.get(provider_lower, {}).get("api_key_name")
    if api_key_name in keys and keys[api_key_name]:
        return keys[api_key_name]

    # Fallback para variáveis de ambiente
    if api_key_name:
        return os.getenv(api_key_name)

    return None

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

class ApiKey(BaseModel):
    provider: str
    api_key: str

# --- Endpoints de Gerenciamento de Chaves ---
@app.get("/api/v1/keys")
def get_keys():
    """Lista provedores e indica se a chave está configurada (sem expor a chave)."""
    keys = load_api_keys()
    response = {}
    for provider, config in PROVIDER_CONFIG.items():
        key_name = config["api_key_name"]
        # Retorna a chave mascarada se existir, para o frontend exibir
        saved_key = keys.get(provider) or keys.get(key_name)
        if saved_key:
            response[provider] = f"{saved_key[:4]}...{saved_key[-4:]}"
        else:
            response[provider] = None
    return response

@app.post("/api/v1/keys")
def save_key(api_key: ApiKey):
    """Salva ou atualiza a chave de um provedor."""
    if api_key.provider.lower() not in PROVIDER_CONFIG:
        raise HTTPException(status_code=400, detail="Provedor inválido.")

    keys = load_api_keys()
    keys[api_key.provider.lower()] = api_key.api_key
    save_api_keys(keys)
    log.info("api_key_saved", provider=api_key.provider)
    return {"status": "ok", "provider": api_key.provider}

@app.delete("/api/v1/keys/{provider}")
def delete_key(provider: str):
    """Remove a chave de um provedor."""
    provider_lower = provider.lower()
    if provider_lower not in PROVIDER_CONFIG:
        raise HTTPException(status_code=400, detail="Provedor inválido.")

    keys = load_api_keys()
    key_name = PROVIDER_CONFIG[provider_lower]["api_key_name"]

    key_removed = False
    if provider_lower in keys:
        del keys[provider_lower]
        key_removed = True
    if key_name in keys:
        del keys[key_name]
        key_removed = True

    if not key_removed:
        raise HTTPException(status_code=404, detail=f"Nenhuma chave encontrada para o provedor '{provider}'.")

    save_api_keys(keys)
    log.info("api_key_deleted", provider=provider)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)


# --- Endpoints da API Principal ---
@app.post("/api/v1/chat")
async def chat_proxy(request: ChatRequest):
    provider = request.provider.lower()
    logger = log.bind(provider=provider, model=request.model)
    logger.info("chat_request_received")

    if provider not in PROVIDER_CONFIG:
        logger.warn("unsupported_provider")
        raise HTTPException(status_code=400, detail=f"Provedor '{request.provider}' não é suportado.")

    config = PROVIDER_CONFIG[provider]

    if request.model not in config.get("supported_models", []):
        logger.warn("unsupported_model_for_provider", supported_models=config.get("supported_models", []))
        raise HTTPException(status_code=400, detail=f"Modelo '{request.model}' não é suportado pelo provedor '{provider}'.")

    api_key = get_api_key(provider)
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
                        error_detail = body.decode()
                        logger.error("provider_api_error", status_code=response.status_code, response_body=error_detail)
                        yield f'{{"error": "PROVIDER_ERROR", "status_code": {response.status_code}, "detail": "{json.dumps(error_detail)}"}}'
                        return
                    async for chunk in response.aiter_bytes():
                        yield chunk
            except httpx.RequestError as e:
                logger.error("provider_connection_error", error=str(e))
                yield f'{{"error": "CONNECTION_ERROR", "detail": "Não foi possível conectar ao provedor de API: {e}"}}'

    return StreamingResponse(stream_response(), media_type="application/x-ndjson")

def chunk_text(text: str, max_length: int = 4000):
    parts, buffer = [], ""
    for para in text.split('\n\n'):
        if not para.strip(): continue
        if len(buffer) + len(para) + 2 > max_length:
            if buffer: parts.append(buffer)
            if len(para) > max_length:
                for i in range(0, len(para), max_length): parts.append(para[i:i+max_length])
                buffer = ""
            else:
                buffer = para
        else:
            buffer = f"{buffer}\n\n{para}" if buffer else para
    if buffer: parts.append(buffer)
    return parts

@app.post("/api/v1/tts")
async def tts_proxy(request: TTSRequest):
    logger = log.bind(model=request.model, voice=request.voice)
    logger.info("tts_request_received")

    api_key = get_api_key("openai")
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
                        logger.error("openai_tts_api_error", chunk_index=i, status_code=response.status_code, response_body=error_detail.decode())
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
