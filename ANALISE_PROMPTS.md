# Análise e Otimização dos Prompts

Este documento detalha a análise dos prompts de geração de conteúdo e propõe novas versões otimizadas para gerar guias de estudo mais completos, densos em informação e com menos redundância.

## 1. Análise dos Problemas Atuais

Com base no feedback, os problemas principais com a geração de conteúdo são:

1.  **Falta de Completude:**
    *   As aulas focam estritamente no tópico solicitado, deixando de fora conceitos "vizinhos" ou relacionados que são cruciais para um entendimento completo.
    *   A estrutura de tópicos, embora progressiva, nem sempre cria uma narrativa de aprendizado coesa, com um tópico levando logicamente ao outro.
2.  **Redundância e Informação Desnecessária:**
    *   A estrutura do prompt de aula (`lesson`) força a IA a preencher várias seções (Introdução, Pré-requisitos, Resumo, Próximos Passos), o que frequentemente leva à repetição da mesma informação com palavras diferentes.
    *   Os tópicos e subtópicos podem, por vezes, ser genéricos ou se sobrepor, resultando em conteúdo repetido em diferentes partes do guia.

O objetivo da otimização é instruir a IA a ser ao mesmo tempo **mais expansiva no escopo** e **mais concisa na entrega**.

---

## 2. Proposta de Novos Prompts

A seguir estão as novas versões para cada prompt, com a justificativa da mudança.

### 2.1. Prompt: Tópicos Principais (`topTopics`)

**Objetivo da Mudança:** Forçar a criação de uma "jornada de aprendizado" mais coesa e garantir que o escopo seja abrangente desde o início.

**Nova Versão:**
```
Você é um especialista em design instrucional. Crie uma jornada de aprendizado coesa e progressiva para o guia: "{{guideTitle}}".

PRINCÍPIOS:
- **Conectividade:** Cada tópico deve construir sobre o anterior e preparar para o próximo. A sequência deve contar uma história de aprendizado.
- **Abrangência:** A trilha deve cobrir não apenas o caminho feliz, mas também os porquês, as alternativas e as implicações práticas.
- **Zero Redundância:** Evite tópicos genéricos ("Introdução", "Fundamentos", "Conceitos Avançados"). Cada título deve prometer um conhecimento único e específico.

REQUISITOS POR TÓPICO:
- Título autoexplicativo (70–110 caracteres).
- Formato sugerido: Conceito/Ferramenta → Ação/Aplicação → Contexto/Resultado.

REGRAS DE SAÍDA:
- Liste de 7 a 9 tópicos, um por linha.
- Sem numeração, marcadores ou explicações.
- Apenas o texto do título por linha.
```

**Justificativa:** A introdução de "PRINCÍPIOS" como "Conectividade" e "Abrangência" instrui a IA a pensar de forma mais holística sobre a estrutura do guia. A regra "Zero Redundância" é mais explícita.

### 2.2. Prompt: Subtópicos (`subtopics`)

**Objetivo da Mudança:** Aumentar a densidade de informação em cada subtópico e garantir que eles cubram diferentes facetas do tópico principal.

**Nova Versão:**
```
No guia "{{guideTitle}}", detalhe o tópico "{{mainTopic}}" em 6 a 9 subtópicos essenciais.

PRINCÍPIOS:
- **Diversidade de Perspectivas:** A sequência deve incluir o "o quê" (conceito), o "como" (aplicação prática), o "porquê" (contexto e design), e o "e se" (armadilhas e casos de borda).
- **Foco em Resultados:** Cada subtópico deve levar a um aprendizado mensurável ou a uma habilidade prática.
- **Progressão Lógica:** Comece com o conhecimento fundamental e avance para a aplicação, integração e otimização.

REQUISITOS POR SUBTÓPICO:
- Título orientado à ação ou a um conceito claro (60–100 caracteres).
- A sequência DEVE incluir: um item de configuração/diagnóstico, múltiplos itens de aplicação central, um item de aprofundamento teórico, um item sobre segurança/boas práticas, e finalizar com um mini-projeto prático.

REGRAS DE SAÍDA:
- Um subtópico por linha.
- Sem numeração ou explicações.
```

**Justificativa:** A instrução para incluir "Diversidade de Perspectivas" força a IA a gerar um conteúdo mais rico. A regra sobre a estrutura da sequência (configuração, aplicação, teoria, etc.) garante que o guia seja mais completo e bem-arredondado.

### 2.3. Prompt: Aula (`lesson`)

**Objetivo da Mudança:** Esta é a mudança mais significativa. O objetivo é eliminar a estrutura rígida e repetitiva, substituindo-a por um fluxo de texto mais natural e denso, como um capítulo de livro bem escrito.

**Nova Versão:**
```
Você é um professor especialista e um escritor técnico excepcional. Sua tarefa é escrever uma aula sobre "{{topicTitle}}".

PRINCÍPIOS:
- **Didática e Clareza:** Explique conceitos complexos de forma simples e intuitiva, usando analogias e exemplos claros.
- **Densidade de Informação:** Vá direto ao ponto. Evite preenchimento e repetições. Cada parágrafo deve introduzir uma nova informação ou aprofundar a anterior.
- **Contexto é Rei:** Não explique apenas "o quê", mas "porquê" e "quando". Conecte o tópico atual com conhecimentos prévios e futuros na trilha de aprendizado.

ESTRUTURA DA AULA:
1.  **Título Principal:** Comece com `<h2>{{topicTitle}}</h2>`.
2.  **Parágrafo Introdutório:** Uma introdução concisa que define o tópico e sua importância prática.
3.  **Desenvolvimento do Conteúdo:**
    *   Use `<h3>` para as seções principais.
    *   Explique os conceitos fundamentais de forma fluida.
    *   **Crucial:** Integre naturalmente a discussão de **conceitos relacionados, pré-requisitos e casos de uso** diretamente no texto, em vez de isolá-los em seções separadas.
    *   Inclua pelo menos um exemplo de código prático dentro de um bloco `<pre><code>`, explicando cada parte.
4.  **Seção de Boas Práticas e Armadilhas:** Use um `<h3>` para criar uma seção final que resuma 3 a 5 dicas práticas ou erros comuns a serem evitados.
5.  **Conclusão Concisa:** Finalize com um único parágrafo que resume o aprendizado e aponta para o próximo tópico da jornada.

REGRAS DE FORMATAÇÃO:
- Use apenas as seguintes tags HTML: `<h2>`, `<h3>`, `<p>`, `<ul>`, `<ol>`, `<li>`, `<strong>`, `<em>`, `<code>`, `<pre>`, `<br>`.
- Não use `<a>`, `<img>` ou qualquer estilo inline.
- Responda apenas com o HTML da aula, sem explicações ou cercas de código.
```

**Justificativa:**
- **Eliminação de Redundância:** A remoção das seções "Objetivos", "Pré-requisitos" e "Resumo" e a instrução para integrá-las "naturalmente no texto" é a principal mudança para combater a repetição.
- **Foco na Densidade:** A instrução "Vá direto ao ponto. Cada parágrafo deve introduzir uma nova informação" incentiva um conteúdo mais rico.
- **Conteúdo Mais Completo:** A regra "Integre naturalmente a discussão de conceitos relacionados" garante que a aula seja mais abrangente.

### 2.4. Prompt: Questões (`questions`)

Nenhuma alteração é necessária. O prompt atual já é eficaz para gerar perguntas de revisão relevantes.
```
Gere 3 PERGUNTAS DE REVISÃO que cubram: (1) conceito fundamental, (2) aplicação prática, (3) aprofundamento/armadilha comum, com base na aula a seguir.

Regras:
- Responda com UMA pergunta por linha.
- Cada linha deve começar com "P: ".
- Sem respostas, sem explicações extras.

AULA:
{{lessonContent}}
```

---

## 3. Próximos Passos

Os novos prompts propostos acima devem ser implementados no arquivo `frontend/index.html`, substituindo os valores existentes na constante `DEFAULT_PROMPT_TEMPLATES`. Após a implementação, é recomendado gerar alguns guias de teste para validar a melhoria na qualidade do conteúdo.
