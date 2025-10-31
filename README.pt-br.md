# Guia de Estudo Pro (Arquitetura de Microsserviços)

O Guia de Estudo Pro é uma poderosa aplicação geradora de guias de estudo, agora refatorada para uma arquitetura de microsserviços robusta, segura e pronta para produção. A aplicação permite que os usuários criem, gerenciem e interajam com trilhas de aprendizado personalizadas sobre qualquer assunto, aproveitando o poder de múltiplos provedores de LLM de forma segura.

Esta versão foi reescrita do zero para separar as responsabilidades, aumentar a segurança e facilitar a implantação.

---

## Arquitetura da Aplicação

A nova arquitetura é composta por dois serviços principais, orquestrados com Docker Compose:

1.  **Frontend**: Uma aplicação estática (HTML/CSS/JS) servida por um Nginx de alta performance. O Nginx também atua como um proxy reverso para o backend, garantindo que todas as comunicações com a API passem por ele.
2.  **Backend**: Um gateway de API seguro construído com Python e FastAPI. Ele gerencia as chaves de API, processa as solicitações do frontend e interage com os diferentes provedores de modelos de linguagem (OpenAI, Groq, etc.).

### Diagrama da Arquitetura

```mermaid
graph TD
    subgraph "Navegador do Usuário"
        A[Frontend - index.html]
    end

    subgraph "Servidor Docker"
        B[Nginx <br> Porta: 8080]
        C[Backend <br> FastAPI]

        subgraph "APIs Externas"
            D[OpenAI API]
            E[Groq API]
            F[Gemini API]
            G[OpenRouter API]
        end
    end

    A -- Requisições HTTP --> B
    B -- Serve arquivos estáticos --> A
    B -- /api/* --> C
    C -- Gerencia chaves e encaminha --> D
    C -- Gerencia chaves e encaminha --> E
    C -- Gerencia chaves e encaminha --> F
    C -- Gerencia chaves e encaminha --> G
```

---

## Principais Melhorias da Nova Versão

-   **Segurança Reforçada**: A chave de API não fica mais exposta no navegador. Todo o gerenciamento é feito no backend, que a lê de variáveis de ambiente seguras.
-   **Suporte a Múltiplos Provedores**: Selecione facilmente entre OpenAI, Groq, Gemini ou OpenRouter na interface do usuário.
-   **Arquitetura Escalável**: A separação entre frontend e backend permite que cada serviço seja escalado de forma independente.
-   **Implantação Simplificada**: Com Docker e Docker Compose, a aplicação inteira pode ser iniciada com um único comando, garantindo um ambiente de desenvolvimento e produção consistente.
-   **Sem Problemas de CORS**: O Nginx atua como um proxy reverso, eliminando a necessidade de configurações complexas de CORS.

---

## Como Começar (Setup)

Para executar o projeto, você precisará ter o **Docker** e o **Docker Compose** instalados em sua máquina.

### 1. Clone o Repositório

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
```

### 2. Configure as Chaves de API

O backend precisa das chaves de API para se comunicar com os provedores de LLM. O `docker-compose.yml` está preparado para recebê-las como variáveis de ambiente.

Crie um arquivo chamado `.env` na raiz do projeto. Este arquivo **não deve** ser enviado para o controle de versão.

```
# .env
# Adicione aqui as chaves de API para os provedores que você deseja usar.
# Você não precisa preencher todas, apenas aquelas que for utilizar.

OPENAI_API_KEY="sk-..."
GROQ_API_KEY="gsk_..."
GEMINI_API_KEY="..."
OPENROUTER_API_KEY="..."
```

O Docker Compose carregará automaticamente as variáveis deste arquivo.

### 3. Construa e Inicie os Contêineres

Com o Docker em execução, execute o seguinte comando na raiz do projeto:

```bash
docker compose up --build -d
```

-   `--build`: Força a reconstrução das imagens Docker, garantindo que as últimas alterações no código sejam aplicadas.
-   `-d`: Roda os contêineres em modo "detached" (em segundo plano).

### 4. Acesse a Aplicação

Após a conclusão do build, a aplicação estará disponível em seu navegador no seguinte endereço:

[**http://localhost:8080**](http://localhost:8080)

---

## Uso da Aplicação

1.  **Acesse a Aplicação**: Abra [http://localhost:8080](http://localhost:8080).
2.  **Vá para as Configurações**:
    -   Clique em "Configurações" na barra de navegação.
    -   **Selecione o Provedor de API** que você configurou no arquivo `.env`.
    -   **Informe o Modelo** correspondente ao provedor (ex: `gpt-4o-mini` para OpenAI, `llama3-8b-8192` para Groq).
    -   Salve as configurações.
3.  **Crie seu Guia**:
    -   Volte para "Meus Guias" e clique em "Criar Novo Guia".
    -   A aplicação usará o provedor e modelo configurados para gerar o conteúdo.

O restante dos recursos, como a geração de aulas, perguntas, exportação e download de áudio, funciona da mesma forma que na versão anterior.

---

## Parando a Aplicação

Para parar os contêineres, execute o seguinte comando na raiz do projeto:

```bash
docker compose down
```

## Autor e Contato

-   **Jailton Fonseca**
-   **Localização**: Brasil
-   **YouTube**: [www.youtube.com/@JailtonFonseca](https://www.youtube.com/@JailtonFonseca)
