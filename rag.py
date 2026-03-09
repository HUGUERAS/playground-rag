import os
import glob
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Configuration
DOCUMENTS_PATH = r"D:\RAG_DATA"  # Updated to point to the collected data folder
EMBEDDING_MODEL = "nomic-embed-text:latest"
LLM_MODEL = "qwen3:8b"
PERSIST_DIRECTORY = r"C:\Users\User\Documents\Playground\chroma_db"

def load_documents():
    """Carrega arquivos PDF, TXT, MD e Código da pasta de documentos."""
    documents = []
    
    # Supported extensions and their loaders
    # Note: TextLoader works for most code/text files
    patterns = ["*.pdf", "*.txt", "*.md", "*.py", "*.js", "*.html", "*.css", "*.java", "*.cpp", "*.json", "*.xml"]
    
    print(f"Varrendo pasta: {DOCUMENTS_PATH}")

    for pattern in patterns:
        files = glob.glob(os.path.join(DOCUMENTS_PATH, pattern))
        for file_path in files:
            try:
                if file_path.endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                else:
                    # Generic text loader for code and md
                    loader = TextLoader(file_path, encoding='utf-8', autodetect_encoding=True)
                    
                docs = loader.load()
                documents.extend(docs)
                print(f"Carregado: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"Erro ao carregar {file_path}: {e}")
            
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

def setup_rag():
    print("Iniciando configuração do RAG...")
    
    # 1. Load Documents
    docs = load_documents()
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
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vector_store = FAISS.from_documents(chunks, embeddings)
    # vector_store.save_local(PERSIST_DIRECTORY) # Optional persistence
    print("Indexação concluída!")

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
    rag_chain = setup_rag()
    
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
