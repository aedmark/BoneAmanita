""" generate_context_skeleton.py """
import os
import ast
import sys
import json

# Configuration
MAX_DEPTH = 10
IGNORE_DIRS = {'.git', '__pycache__', 'venv', '.venv', 'env', 'node_modules', '.idea', '.vscode', 'build', 'dist'}
IGNORE_FILES = {'.DS_Store', 'poetry.lock', 'package-lock.json'}
OUTPUT_FILE = "bone_skeleton.txt"

def generate_skeleton(directory=".", output_file=OUTPUT_FILE):
    """
    Generates a high-fidelity context map of the codebase for LLM ingestion.
    """
    skeleton_buffer = [f"<codebase_context root='{os.path.abspath(directory)}'>", "", "\n"]

    # Header for the LLM

    total_files = 0

    for root, dirs, files in os.walk(directory):
        # Filter directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for filename in sorted(files):
            if filename in IGNORE_FILES or filename == output_file or filename == os.path.basename(__file__):
                continue

            file_path = os.path.join(root, filename)
            rel_path = os.path.relpath(file_path, directory)

            # 1. Process Python Files
            if filename.endswith(".py"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)
                    visitor = SkeletonVisitor()
                    visitor.visit(tree)

                    skeleton_buffer.append(f'<file path="{rel_path}">')
                    skeleton_buffer.append(visitor.get_output().strip())
                    skeleton_buffer.append(f'</file>\n')
                    total_files += 1
                except Exception as e:
                    skeleton_buffer.append(f"\n")

            # 2. Process JSON Files (Data Spores)
            elif filename.endswith(".json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    skeleton_buffer.append(f'<data_file path="{rel_path}">')
                    schema = _skeletonize_data(data)
                    skeleton_buffer.append(json.dumps(schema, indent=2))
                    skeleton_buffer.append(f'</data_file>\n')
                    total_files += 1
                except Exception as e:
                    skeleton_buffer.append(f"\n")

    skeleton_buffer.append("</codebase_context>")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(skeleton_buffer))

    print(f"🗺️  Context Map generated: {output_file}")
    print(f"📉  Processed {total_files} files.")

def _skeletonize_data(data, depth=0):
    """ Creates a schema summary of JSON data to save tokens. """
    if depth > 5:
        return "..."
    if isinstance(data, dict):
        return {k: _skeletonize_data(v, depth + 1) for k, v in data.items()}
    elif isinstance(data, list):
        if not data:
            return []
        sample = _skeletonize_data(data[0], depth + 1)
        if len(data) > 1:
            return [sample, f"... ({len(data)-1} more items)"]
        return [sample]
    else:
        return str(type(data).__name__)

class SkeletonVisitor(ast.NodeVisitor):
    def __init__(self):
        self.buffer = []
        self.indent_level = 0

    def get_output(self):
        return "".join(self.buffer)

    def _indent(self):
        return "    " * self.indent_level

    def _write(self, text):
        self.buffer.append(f"{self._indent()}{text}\n")

    def visit_Import(self, node):
        """ Capture standard imports. """
        names = [n.name + (f" as {n.asname}" if n.asname else "") for n in node.names]
        self._write(f"import {', '.join(names)}")

    def visit_ImportFrom(self, node):
        """ Capture from-imports. """
        module = node.module or "."
        names = [n.name + (f" as {n.asname}" if n.asname else "") for n in node.names]
        self._write(f"from {module} import {', '.join(names)}")

    def visit_Assign(self, node):
        """ Capture top-level constants (e.g. CONFIG_VAR = ...). """
        if self.indent_level == 0:
            # We only care about global assignments
            targets = []
            for t in node.targets:
                if isinstance(t, ast.Name):
                    targets.append(t.id)

            if targets:
                # Basic heuristic: capture if it looks like a constant or config
                target_str = ", ".join(targets)
                # If the value is simple (str/num/bool), show it. Otherwise show '...'
                try:
                    if sys.version_info >= (3, 9):
                        value_repr = ast.unparse(node.value)
                    else:
                        value_repr = "..." # Fallback for older python

                    # Truncate long values
                    if len(value_repr) > 80:
                        value_repr = value_repr[:77] + "..."

                    self._write(f"{target_str} = {value_repr}")
                except:
                    self._write(f"{target_str} = ...")

    def visit_ClassDef(self, node):
        bases = [self._get_name(b) for b in node.bases]
        bases_str = f"({', '.join(bases)})" if bases else ""
        self._write(f"class {node.name}{bases_str}:")
        self.indent_level += 1

        doc = ast.get_docstring(node)
        if doc:
            self._write(f'""" {doc.strip().splitlines()[0]} ... """')

        # Only visit body items that define structure (methods, nested classes)
        has_content = False
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.visit(item)
                has_content = True
            elif isinstance(item, ast.AnnAssign):
                # Capture typed fields in classes (e.g. dataclasses)
                target = self._get_name(item.target)
                annotation = self._get_name(item.annotation)
                self._write(f"{target}: {annotation}")
                has_content = True

        if not has_content:
            self._write("...")

        self.indent_level -= 1

    def visit_FunctionDef(self, node):
        self._process_function(node)

    def visit_AsyncFunctionDef(self, node):
        self._process_function(node, is_async=True)

    def _process_function(self, node, is_async=False):
        decorators = []
        for d in node.decorator_list:
            decorators.append(f"@{self._get_name(d)}")

        for dec in decorators:
            self._write(dec)

        prefix = "async " if is_async else ""
        args = self._get_args(node)
        returns = f" -> {self._get_name(node.returns)}" if node.returns else ""

        self._write(f"{prefix}def {node.name}({args}){returns}:")
        self.indent_level += 1

        doc = ast.get_docstring(node)
        if doc:
            self._write(f'""" {doc.strip().splitlines()[0]} ... """')

        self._write("...")
        self.indent_level -= 1

    @staticmethod
    def _get_args(node):
        """ Extract arguments ensuring compatibility. """
        if sys.version_info >= (3, 9):
            return ast.unparse(node.args)
        # Simple fallback for older python
        else:
            return "..."

    @staticmethod
    def _get_name(node):
        """ Helper to get string representation of an AST node. """
        if sys.version_info >= (3, 9):
            return ast.unparse(node)
        elif isinstance(node, ast.Name):
            return node.id
        else:
            return "..."

if __name__ == "__main__":
    generate_skeleton()
