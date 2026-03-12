import os
import shutil
from datetime import datetime
from collections import defaultdict
import math

# Configuration
TARGET_DIR = r"D:"
SKIP_DIRS = {'.git', 'node_modules', '.vscode', '__pycache__', 'chroma_db', 'faiss_db', 'Playground', '$RECYCLE.BIN', 'System Volume Information'}

# Categories
FILE_TYPES = {
    "Imagens": {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'},
    "Documentos": {'.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls', '.pptx', '.csv', '.md'},
    "Arquivos Compactados": {'.zip', '.rar', '.7z', '.tar', '.gz'},
    "Executáveis": {'.exe', '.msi', '.bat', '.ps1'},
    "Código": {'.py', '.js', '.html', '.css', '.java', '.cpp', '.json', '.xml'},
    "Vídeos": {'.mp4', '.mkv', '.avi', '.mov'},
    "Áudio": {'.mp3', '.wav', '.flac'}
}

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def scan_files(directory):
    stats = defaultdict(lambda: {'count': 0, 'size': 0, 'files': []})
    total_size = 0
    total_files = 0

    print(f"--- Iniciando Varredura em: {directory} ---\n")

    for root, dirs, files in os.walk(directory):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            
            try:
                size = os.path.getsize(file_path)
                total_size += size
                total_files += 1
                
                # Determine Category
                category = "Outros"
                for cat, extensions in FILE_TYPES.items():
                    if ext in extensions:
                        category = cat
                        break
                
                stats[category]['count'] += 1
                stats[category]['size'] += size
                # stats[category]['files'].append(file) # Uncomment to list all files (too verbose for CLI)
                
            except Exception as e:
                pass # Permission issues etc.

    return stats, total_files, total_size

def print_report(stats, total_files, total_size):
    print(f"{'CATEGORIA':<25} | {'ARQUIVOS':<10} | {'TAMANHO':<10}")
    print("-" * 50)
    
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['size'], reverse=True)
    
    for category, data in sorted_stats:
        print(f"{category:<25} | {data['count']:<10} | {convert_size(data['size']):<10}")
    
    print("-" * 50)
    print(f"TOTAL: {total_files} arquivos | {convert_size(total_size)}")

def main():
    if not os.path.exists(TARGET_DIR):
        print(f"Diretório não encontrado: {TARGET_DIR}")
        return

    stats, total_files, total_size = scan_files(TARGET_DIR)
    print_report(stats, total_files, total_size)
    
    print("\nSUGESTÃO DE ORGANIZAÇÃO:")
    print("Para mover os arquivos automaticamente para pastas organizadas por tipo,")
    print("eu posso atualizar este script para executar a ação de 'mover'.")

if __name__ == "__main__":
    main()
