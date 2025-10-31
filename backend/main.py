import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

# Mapeamento de provedores para suas URLs de API e nomes de variáveis de ambiente
PROVIDER_CONFIG = {
    "openai": {
        "api_url": "https://api.openai.com/v1/chat/completions",
        "api_key_name": "OPENAI_API_KEY",
    },
    "groq": {
        "api_url": "https://api.groq.com/openai/v1/chat/completions",
        "api_key_name": "GROQ_API_KEY",
    },
    "gemini": {
        # Placeholder - A API do Gemini pode ter uma estrutura diferente
        "api_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:streamGenerateContent",
        "api_key_name": "GEMINI_API_KEY",
    },
    "openrouter": {
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_key_name": "OPENROUTER_API_KEY",
    },
}

class ChatRequest(BaseModel):
    provider: str
    model: str
    messages: List[Dict[str, str]]
    # Adicione outros parâmetros que possam ser passados, como stream
    stream: bool = True

class TTSRequest(BaseModel):
    model: str
    voice: str
    input: str
    format: str = "mp3"


@app.post("/api/v1/chat")
async def chat_proxy(request: ChatRequest):
    provider = request.provider.lower()
    if provider not in PROVIDER_CONFIG:
        raise HTTPException(status_code=400, detail=f"Provedor '{request.provider}' não é suportado.")

    config = PROVIDER_CONFIG[provider]
    api_key = os.getenv(config["api_key_name"])

    if not api_key:
        raise HTTPException(status_code=500, detail=f"A chave de API para {provider} não está configurada no servidor.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # O corpo da solicitação para o provedor externo
    payload = {
        "model": request.model,
        "messages": request.messages,
        "stream": request.stream,
    }

    # A API do Gemini tem um formato de solicitação diferente
    if provider == "gemini":
        # Adapte o payload para o formato esperado pelo Gemini
        # Esta é uma implementação simplificada
        adapted_payload = {"contents": [{"parts": [{"text": m["content"]}] for m in request.messages if m["role"] == "user"}]}
        api_url = f"{config['api_url']}?key={api_key}" # Gemini usa a chave como parâmetro de consulta
        headers.pop("Authorization", None)
    else:
        api_url = config["api_url"]


    async def stream_response():
        async with httpx.AsyncClient(timeout=300) as client:
            try:
                async with client.stream("POST", api_url, json=payload, headers=headers) as response:
                    # Verifica se a solicitação para o provedor foi bem-sucedida
                    if response.status_code != 200:
                        body = await response.aread()
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=f"Erro do provedor externo: {body.decode()}"
                        )

                    # Passa os dados do stream
                    async for chunk in response.aiter_bytes():
                        yield chunk
            except httpx.RequestError as e:
                # Trata erros de conexão
                error_message = f"Não foi possível conectar ao provedor de API: {e}"
                print(error_message) # Log do erro no servidor
                # Não é possível enviar um HTTPException aqui porque o streaming já começou
                # Em vez disso, poderíamos enviar um chunk de erro formatado, se o cliente suportar
                yield f'{{"error": "{error_message}"}}'.encode()


    return StreamingResponse(stream_response(), media_type="application/x-ndjson")


# Função para dividir o texto em pedaços menores (chunks)
def chunk_text(text: str, max_length: int = 4000):
    """Divide o texto em pedaços respeitando os parágrafos."""
    parts = []
    paragraphs = text.split('\n\n')
    buffer = ""
    for para in paragraphs:
        if not para.strip():
            continue
        if len(buffer) + len(para) + 2 > max_length:
            if buffer:
                parts.append(buffer)
            # Se um único parágrafo for muito longo, ele é dividido à força
            if len(para) > max_length:
                for i in range(0, len(para), max_length):
                    parts.append(para[i:i+max_length])
                buffer = ""
            else:
                buffer = para
        else:
            buffer = f"{buffer}\n\n{para}" if buffer else para
    if buffer:
        parts.append(buffer)
    return parts

@app.post("/api/v1/tts")
async def tts_proxy(request: TTSRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="A chave de API da OpenAI (para TTS) não está configurada.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Divide o texto de entrada em chunks
    text_chunks = chunk_text(request.input)

    # Prepara o payload base, sem o 'input'
    base_payload = request.model_dump()
    base_payload.pop("input", None)

    async def stream_audio():
        async with httpx.AsyncClient(timeout=180) as client:
            for i, chunk in enumerate(text_chunks):
                payload = {**base_payload, "input": chunk}
                try:
                    response = await client.post("https://api.openai.com/v1/audio/speech", json=payload, headers=headers)

                    if response.status_code != 200:
                        error_detail = await response.aread()
                        # Log do erro no servidor e interrupção do stream
                        print(f"Erro da API de TTS da OpenAI no chunk {i}: {error_detail.decode()}")
                        # Não podemos mais enviar um HTTPException aqui
                        return

                    async for audio_chunk in response.aiter_bytes():
                        yield audio_chunk

                except httpx.RequestError as e:
                    # Log do erro e interrupção
                    print(f"Não foi possível conectar à API de TTS da OpenAI no chunk {i}: {e}")
                    return

    # O tipo de mídia é determinado pelo formato solicitado, com um padrão
    media_type = f"audio/{request.format.lower()}" if request.format else "audio/mpeg"
    return StreamingResponse(stream_audio(), media_type=media_type)


@app.get("/")
def health_check():
    return {"status": "ok"}
