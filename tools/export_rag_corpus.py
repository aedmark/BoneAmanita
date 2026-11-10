#!/usr/bin/env python3
"""
RAG Corpus Harvester & Bundler for Google NotebookLM and High-Context Models.

Formalized declarative pipeline to export any codebase into curated,
structured Markdown volumes adhering to Google NotebookLM limits (500k words/source).
Supports custom manifest configurations or automatic repository discovery.

Zero external dependencies (Python 3.10+ standard library).
"""

from __future__ import annotations

import argparse
import fnmatch
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Set, Tuple


class SimpleHTMLToMarkdown(HTMLParser):
    """Converts HTML articles into clean Markdown without external dependencies."""

    def __init__(self) -> None:
        super().__init__()
        self.text_parts: List[str] = []
        self.in_title = False
        self.in_script_or_style = False
        self.list_depth = 0

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        tag = tag.lower()
        if tag in ("script", "style"):
            self.in_script_or_style = True
            return
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.text_parts.append("\n\n# ")
        elif tag == "h2":
            self.text_parts.append("\n\n## ")
        elif tag == "h3":
            self.text_parts.append("\n\n### ")
        elif tag == "h4":
            self.text_parts.append("\n\n#### ")
        elif tag == "p":
            self.text_parts.append("\n\n")
        elif tag == "br":
            self.text_parts.append("\n")
        elif tag == "li":
            indent = "  " * (self.list_depth - 1) if self.list_depth > 1 else ""
            self.text_parts.append(f"\n{indent}- ")
        elif tag in ("ul", "ol"):
            self.list_depth += 1
        elif tag == "pre":
            self.text_parts.append("\n\n```\n")
        elif tag == "code" and self.text_parts and not self.text_parts[-1].endswith("```\n"):
            self.text_parts.append("`")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in ("script", "style"):
            self.in_script_or_style = False
            return
        if tag == "title":
            self.in_title = False
            self.text_parts.append("\n\n")
        elif tag in ("h1", "h2", "h3", "h4"):
            self.text_parts.append("\n")
        elif tag in ("ul", "ol"):
            self.list_depth = max(0, self.list_depth - 1)
        elif tag == "pre":
            self.text_parts.append("\n```\n")
        elif tag == "code" and self.text_parts and not self.text_parts[-1].endswith("```\n"):
            self.text_parts.append("`")

    def handle_data(self, data: str) -> None:
        if self.in_script_or_style:
            return
        clean = data.replace("\r", "")
        self.text_parts.append(clean)

    def get_markdown(self) -> str:
        raw = "".join(self.text_parts)
        # Collapse excessive newlines
        collapsed = re.sub(r"\n{3,}", "\n\n", raw)
        return collapsed.strip()


def html_to_markdown(html_text: str) -> str:
    parser = SimpleHTMLToMarkdown()
    parser.feed(html_text)
    return parser.get_markdown()


def glob_to_regex(pat: str) -> re.Pattern:
    """Translates standard glob patterns including recursive ** into regex."""
    i, n = 0, len(pat)
    res = []
    while i < n:
        c = pat[i]
        if c == '*':
            if i + 1 < n and pat[i + 1] == '*':
                if i + 2 < n and pat[i + 2] == '/':
                    res.append('(?:.*/)?')
                    i += 3
                    continue
                else:
                    res.append('.*')
                    i += 2
                    continue
            else:
                res.append('[^/]*')
                i += 1
                continue
        elif c == '?':
            res.append('[^/]')
            i += 1
            continue
        else:
            res.append(re.escape(c))
            i += 1
    return re.compile(f'^{"".join(res)}$')


def match_glob_patterns(rel_path: str, patterns: List[str]) -> bool:
    """Matches a relative path against a list of glob patterns supporting recursive **."""
    normalized = rel_path.replace("\\", "/")
    for pattern in patterns:
        norm_pattern = pattern.replace("\\", "/")
        try:
            rx = glob_to_regex(norm_pattern)
            if rx.match(normalized):
                return True
        except Exception:
            if fnmatch.fnmatch(normalized, norm_pattern):
                return True
    return False


def get_file_language(path: Path) -> str:
    """Maps file extension to markdown code fence language tag."""
    ext = path.suffix.lower()
    mapping = {
        ".py": "python",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".md": "markdown",
        ".html": "html",
        ".js": "javascript",
        ".ts": "typescript",
        ".css": "css",
        ".sh": "bash",
        ".bash": "bash",
        ".sql": "sql",
        ".toml": "toml",
        ".rs": "rust",
        ".go": "go",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
    }
    return mapping.get(ext, "text")


class RAGCorpusBuilder:
    """Discovers, validates, and builds RAG corpus volumes from configuration."""

    def __init__(self, repo_root: Path, config: Dict[str, Any], output_dir: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.config = config
        self.output_dir = output_dir.resolve()
        self.global_exclusions = config.get("global_exclusions", [])
        self.limits = config.get("limits", {
            "max_words_per_volume": 500000,
            "max_chars_per_volume": 3500000,
            "max_volumes": 50,
        })
        self.volume_stats: List[Dict[str, Any]] = []

    def is_globally_excluded(self, rel_path: str) -> bool:
        return match_glob_patterns(rel_path, self.global_exclusions)

    def scan_volume_files(self, volume: Dict[str, Any]) -> List[Path]:
        """Resolves all matching files for a volume in prioritized order."""
        includes = volume.get("include", [])
        excludes = volume.get("exclude", [])
        priority_files = volume.get("priority_files", [])

        matched_files: Set[Path] = set()

        # Scan repository root
        for root, dirs, files in os.walk(self.repo_root):
            rel_dir = os.path.relpath(root, self.repo_root).replace("\\", "/")
            if rel_dir == ".":
                rel_dir = ""

            # Prune excluded directories
            if rel_dir and self.is_globally_excluded(rel_dir):
                dirs[:] = []
                continue

            for f in files:
                file_path = Path(root) / f
                rel_path = os.path.relpath(file_path, self.repo_root).replace("\\", "/")

                if self.is_globally_excluded(rel_path):
                    continue
                if excludes and match_glob_patterns(rel_path, excludes):
                    continue

                if match_glob_patterns(rel_path, includes):
                    matched_files.add(file_path)

        # Sort with priority files first, followed by alphabetical relative paths
        priority_paths = [
            (self.repo_root / p).resolve()
            for p in priority_files
            if (self.repo_root / p).resolve() in matched_files
        ]

        remaining = sorted(
            [p for p in matched_files if p not in priority_paths],
            key=lambda p: str(p.relative_to(self.repo_root))
        )

        return priority_paths + remaining

    def render_file_markdown(self, file_path: Path, strip_html: bool) -> str:
        """Renders an individual file into formatted Markdown with metadata headers."""
        rel_path = str(file_path.relative_to(self.repo_root)).replace("\\", "/")
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return f"\n\n---\n# File: {rel_path}\n> ERROR READING FILE: {e}\n---\n\n"

        line_count = content.count("\n") + 1
        word_count = len(content.split())
        ext = file_path.suffix.lower()

        header = [
            "\n\n---",
            f"# File: {rel_path}",
            f"> Path: `{rel_path}` | Lines: {line_count} | Words: {word_count}",
            "---\n"
        ]

        if strip_html and ext in (".html", ".htm"):
            clean_md = html_to_markdown(content)
            body = clean_md
        elif ext == ".md":
            # Direct markdown embedding with visual delimiter
            body = content.strip()
        else:
            lang = get_file_language(file_path)
            body = f"```{lang}\n{content.strip()}\n```"

        return "\n".join(header) + "\n" + body + "\n"

    def build_volume(self, volume: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
        """Compiles a single volume into a self-contained Markdown document."""
        vol_id = volume["id"]
        title = volume["title"]
        desc = volume.get("description", "")
        strip_html = volume.get("strip_html", False)

        files = self.scan_volume_files(volume)
        parts: List[str] = []

        # Volume Header
        parts.append(f"# {title}")
        parts.append(f"\n> **Volume ID:** `{vol_id}`")
        if desc:
            parts.append(f"> **Subsystem Description:** {desc}")
        parts.append(f"> **Files Included:** {len(files)}")
        parts.append("\n## Table of Contents")
        for f in files:
            rel = str(f.relative_to(self.repo_root)).replace("\\", "/")
            parts.append(f"- [{rel}](#file-{rel.replace('/', '-').replace('.', '-')})")

        total_words = 0
        total_chars = 0
        total_lines = 0

        for f in files:
            rendered = self.render_file_markdown(f, strip_html=strip_html)
            parts.append(rendered)
            words = len(rendered.split())
            chars = len(rendered)
            lines = rendered.count("\n")
            total_words += words
            total_chars += chars
            total_lines += lines

        full_text = "\n".join(parts)
        out_filename = f"{vol_id}.md"
        out_path = self.output_dir / out_filename

        if not dry_run:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            out_path.write_text(full_text, encoding="utf-8")

        max_words = self.limits.get("max_words_per_volume", 500000)
        warning = None
        if total_words > max_words:
            warning = f"EXCEEDS NOTEBOOKLM LIMIT: {total_words} words > {max_words} words"

        stats = {
            "id": vol_id,
            "title": title,
            "filename": out_filename,
            "file_count": len(files),
            "words": total_words,
            "chars": total_chars,
            "lines": total_lines,
            "warning": warning,
            "path": str(out_path),
        }
        return stats

    def build_all(self, dry_run: bool = False) -> List[Dict[str, Any]]:
        """Builds all volumes and generates the master corpus index."""
        volumes = self.config.get("volumes", [])
        results: List[Dict[str, Any]] = []

        for vol in volumes:
            stats = self.build_volume(vol, dry_run=dry_run)
            results.append(stats)
            self.volume_stats.append(stats)

        # Generate Master Corpus Index
        if not dry_run:
            self.write_corpus_index(results)

        return results

    def write_corpus_index(self, results: List[Dict[str, Any]]) -> None:
        """Writes 00_CORPUS_INDEX.md summarizing all volumes and providing prompting guidance."""
        corpus_title = self.config.get("title", "Repository RAG Corpus")
        corpus_desc = self.config.get("description", "")
        target_sys = self.config.get("target_system", "notebooklm")

        total_files = sum(r["file_count"] for r in results)
        total_words = sum(r["words"] for r in results)
        total_chars = sum(r["chars"] for r in results)

        lines = [
            f"# {corpus_title}: Master RAG Corpus Index",
            "",
            f"> **Corpus Summary:** {corpus_desc}",
            f"> **Target System:** `{target_sys}`",
            f"> **Total Volumes:** {len(results)} | **Total Source Files:** {total_files} | **Total Word Count:** {total_words:,} words ({total_chars / 1024 / 1024:.2f} MB)",
            "",
            "## Volume Manifest",
            "",
            "| Volume File | Title | Files | Word Count | Status |",
            "| :--- | :--- | :---: | :---: | :--- |",
        ]

        for r in results:
            status = "Ready" if not r["warning"] else f"Warning: {r['warning']}"
            lines.append(f"| [`{r['filename']}`](./{r['filename']}) | {r['title']} | {r['file_count']} | {r['words']:,} | {status} |")

        lines.extend([
            "",
            "## How to Use with Google NotebookLM",
            "",
            "1. **Upload Sources:**",
            "   - Open [Google NotebookLM](https://notebooklm.google.com/) and create a new notebook.",
            "   - Click **Add Sources** -> **Upload Files**.",
            "   - Select the generated `.md` volume files from this directory.",
            "2. **Generating Audio Overviews (Deep Dive Podcast):**",
            "   - Select Volumes 1, 2, and 6 (Architecture, Somatic Biology, and Devlogs).",
            "   - In the Notebook Guide panel, click **Generate** under Audio Overview.",
            "   - Customize prompt if desired (e.g. 'Focus on how BoneAmanita replaces sycophancy with somatic boundaries and distress space holding').",
            "3. **Targeted Subsystem Inquiry:**",
            "   - Use the checkmarks beside sources to isolate specific subsystems (e.g. check only Volume 2 for ATP/cortisol mechanics, or Volume 4 for Turn Loop and Gatekeeper filters).",
            "   - Ask specific architectural questions with confidence that the LLM will ground its answers in verified code and decision records.",
            "",
            "## Volume Details and System Prompts",
            "",
        ])

        for r in results:
            vol_def = next((v for v in self.config.get("volumes", []) if v["id"] == r["id"]), {})
            desc = vol_def.get("description", "")
            lines.extend([
                f"### {r['title']} (`{r['filename']}`)",
                f"- **Description:** {desc}",
                f"- **Source Files:** {r['file_count']}",
                f"- **Word Count:** {r['words']:,}",
                f"- **Character Count:** {r['chars']:,}",
                "",
            ])

        index_path = self.output_dir / "00_CORPUS_INDEX.md"
        index_path.write_text("\n".join(lines), encoding="utf-8")


def auto_discover_repository(repo_path: Path) -> Dict[str, Any]:
    """Inspects an arbitrary codebase and derives a structured RAG volume manifest."""
    repo_name = repo_path.resolve().name
    manifest: Dict[str, Any] = {
      "$schema": "./rag_corpus.schema.json",
      "corpus_id": re.sub(r"[^a-z0-9_-]", "_", repo_name.lower()),
      "title": f"{repo_name} Repository Corpus",
      "description": f"Automated RAG corpus extracted from {repo_name} codebase.",
      "target_system": "notebooklm",
      "limits": {
        "max_words_per_volume": 500000,
        "max_chars_per_volume": 3500000,
        "max_volumes": 50,
      },
      "global_exclusions": [
        "**/.git/**",
        "**/.venv/**",
        "**/venv/**",
        "**/__pycache__/**",
        "**/*.pyc",
        "**/node_modules/**",
        "**/dist/**",
        "**/build/**",
        "**/target/**",
        "**/scratch/**",
        "**/logs/**",
        "**/saves/**",
        "**/output/**",
        "**/tmp/**",
        "**/temp/**",
        "**/cache/**",
        "**/.idea/**",
        "**/.vscode/**",
        "**/*.log",
        "**/*.db",
        "**/*.sqlite*",
        "**/*.lock",
      ],
      "volumes": []
    }

    # Detect top-level directories
    ignored_dir_names = {
        "docs", "doc", "tests", "test", "tools", "scripts", "lore",
        "config", "scratch", "logs", "saves", "output", "memories",
        "cache", "tmp", "temp", "node_modules", "target", "build", "dist",
        "test_telemetry_logs", "magicmock", "site-packages", "__pycache__",
        ".pytest_cache"
    }
    top_dirs = [d.name for d in repo_path.iterdir() if d.is_dir() and not d.name.startswith(".")]

    # 1. Documentation volume
    manifest["volumes"].append({
        "id": "01_documentation_and_architecture",
        "title": "Documentation, Architecture & Guides",
        "description": "High-level guides, architectural records, design specs, and documentation.",
        "include": ["*.md", "docs/**", "doc/**", "*.rst"],
        "priority_files": ["README.md", "docs/ARCHITECTURE.md", "docs/DECISIONS.md"]
    })

    # 2. Source code directories grouped logically
    src_dirs = [d for d in top_dirs if d.lower() not in ignored_dir_names]
    if src_dirs:
        # Group into 1 to 4 volumes depending on count
        chunk_size = max(1, len(src_dirs) // 3)
        vol_num = 2
        for i in range(0, len(src_dirs), chunk_size):
            group = src_dirs[i:i + chunk_size]
            includes = [f"{g}/**" for g in group]
            manifest["volumes"].append({
                "id": f"{vol_num:02d}_{'_'.join(group)[:30]}",
                "title": f"Source Subsystems: {', '.join(group)}",
                "description": f"Implementation code for subsystems: {', '.join(group)}.",
                "include": includes
            })
            vol_num += 1

    # 3. Configurations and factory data
    manifest["volumes"].append({
        "id": f"{len(manifest['volumes']) + 1:02d}_config_and_lore",
        "title": "Configuration, Schemas & Factory Data",
        "description": "JSON/YAML configurations, schemas, and static data dictionaries.",
        "include": ["*.json", "*.yaml", "*.yml", "*.toml", "lore/**", "config/**"]
    })

    # 4. Tests and tooling
    if (repo_path / "tests").exists() or (repo_path / "test").exists():
        manifest["volumes"].append({
            "id": f"{len(manifest['volumes']) + 1:02d}_tests_and_verification",
            "title": "Test Suites & Verification Contracts",
            "description": "Unit tests, behavioral tests, and verification test suites.",
            "include": ["tests/**", "test/**"]
        })

    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Export codebase into structured RAG/NotebookLM volumes.")
    parser.add_argument("--config", "-c", type=str, help="Path to RAG corpus manifest JSON.")
    parser.add_argument("--repo", "-r", type=str, default=".", help="Root path of target repository.")
    parser.add_argument("--output-dir", "-o", type=str, default="scratch/rag_corpus", help="Destination folder for Markdown volumes.")
    parser.add_argument("--auto", action="store_true", help="Auto-discover codebase structure for any repository.")
    parser.add_argument("--emit-config", type=str, help="Emit auto-discovered configuration to specified JSON path and exit.")
    parser.add_argument("--check", action="store_true", help="Perform dry run and report statistics without writing files.")

    args = parser.parse_args()
    repo_root = Path(args.repo).resolve()
    out_dir = Path(args.output_dir)

    if args.auto:
        config = auto_discover_repository(repo_root)
        if args.emit_config:
            emit_path = Path(args.emit_config)
            emit_path.parent.mkdir(parents=True, exist_ok=True)
            emit_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
            print(f"Auto-discovered configuration emitted to {emit_path}")
            return 0
    elif args.config:
        config_path = Path(args.config)
        if not config_path.is_file():
            print(f"Error: configuration file '{config_path}' not found.", file=sys.stderr)
            return 1
        config = json.loads(config_path.read_text(encoding="utf-8"))
    else:
        # Default to BoneAmanita manifest if it exists
        default_manifest = repo_root / "tools" / "rag_manifest.boneamanita.json"
        if default_manifest.is_file():
            config = json.loads(default_manifest.read_text(encoding="utf-8"))
        else:
            print("No config provided; falling back to auto-discovery mode...")
            config = auto_discover_repository(repo_root)

    builder = RAGCorpusBuilder(repo_root=repo_root, config=config, output_dir=out_dir)
    print(f"Starting RAG Corpus compilation for '{config.get('title', 'Repository')}'...")
    print(f"Output directory: {out_dir}")
    print(f"Mode: {'DRY RUN (Check only)' if args.check else 'BUILD'}\n")

    results = builder.build_all(dry_run=args.check)

    print(f"{'Volume ID':<38} | {'Files':>5} | {'Words':>9} | {'Size (KB)':>9} | {'Status'}")
    print("-" * 80)
    for r in results:
        status = "OK" if not r["warning"] else r["warning"]
        kb = r["chars"] / 1024
        print(f"{r['id']:<38} | {r['file_count']:>5} | {r['words']:>9,} | {kb:>8.1f}K | {status}")
    print("-" * 80)

    total_files = sum(r["file_count"] for r in results)
    total_words = sum(r["words"] for r in results)
    total_mb = sum(r["chars"] for r in results) / 1024 / 1024

    print(f"Total: {len(results)} volumes | {total_files} files | {total_words:,} words | {total_mb:.2f} MB")
    if not args.check:
        print(f"\nCorpus successfully generated in: {out_dir}/")
        print(f"Master index written to: {out_dir / '00_CORPUS_INDEX.md'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
