# Guia de Estudo Pro

O Guia de Estudo Pro é um poderoso gerador de guias de estudo, local e orientado por IA. Ele permite que os usuários criem, gerenciem e interajam com trilhas de aprendizado personalizadas sobre qualquer assunto, aproveitando o poder de grandes modelos de linguagem diretamente no navegador.

## Principais Recursos

### 1. Gerenciamento de Guias (CRUD)
- **Criar Novos Guias**: Comece facilmente um novo guia de estudo fornecendo um título. A aplicação usa IA para gerar automaticamente uma lista progressiva e específica de tópicos principais.
- **Ver Todos os Guias**: O painel principal lista todos os seus guias criados, mostrando o progresso de conclusão (porcentagem e tópicos concluídos/total).
- **Renomear e Excluir**: Controle total sobre seus guias com opções para renomeá-los ou excluí-los conforme necessário.

### 2. Geração de Conteúdo com IA
- **Geração Automática de Tópicos**: Com base no título do guia, a IA sugere uma lista de 7 a 9 tópicos de alto nível, seguindo as melhores práticas de design instrucional para garantir uma progressão lógica.
- **Geração Automática de Subtópicos**: Para cada tópico principal, a IA pode gerar uma lista mais granular de 6 a 9 subtópicos, cobrindo pré-requisitos, conceitos centrais, aplicações práticas e um miniprojeto.
- **Geração Detalhada de Aulas**: Gere uma aula completa e aprofundada para qualquer tópico ou subtópico. A aula é estruturada com objetivos de aprendizado claros, pré-requisitos, conceitos fundamentais, exemplos guiados e exercícios práticos.
- **Geração em Massa**: Economize tempo gerando todas as aulas para um guia inteiro ou um ramo específico da árvore de conhecimento de uma só vez.

### 3. Ambiente de Estudo Interativo
- **Árvore de Conhecimento**: Navegue pelo seu guia de estudo através de uma estrutura de árvore recolhível. Isso fornece uma visão geral clara de todo o currículo.
- **Acompanhamento de Conclusão de Tópicos**: Marque os tópicos como "concluídos" para acompanhar seu progresso visualmente na árvore de conhecimento.
- **Perguntas e Respostas Interativas**: Após gerar uma aula, você pode gerar perguntas de revisão. Digite sua resposta e peça para a IA avaliá-la, fornecendo feedback construtivo.

### 4. Personalização e Configuração
- **Gerenciamento de Chave de API**: Salve com segurança sua chave de API da OpenAI no armazenamento local do navegador. A chave nunca é compartilhada.
- **Seleção de Modelo**: Escolha o modelo da OpenAI que melhor se adapta às suas necessidades, tanto para conclusões de chat (ex: `gpt-4o-mini`) quanto para Text-to-Speech (ex: `gpt-4o-mini-tts`).
- **Prompts Personalizados**: Usuários avançados podem personalizar os prompts usados para gerar tópicos, subtópicos, aulas e perguntas para adaptar a saída da IA às suas necessidades específicas.
- **Troca de Tema**: Alterne entre os modos claro e escuro para uma experiência de visualização confortável.

### 5. Exportação
- **Múltiplos Formatos**: Exporte seus guias de estudo completos em vários formatos:
    - **HTML**: Uma página da web autônoma e estilizada com um índice.
    - **Markdown**: Um arquivo de texto estruturado, perfeito para anotações pessoais ou controle de versão.
    - **TXT**: Uma versão em texto simples para máxima compatibilidade.
    - **JSON**: Um despejo completo da estrutura de dados do guia, incluindo todo o conteúdo e metadados, para backup ou interoperabilidade.

### 6. Aulas em Áudio (Text-to-Speech)
- **Áudio para Download**: Gere e baixe uma versão em áudio de qualquer aula nos formatos MP3, WAV ou OGG.
- **Opções de Voz e Código**: Configure a voz do TTS e escolha se deseja incluir blocos de código na narração.

## Como Funciona

A aplicação é um único arquivo `index.html` que é executado inteiramente no seu navegador da web. Ele usa JavaScript para gerenciar o estado da aplicação, renderizar a interface do usuário e interagir com a API da OpenAI. Todos os dados, incluindo seus guias de estudo e chave de API, são armazenados localmente no `localStorage` do seu navegador. Isso garante a privacidade e torna a aplicação rápida e responsiva.

## Como Começar

1.  Abra o arquivo `index.html` em um navegador da web moderno.
2.  Navegue até a página "Configurações".
3.  Insira sua chave de API da OpenAI.
4.  Opcionalmente, configure os modelos e prompts personalizados.
5.  Volte para "Meus Guias" e clique em "Criar Novo Guia" para começar a aprender!

## Uso

A aplicação foi projetada para ser intuitiva. Aqui está um fluxo de trabalho típico:

### Criando um Guia
1.  No painel **Meus Guias**, clique no botão **Criar Novo Guia**.
2.  Insira um título para o seu assunto (ex: "História da Roma Antiga" ou "Conceitos Avançados de JavaScript").
3.  A IA irá gerar os tópicos principais e abrir a **Visão do Editor**.

### Navegando no Editor
-   **Árvore de Conhecimento** (Painel Esquerdo): Mostra a estrutura do seu guia.
    -   Clique no ícone `+` ao lado de um tópico para gerar seus subtópicos.
    -   Clique nos ícones `▸` ou `▾` para expandir ou recolher os subtópicos.
    -   Dê um duplo clique no título de qualquer tópico para renomeá-lo.
    -   Use a caixa de seleção para marcar um tópico como concluído.
-   **Área de Estudo** (Painel Direito): É aqui que você interage com o conteúdo.
    -   Selecione um tópico na árvore para visualizá-lo na área de estudo.

### Gerando e Interagindo com Aulas
1.  Com um tópico selecionado, clique em **Gerar Aula**. A IA escreverá uma aula detalhada.
2.  Assim que a aula for gerada, você pode:
    -   **Baixar Áudio**: Obtenha uma versão em áudio MP3 da aula.
    -   **Gerar Perguntas**: Crie um conjunto de perguntas de revisão com base na aula.
    -   **Avaliar Respostas**: Escreva sua resposta a uma pergunta e clique em **Avaliar Resposta** para obter feedback com tecnologia de IA.
3.  Use o botão **Gerar Aulas em Massa** para criar automaticamente aulas para todos os tópicos do guia ou de um ramo específico.

### Exportando seu Guia
-   Na Visão do Editor, use os botões de **Exportar** na barra de ferramentas superior para salvar seu guia nos formatos HTML, Markdown, TXT ou JSON.

## Autor e Contato

-   **Jailton Fonseca**
-   **Localização**: Brasil
-   **YouTube**: [www.youtube.com/@JailtonFonseca](https://www.youtube.com/@JailtonFonseca)
-   **Redes Sociais**:
    -   Instagram: [@jailton_fon](https://instagram.com/jailton_fon)
    -   Facebook: [Jailton Fonseca](https://facebook.com/jailton.fonseca.507)
    -   TikTok: [@fonsecac41](https://tiktok.com/@fonsecac41)
    -   Twitch: [fonsecac41](https://twitch.tv/fonsecac41)
