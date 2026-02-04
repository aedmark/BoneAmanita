""" generate_skeleton.py - "The Map is not the Territory, but it helps." """

import os
import ast
import sys

IGNORE_LIST = {
    "generate_skeleton.py",
    "setup.py",
    "__init__.py"}

def generate_skeleton(directory=".", output_file="bone_map.py"):
    skeleton = [f'""" SYSTEM ARCHITECTURE MAP (Generated {directory}) """\n']
    try:
        files = [f for f in os.listdir(directory) if f.endswith(".py")]
    except FileNotFoundError:
        print(f"❌ Error: Directory '{directory}' not found.")
        return
    count = 0
    for filename in sorted(files):
        if filename == output_file:
            continue
        if filename in IGNORE_LIST or filename.startswith("."):
            continue
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
                tree = ast.parse(source)
            skeleton.append(f"\n# === MODULE: {filename} ===")
            has_content = False
            for node in tree.body:
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    _process_node(node, skeleton)
                    has_content = True
            if not has_content:
                skeleton.append("# (No classes or functions found)")
            count += 1
        except Exception as e:
            print(f"⚠️ Could not parse {filename}: {e}")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(skeleton))
    print(f"🗺️  Map generated: {output_file} ({count} modules mapped)")

def _process_node(node, buffer, indent=0):
    prefix = "    " * indent
    signature = ""
    if isinstance(node, ast.ClassDef):
        signature = f"class {node.name}:"
    elif isinstance(node, ast.FunctionDef):
        args = [a.arg for a in node.args.args]
        if 'self' in args: args.remove('self')
        arg_str = ", ".join(args)
        if len(arg_str) > 50: arg_str = arg_str[:47] + "..."
        signature = f"def {node.name}(self, {arg_str}):"
    buffer.append(f"{prefix}{signature}")
    doc = ast.get_docstring(node)
    if doc:
        short_doc = doc.split('\n')[0].strip()
        if short_doc:
            buffer.append(f'{prefix}    """ {short_doc} """')
    buffer.append(f"{prefix}    ...")
    if isinstance(node, ast.ClassDef):
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                _process_node(child, buffer, indent + 1)

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_skeleton(target_dir)