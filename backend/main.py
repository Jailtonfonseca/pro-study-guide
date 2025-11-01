import os
import httpx
import structlog
import logging
import json
import backoff
from fastapi import FastAPI, HTTPException, Request, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse, Response
from pydantic import BaseModel
from typing import List, Dict, Any, Annotated
import io
from docx import Document
from pypdf import PdfReader


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
    if not os.path.exists(API_KEYS_FILE) or os.path.getsize(API_KEYS_FILE) == 0:
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
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Funções de Lógica de Negócios ---

@backoff.on_exception(backoff.expo, httpx.RequestError, max_tries=3)
@backoff.on_exception(backoff.expo, httpx.HTTPStatusError, max_tries=3, giveup=lambda e: e.response.status_code < 500)
async def call_llm_api(provider: str, model: str, messages: List[Dict[str, str]]) -> str:
    """Função reutilizável para chamadas não-streaming à API de LLM."""
    logger = log.bind(provider=provider, model=model)

    if provider not in PROVIDER_CONFIG:
        logger.warn("unsupported_provider_in_call")
        raise HTTPException(status_code=400, detail=f"Provedor '{provider}' não suportado.")

    config = PROVIDER_CONFIG[provider]
    api_key = get_api_key(provider)
    if not api_key:
        logger.error("api_key_not_configured_in_call")
        raise HTTPException(status_code=500, detail=f"API key para {provider} não configurada.")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "stream": False}
    api_url = config["api_url"]

    async with httpx.AsyncClient(timeout=300) as client:
        try:
            response = await client.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            # A estrutura da resposta pode variar entre provedores
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                logger.warn("empty_llm_response", response_data=data)
            return content
        except httpx.HTTPStatusError as e:
            error_detail = e.response.content.decode()
            logger.error("provider_api_error_in_call", status_code=e.response.status_code, response_body=error_detail)
            raise HTTPException(status_code=e.response.status_code, detail=json.loads(error_detail))
        except httpx.RequestError as e:
            logger.error("provider_connection_error_in_call", error=str(e))
            raise HTTPException(status_code=503, detail=f"Não foi possível conectar ao provedor de API: {e}")


# --- Endpoints da API Principal ---

@app.post("/api/v1/guides/upload")
async def create_guide_from_upload(
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    job_role: Annotated[str, Form()],
    persona: Annotated[str, Form()],
    level: Annotated[str, Form()],
    context: Annotated[str, Form()],
    objective: Annotated[str, Form()],
    seedTopics: Annotated[str, Form()],
):
    """
    Recebe um arquivo (edital) e metadados para criar um novo guia de estudos.
    """
    logger = log.bind(filename=file.filename, title=title, job_role=job_role)
    logger.info("guide_upload_received")

    content = await file.read()
    text = ""
    try:
        if file.content_type == "application/pdf":
            reader = PdfReader(io.BytesIO(content))
            text = "".join(page.extract_text() for page in reader.pages)
        elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(io.BytesIO(content))
            text = "\n".join(para.text for para in doc.paragraphs)
        else:
            logger.warn("unsupported_file_type", content_type=file.content_type)
            raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado. Use PDF ou DOCX.")

        if not text.strip():
            logger.warn("empty_file_content")
            raise HTTPException(status_code=400, detail="O arquivo parece estar vazio ou o texto não pôde ser extraído.")

    except Exception as e:
        logger.error("file_processing_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo: {e}")

    logger.info("file_text_extracted", text_length=len(text))

    # --- Estratégia de Resumo Inteligente ---
    CONTEXT_MAX_LENGTH = 15000  # Limite seguro de caracteres
    document_context = text

    if len(text) > CONTEXT_MAX_LENGTH:
        logger.info("document_too_long_for_context", text_length=len(text))

        job_role_instruction = ""
        if job_role and job_role.strip():
            job_role_instruction = (
                "\n**IMPORTANTE:** O documento pode conter informações para vários cargos. "
                f'Você DEVE focar sua análise e extração de conteúdo EXCLUSIVAMENTE no que for relevante para o cargo de: **"{job_role}"**. '
                "Ignore seções sobre outros cargos.\n"
            )

        summarization_prompt = f"""
O seguinte texto foi extraído de um documento (edital de concurso). O texto é muito longo para ser usado diretamente.
Sua tarefa é ler o texto e criar um resumo executivo focado EXCLUSIVAMENTE nos seguintes pontos:
1.  Tópicos de estudo explícitos mencionados.
2.  Pesos ou importância de cada matéria ou tópico.
3.  Critérios de avaliação ou formato das provas.
4.  Conhecimentos específicos exigidos.
{job_role_instruction}
Seja conciso e direto. O objetivo é criar um "mapa de estudos" a partir do documento.

Texto original:
---
{text[:CONTEXT_MAX_LENGTH]}
"""

        document_context = await call_llm_api(
            provider="openai",  # Usar um provedor padrão para tarefas internas
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": summarization_prompt}]
        )
        logger.info("document_summarized", original_length=len(text), summary_length=len(document_context))

    # --- Geração dos Tópicos do Guia ---
    job_role_context = ""
    if job_role and job_role.strip():
        job_role_context = f'- Cargo Alvo: "{job_role}"'

    generation_prompt = f"""
Você é um especialista em design instrucional. Sua tarefa é criar uma jornada de aprendizado coesa e progressiva a partir do documento fornecido.

**Contexto do Guia:**
- Título: "{title}"
{job_role_context}
- Perfil do Aluno: "{persona}"
- Nível: "{level}"
- Objetivo Principal: "{objective}"
- Tópicos Iniciais Sugeridos (Sementes): "{seedTopics}"

**Documento de Referência (Edital/Conteúdo):**
---
{document_context}
---

Com base em TODO o contexto fornecido (especialmente o Documento de Referência e o Cargo Alvo, se especificado), gere de 7 a 9 tópicos principais para o guia de estudos.

REGRAS DE SAÍDA:
- Liste de 7 a 9 tópicos, um por linha.
- Sem numeração, marcadores ou explicações.
- Apenas o texto do título por linha.
"""

    topic_list_str = await call_llm_api(
        provider="openai",
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": generation_prompt}]
    )

    import uuid
    topics = [{"id": str(uuid.uuid4()), "title": line, "status": "pendente", "collapsed": False, "subtopics": []} for line in topic_list_str.split('\n') if line.strip()]

    if not topics:
        logger.warn("llm_failed_to_generate_topics")
        raise HTTPException(status_code=500, detail="A IA não conseguiu gerar os tópicos a partir do documento.")

    new_guide = {
        "id": str(uuid.uuid4()),
        "title": title,
        "persona": persona,
        "level": level,
        "context": context,
        "objective": objective,
        "seedTopics": seedTopics.split('\n') if seedTopics else [],
        "topics": topics
    }
    return new_guide


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

    @backoff.on_exception(backoff.expo, httpx.RequestError, max_tries=3)
    @backoff.on_exception(backoff.expo, httpx.HTTPStatusError, max_tries=3, giveup=lambda e: e.response.status_code < 500)
    async def stream_response():
        async with httpx.AsyncClient(timeout=300) as client:
            try:
                async with client.stream("POST", api_url, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_bytes():
                        yield chunk
            except httpx.HTTPStatusError as e:
                error_detail = f"Error {e.response.status_code}"
                try:
                    body = await e.response.aread()
                    error_detail = body.decode()
                    logger.error("provider_api_error", status_code=e.response.status_code, response_body=error_detail)
                except httpx.StreamClosed:
                    logger.error("provider_stream_closed_unexpectedly", status_code=e.response.status_code)
                    error_detail = f"A conexão com o provedor foi fechada inesperadamente (Status: {e.response.status_code})."

                yield f'{{"error": "PROVIDER_ERROR", "status_code": {e.response.status_code}, "detail": {json.dumps(error_detail)}}}'
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

    @backoff.on_exception(backoff.expo, httpx.RequestError, max_tries=3)
    @backoff.on_exception(backoff.expo, httpx.HTTPStatusError, max_tries=3, giveup=lambda e: e.response.status_code < 500)
    async def stream_audio():
        async with httpx.AsyncClient(timeout=180) as client:
            for i, chunk in enumerate(text_chunks):
                payload = {**base_payload, "input": chunk}
                try:
                    response = await client.post("https://api.openai.com/v1/audio/speech", json=payload, headers=headers)
                    response.raise_for_status()
                    async for audio_chunk in response.aiter_bytes():
                        yield audio_chunk
                except httpx.HTTPStatusError as e:
                    error_detail = e.response.content.decode()
                    logger.error("openai_tts_api_error", chunk_index=i, status_code=e.response.status_code, response_body=error_detail)
                    return
                except httpx.RequestError as e:
                    logger.error("openai_tts_connection_error", chunk_index=i, error=str(e))
                    return

    media_type = f"audio/{request.format.lower()}" if request.format else "audio/mpeg"
    return StreamingResponse(stream_audio(), media_type=media_type)

@app.get("/")
def health_check():
    log.info("health_check_called")
    return {"status": "ok"}
