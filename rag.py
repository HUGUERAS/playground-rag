import os
import glob
import argparse
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Configuration
DEFAULT_DOCUMENTS_PATH = r"D:\RAG_DATA"
EMBEDDING_MODEL = "nomic-embed-text:latest"
LLM_MODEL = "qwen3:8b"
PERSIST_DIRECTORY = r"C:\Users\User\Documents\Playground\faiss_db"
CHAT_PERSIST_DIRECTORY = r"C:\Users\User\Documents\Playground\faiss_db_chats"
TEXT_EXTENSIONS = {
    ".pdf", ".txt", ".md", ".rst", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".log", ".csv", ".xml", ".html", ".css", ".js", ".jsx", ".ts", ".tsx", ".py", ".ps1", ".sh", ".bat", ".cmd",
    ".sql", ".kml", ".qmd",
}
IMPORTANT_FILENAMES = {
    "workspace.json", "state.json", "entries.json", "sessions.json", "chatInteraction.jsonl", "toolUsage.jsonl",
    "editInteraction.jsonl", "tokensGenerated.jsonl", "continue.sessions.bin",
}
CHAT_HINT_TOKENS = [
    "chat",
    "session",
    "history",
    "conversation",
    "copilot",
    "continue",
    "agent-",
    "toolu_",
    "interaction",
]
SKIP_PATH_TOKENS = [
    "\\node_modules\\",
    "\\.venv\\",
    "\\venv\\",
    "\\site-packages\\",
    "\\__pycache__\\",
    "\\dist\\",
    "\\build\\",
    "\\cache\\",
    "\\extensions\\",
    "\\ms-playwright\\",
    "\\playwright\\",
    "\\.git\\",
]
SOURCE_RULES = [
    # Continue
    (r"C:\Users\User\.continue\sessions", None),
    (r"C:\Users\User\.continue\dev_data", None),
    # Copilot / VS Code
    (r"C:\Users\User\AppData\Roaming\Code\User\globalStorage\github.copilot-chat", None),
    (r"C:\Users\User\AppData\Roaming\Code\User\globalStorage\continue.continue", None),
    (r"C:\Users\User\AppData\Roaming\Code\User\globalStorage\emptyWindowChatSessions", None),
    (r"C:\Users\User\AppData\Roaming\Code\User\workspaceStorage", ["GitHub.copilot-chat\\chat-session-resources", "github.copilot-chat"]),
    # Cursor
    (r"C:\Users\User\AppData\Roaming\Cursor\User\globalStorage", None),
    (r"C:\Users\User\AppData\Roaming\Cursor\User\workspaceStorage", ["chat-session-resources", "github.copilot-chat", "workspace.json", "state.json"]),
    # Codex / Antigravity / Claude
    (r"C:\Users\User\.codex", None),
    (r"C:\Users\User\.gemini\antigravity", ["brain", "scratch", "chat", "session"]),
    (r"C:\Users\User\.claude", None),
    (r"C:\Users\User\AppData\Roaming\Claude", None),
    (r"C:\Users\User\AppData\Local\Claude", ["session", "chat", "history"]),
]


def get_documents_path():
    """Prioriza a coleta consolidada mais recente, com fallback para D:\\RAG_DATA."""
    candidates = sorted(
        glob.glob(r"D:\\PROGRAMACAO_COLETA_*"),
        key=os.path.getmtime,
        reverse=True,
    )
    if candidates:
        return candidates[0]
    return DEFAULT_DOCUMENTS_PATH


def get_source_rules(chats_only=False):
    """Monta fontes ativas: coleta + regras por origem de histórico."""
    rules = []
    if not chats_only:
        rules.append((get_documents_path(), None))
    for path, include_tokens in SOURCE_RULES:
        if os.path.exists(path):
            rules.append((path, include_tokens))
    return rules


def should_include_file(file_path: str, include_tokens, chats_only=False):
    file_name = os.path.basename(file_path)
    ext = Path(file_path).suffix.lower()
    lower_path = file_path.lower()

    if any(token in lower_path for token in SKIP_PATH_TOKENS):
        return False

    if include_tokens:
        # Quando há regra de filtro por origem, só inclui caminhos realmente relacionados.
        token_hit = any(token.lower() in lower_path for token in include_tokens)
        if not token_hit and file_name not in IMPORTANT_FILENAMES:
            return False
    elif chats_only:
        # Em chats-only, quando a fonte nao tem token explicito, exige indício de conversa.
        chat_hint_hit = any(token in lower_path for token in CHAT_HINT_TOKENS)
        if not chat_hint_hit and file_name not in IMPORTANT_FILENAMES:
            return False

    if ext in TEXT_EXTENSIONS or file_name in IMPORTANT_FILENAMES:
        return True

    return False


def load_documents(source_rules, chats_only=False):
    """Carrega arquivos textuais/código de múltiplas pastas de origem."""
    documents = []
    loaded_files = set()
    loaded_count = 0
    skipped_count = 0
    error_count = 0

    for source, include_tokens in source_rules:
        print(f"Varrendo pasta: {source}")
        files = glob.glob(os.path.join(source, "**", "*"), recursive=True)
        for file_path in files:
            if not os.path.isfile(file_path):
                continue
            if file_path in loaded_files:
                continue
            if not should_include_file(file_path, include_tokens, chats_only=chats_only):
                skipped_count += 1
                continue
            loaded_files.add(file_path)

            try:
                if file_path.lower().endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                else:
                    # Tenta carregar qualquer arquivo textual; binários serão ignorados no except.
                    loader = TextLoader(file_path, encoding='utf-8', autodetect_encoding=True)

                docs = loader.load()
                documents.extend(docs)
                print(f"Carregado: {os.path.basename(file_path)}")
                loaded_count += 1
            except Exception as e:
                print(f"Erro ao carregar {file_path}: {e}")
                error_count += 1

    print(
        f"Resumo ingestao: carregados={loaded_count}, pulados={skipped_count}, erros={error_count}"
    )
            
    return documents

def split_text(documents):
    """Divide os documentos em pedaços menores (chunks)."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Documentos divididos em {len(chunks)} pedaços.")
    if not chunks:
        print("Aviso: Nenhum texto foi extraído dos PDFs. Verifique se são arquivos digitalizados (imagens) ou vetoriais sem texto selecionável.")
    return chunks

def setup_rag(reindex=False, chats_only=False):
    print("Iniciando configuração do RAG...")
    source_rules = get_source_rules(chats_only=chats_only)
    print(f"Total de fontes ativas: {len(source_rules)}")

    persist_directory = CHAT_PERSIST_DIRECTORY if chats_only else PERSIST_DIRECTORY

    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    faiss_index_file = os.path.join(persist_directory, "index.faiss")
    if (not reindex) and os.path.exists(faiss_index_file):
        print(f"Carregando índice FAISS existente: {persist_directory}")
        vector_store = FAISS.load_local(
            persist_directory,
            embeddings,
            allow_dangerous_deserialization=True,
        )
    else:
        # 1. Load Documents
        docs = load_documents(source_rules, chats_only=chats_only)
        if not docs:
            print("Nenhum documento encontrado.")
            return
    
        # 2. Split Text
        chunks = split_text(docs)
        
        if not chunks:
            print("Impossível continuar sem texto para indexar.")
            return

        # 3. Create Embeddings & Vector Store
        print("Gerando embeddings e indexando no FAISS (isso pode demorar)...")
        vector_store = FAISS.from_documents(chunks, embeddings)
        os.makedirs(persist_directory, exist_ok=True)
        vector_store.save_local(persist_directory)
        print(f"Indexação concluída e salva em: {persist_directory}")

    # 4. Setup LLM and Retrieval Chain
    llm = ChatOllama(model=LLM_MODEL)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    system_prompt = (
        "Você é um assistente útil para responder perguntas sobre documentos técnicos de topografia e engenharia. "
        "Use os seguintes pedaços de contexto recuperado para responder à pergunta. "
        "Se você não souber a resposta, diga apenas que não sabe. "
        "Use no máximo três frases e mantenha a resposta concisa.\n\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    return rag_chain

def main():
    parser = argparse.ArgumentParser(description="RAG local com FAISS + Ollama")
    parser.add_argument(
        "--reindex",
        action="store_true",
        help="Forca a recriacao do indice FAISS a partir dos documentos",
    )
    parser.add_argument(
        "--chats-only",
        action="store_true",
        help="Indexa apenas conversas/historicos (sem base de documentos coletados)",
    )
    args = parser.parse_args()

    rag_chain = setup_rag(reindex=args.reindex, chats_only=args.chats_only)
    
    if rag_chain:
        print("\nSistema RAG pronto! Digite 'sair' para encerrar.")
        while True:
            query = input("\nPergunta: ")
            if query.lower() in ["sair", "exit", "quit"]:
                break
            
            if not query.strip():
                continue

            print("Pensando...")
            result = rag_chain.invoke({"input": query})
            print(f"\nResposta: {result['answer']}")

if __name__ == "__main__":
    main()
