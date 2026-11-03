import os

OUTPUT_FILE = "project_context.txt"

# 1. Các thư mục cần bỏ qua để tránh file quá nặng hoặc bị treo
EXCLUDE_DIRS = {
    '.venv', 'venv', 'node_modules', '__pycache__', 
    '.git', '.vscode', 'build', 'dist'
}

# 2. Các định dạng file không cần gom (file nhị phân, ảnh, database, lockfile)
EXCLUDE_EXTS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', 
    '.db', '.sqlite', '.pyc', '.lock', '.exe'
}

# 3. Các file cụ thể cần bỏ qua
EXCLUDE_FILES = {
    OUTPUT_FILE, 'bundle_code.py', 'package-lock.json', 'erd.png'
}

def bundle_project():
    print("Dang quét va gom ma nguon...")
    file_count = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        # Ghi mục lục cây thư mục dự án
        outfile.write("==================================================\n")
        outfile.write("CAU TRUC THU MUC DU AN\n")
        outfile.write("==================================================\n\n")
        
        for root, dirs, files in os.walk("."):
            # Bỏ qua các thư mục không mong muốn ngay khi duyệt
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            level = root.replace(".", "").count(os.sep)
            indent = " " * 4 * level
            folder_name = os.path.basename(os.path.abspath(root))
            if root == ".":
                outfile.write("PBL4/\n")
            else:
                outfile.write(f"{indent}{folder_name}/\n")
                
            subindent = " " * 4 * (level + 1)
            for f in files:
                if not any(f.endswith(ext) for ext in EXCLUDE_EXTS) and f not in EXCLUDE_FILES:
                    outfile.write(f"{subindent}{f}\n")

        # Ghi nội dung chi tiết của từng file
        outfile.write("\n\n==================================================\n")
        outfile.write("NOI DUNG CHI TIET TUNG FILE MA NGUON\n")
        outfile.write("==================================================\n\n")
        
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if any(file.endswith(ext) for ext in EXCLUDE_EXTS) or file in EXCLUDE_FILES:
                    continue
                
                file_path = os.path.join(root, file)
                normalized_path = os.path.normpath(file_path).replace("\\", "/")
                
                outfile.write(f"\n{'='*60}\n")
                outfile.write(f"FILE: {normalized_path}\n")
                outfile.write(f"{'='*60}\n\n")
                
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
                        outfile.write(infile.read())
                    file_count += 1
                except Exception as e:
                    outfile.write(f"[Khong the doc file: {e}]\n")
                
                outfile.write("\n")

    print(f"-> Hoan tat! Da gom {file_count} file vao: {OUTPUT_FILE}")

if __name__ == "__main__":
    bundle_project()