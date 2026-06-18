#!/usr/bin/env python3
import os
import sys
import fnmatch

# Baseline structural boundaries
DEFAULT_IGNORES = {'.git', '.svn', 'node_modules', '__pycache__', 'venv', 'env', '.DS_Store'}
BINARY_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', '.tar', '.gz', '.mp4', '.mp3', '.pyc', '.so', '.exe', '.dll'}

def parse_gitignore(repo_path):
    """Maps the negative space by reading local ignore rules."""
    ignores = list(DEFAULT_IGNORES)
    gitignore_path = os.path.join(repo_path, '.gitignore')
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Strip leading/trailing slashes for simpler matching
                    if line.startswith('/'): line = line[1:]
                    if line.endswith('/'): line = line[:-1]
                    ignores.append(line)
    return ignores

def should_ignore(file_path, ignores, base_path):
    """Calculates if a file exists inside a pruned path."""
    rel_path = os.path.relpath(file_path, base_path)
    parts = rel_path.split(os.sep)

    if any(part in DEFAULT_IGNORES for part in parts):
        return True
    if any(file_path.endswith(ext) for ext in BINARY_EXTS):
        return True

    for pattern in ignores:
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
            return True
        for i in range(1, len(parts)):
            if fnmatch.fnmatch(os.sep.join(parts[:i]), pattern):
                return True
                
    return False

def ingest_repo(repo_path, output_filename="codebase.txt"):
    """Executes the structural consolidation."""
    ignores = parse_gitignore(repo_path)
    
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write(f"DIRECTORY INGESTION: {os.path.abspath(repo_path)}\n")
        outfile.write("=" * 60 + "\n\n")
        
        for root, dirs, files in os.walk(repo_path):
            # Mutate dirs in-place to prevent os.walk from burning cycles in ignored folders
            dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignores, repo_path)]
            
            for file in files:
                file_path = os.path.join(root, file)
                if not should_ignore(file_path, ignores, repo_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(f"--- FILE: {os.path.relpath(file_path, repo_path)} ---\n")
                            outfile.write(content)
                            outfile.write("\n\n")
                    except UnicodeDecodeError:
                        # Silently drop unmapped binary data
                        continue
                        
    print(f"Consolidation complete. Output localized to: {output_filename}")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    ingest_repo(target_dir)