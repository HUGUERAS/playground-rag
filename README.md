# Playground RAG

Este projeto implementa um sistema RAG (Retrieval-Augmented Generation) simples usando:
- Ollama (LLM e Embeddings)
- LangChain
- FAISS (Vector Store)

## O que é RAG?

O **RAG**, ou **Retrieval-Augmented Generation** (Geração Aumentada por Recuperação), é uma arquitetura de Inteligência Artificial que melhora a qualidade e a precisão das respostas de um Modelo de Linguagem Grande (LLM) conectando-o a uma base de dados externa.

**A analogia perfeita:** 
Imagine um estudante muito inteligente (o LLM). Sem o RAG, ele faz uma prova usando apenas o que decorou anos atrás. Com o RAG, o estudante faz a prova com "consulta aberta" a uma biblioteca atualizada.

### Como funciona (3 Fases)

#### FASE 1: A INGESTÃO E INDEXAÇÃO DE DADOS (A "Biblioteca")
1. **Extração e Carregamento:** Ler arquivos (PDFs, etc.) e converter em texto puro.
2. **Segmentação (Chunking):** Quebrar documentos longos em pedaços menores.
3. **Geração de Embeddings:** Converter texto em vetores numéricos (significado semântico).
4. **Banco de Dados Vetorial:** Armazenar os vetores para busca rápida.

#### FASE 2: RECUPERAÇÃO (Retrieval)
5. **Processamento da Pergunta:** Converter a pergunta do usuário em vetor.
6. **Busca por Similaridade:** Encontrar os trechos de texto mais parecidos com a pergunta.
7. **Re-ranking (Opcional):** Refinar a ordem dos resultados.

#### FASE 3: GERAÇÃO AUMENTADA (Generation)
8. **Construção do Prompt:** Juntar a pergunta com os textos recuperados.
9. **Modelo de Linguagem:** O LLM gera a resposta baseada nos dados reais fornecidos.

## Como usar este projeto

1. Instale as dependências: `pip install -r requirements.txt`
2. Coloque seus PDFs na pasta `Documents`.
3. Execute: `python rag.py`

## Documentacao GeoAdmin

O workspace agora inclui uma base documental consolidada em `geoadmin-docs/` com:

- PRD e visao do produto.
- Roadmap reorganizado por fases.
- Mapeamento funcional das telas reais do app.
- Materiais de referencia e arquivos de origem arquivados.
