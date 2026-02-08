""" generate_skeleton.py - "The Map is not the Territory, but it helps." """
import os
import ast

def generate_skeleton(directory=".", output_file="project_skeleton.py"):
    skeleton = [f'""" PROJECT SYSTEM ARCHITECTURE (Recursive Map) """\n']
    for root, dirs, files in os.walk(directory):
        for filename in sorted(files):
            rel_path = os.path.relpath(os.path.join(root, filename), directory)
            if filename == output_file:
                continue
            if filename.endswith(".py"):
                file_path = os.path.join(root, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read())
                        skeleton.append(f"\n# === MODULE: {rel_path} ===")
                        for node in tree.body:
                            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                                _process_node(node, skeleton)
                    except Exception as e:
                        skeleton.append(f"\n# [!] Error parsing {rel_path}: {e}")
            elif filename.endswith(".json"):
                skeleton.append(f"\n# === DATA_SPORE: {rel_path} ===")
                skeleton.append(f"    # [JSON Configuration/State File]")
                skeleton.append(f"    ...")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(skeleton))
    print(f"🗺️  Recursive Map generated: {output_file}")

def _process_node(node, buffer, indent=0):
    prefix = "    " * indent
    if isinstance(node, ast.ClassDef):
        buffer.append(f"{prefix}class {node.name}:")
    elif isinstance(node, ast.FunctionDef):
        args = [a.arg for a in node.args.args]
        if 'self' in args: args.remove('self')
        arg_str = ", ".join(args)
        if len(arg_str) > 50: arg_str = "..."
        buffer.append(f"{prefix}def {node.name}(self, {arg_str}):")
    doc = ast.get_docstring(node)
    if doc:
        short_doc = doc.split('\n')[0]
        buffer.append(f'{prefix}    """ {short_doc} """')
    buffer.append(f"{prefix}    ...")
    if isinstance(node, ast.ClassDef):
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                _process_node(child, buffer, indent + 1)

if __name__ == "__main__":
    generate_skeleton()
