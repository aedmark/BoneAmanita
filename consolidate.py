import os
import glob


def consolidate_python_to_markdown(output_filename="notebook_lm_source.md"):
    """
    Scans the current working directory for all .py files and concatenates them
    into a single Markdown file optimized for NotebookLM ingestion.
    """
    # Map the perimeter: Find all .py files in the current directory
    py_files = glob.glob("*.py")

    # Identify self: Exclude this exact script from the output to prevent loop-holes
    script_name = os.path.basename(__file__)
    if script_name in py_files:
        py_files.remove(script_name)

    if not py_files:
        print("SYSTEM LOG: No Python files found in the current directory. Aborting.")
        return

    # Construct the foundation
    with open(output_filename, "w", encoding="utf-8") as outfile:
        outfile.write("# Python Source Code Consolidation\n\n")
        outfile.write(f"**Total files mapped:** {len(py_files)}\n\n")
        outfile.write("---\n\n")

        for file_path in py_files:
            try:
                with open(file_path, "r", encoding="utf-8") as infile:
                    content = infile.read()

                # Build the walls: Write markdown headers and protected code blocks
                outfile.write(f"## File: `{file_path}`\n\n")
                outfile.write("```python\n")
                outfile.write(content)
                if not content.endswith("\n"):
                    outfile.write("\n")
                outfile.write("```\n\n")
                outfile.write("---\n\n")
                print(f"Attached: {file_path}")

            except Exception as e:
                # Log structural fractures
                print(f"FRACTURE DETECTED reading {file_path}: {e}")
                outfile.write(f"## File: `{file_path}`\n\n")
                outfile.write(f"> **Error reading file:** {e}\n\n")
                outfile.write("---\n\n")

    print(f"\nARCHITECTURE COMPLETE. Consolidated {len(py_files)} files into '{output_filename}'")


if __name__ == "__main__":
    consolidate_python_to_markdown()