import os
import shutil
from datetime import datetime
from collections import defaultdict
import math

# --- Configuration ---
SOURCE_DIR = r"D:"
TARGET_ROOT = r"D:\ORGANIZADOS"  # New base folder
RAG_DATA_DIR = r"D:\RAG_DATA"    # Dedicated folder for RAG indexing
SKIP_DIRS = {'.git', 'node_modules', '.vscode', '__pycache__', 'chroma_db', 'faiss_db', 'Playground', '$RECYCLE.BIN', 'System Volume Information', 'ORGANIZADOS', 'RAG_DATA', 'WindowsApps', 'Program Files'}

# --- Organization Rules ---
# Format: "Category Name": {set of extensions}
FILE_TYPES = {
    "IMAGENS": {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff', '.ico'},
    "VIDEOS": {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'},
    "AUDIO": {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'},
    "DOCUMENTOS": {'.pdf', '.docx', '.doc', '.txt', '.rtf', '.odt', '.wpd'},
    "PLANILHAS": {'.xlsx', '.xls', '.csv', '.ods'},
    "APRESENTACOES": {'.pptx', '.ppt', '.odp'},
    "COMPACTADOS": {'.zip', '.rar', '.7z', '.tar', '.gz', '.iso'},
    "EXECUTAVEIS": {'.exe', '.msi', '.bat', '.ps1', '.cmd'},
    "CODIGOS": {'.py', '.js', '.html', '.css', '.java', '.cpp', '.json', '.xml', '.php', '.ts'},
    "FONTES": {'.ttf', '.otf', '.woff', '.woff2'},
    "BANCOS_DADOS": {'.sql', '.db', '.sqlite', '.mdb'}
}

def get_category(ext):
    for category, extensions in FILE_TYPES.items():
        if ext in extensions:
            return category
    return "OUTROS"

def organize_files(source_dir, dry_run=True):
    print(f"--- Organizando D: -> {TARGET_ROOT} (RAG -> {RAG_DATA_DIR}) (Dry Run: {dry_run}) ---\n")
    
    moved_count = 0
    copied_rag_count = 0
    errors = 0
    
    # Create target roots if not dry run
    if not dry_run:
        for d in [TARGET_ROOT, RAG_DATA_DIR]:
            if not os.path.exists(d):
                try:
                    os.makedirs(d)
                except Exception as e:
                    print(f"Erro ao criar pasta {d}: {e}")
                    return

    # Walk through source directory
    for root, dirs, files in os.walk(source_dir):
        # Prevent scanning targets or system folders
        if root.startswith(TARGET_ROOT) or root.startswith(RAG_DATA_DIR):
            continue
            
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for file in files:
            source_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            
            category = get_category(ext)
            
            # Special logic for RAG: COPY code and MD files to RAG_DATA
            if category in ["CODIGOS", "DOCUMENTOS"] or ext == '.md':
                rag_dest_path = os.path.join(RAG_DATA_DIR, file)
                # Handle duplicates for RAG copy
                if os.path.exists(rag_dest_path) and source_path != rag_dest_path:
                    base, extension = os.path.splitext(file)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    rag_dest_path = os.path.join(RAG_DATA_DIR, f"{base}_{timestamp}{extension}")
                
                try:
                    if dry_run:
                        print(f"[SIMULACAO] Copiar p/ RAG: {source_path} -> {rag_dest_path}")
                    else:
                        shutil.copy2(source_path, rag_dest_path)
                        print(f"[COPIADO RAG] {file}")
                    copied_rag_count += 1
                except Exception as e:
                    print(f"[ERRO RAG] Falha ao copiar {file}: {e}")

            # Standard Move Logic (skip if already handled or specialized)
            # ... (rest of move logic remains similar but simplified for this context)
            
            # Define destination path for MOVE
            dest_dir = os.path.join(TARGET_ROOT, category)
            dest_path = os.path.join(dest_dir, file)
            
            # Handle duplicates (simple rename)
            if os.path.exists(dest_path) and source_path != dest_path:
                base, extension = os.path.splitext(file)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = f"{base}_{timestamp}{extension}"
                dest_path = os.path.join(dest_dir, new_filename)
            
            try:
                if dry_run:
                    print(f"[SIMULACAO] Mover: {source_path} -> {dest_path}")
                else:
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    shutil.move(source_path, dest_path)
                    print(f"[MOVIDO] {file} -> {category}")
                
                moved_count += 1
                
            except Exception as e:
                print(f"[ERRO] Falha ao mover {file}: {e}")
                errors += 1

    print(f"\n--- Concluído ---")
    print(f"Arquivos movidos (Organização): {moved_count}")
    print(f"Arquivos copiados (RAG): {copied_rag_count}")
    print(f"Erros: {errors}")
    if dry_run:
        print("\nIsso foi apenas uma SIMULAÇÃO. Nenhum arquivo foi movido.")
        print("Para executar de verdade, mude 'dry_run=True' para 'dry_run=False' no script.")

if __name__ == "__main__":
    # Change dry_run to False to actually move files
    organize_files(SOURCE_DIR, dry_run=False)
