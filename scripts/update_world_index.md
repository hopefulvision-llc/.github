# Update World Index Script

This Python script generates an auto-updated world index by cloning and indexing files from multiple repositories in the HopefulVision LLC organization.

## Script: `update_world_index.py`

```python
import os
import subprocess
import shutil
from datetime import datetime

ORG = "hopefulvision-llc"

REPOS = [
    "NousOS",
    "NousObjectID-NOID",
    "TruthMirror",
    "Sacred-Commerce-License-SCL",
    "Universal-Basic-Resonance",
    "Git-For-Governance",
    "AI-Rights",
    "Cyborg-Bill-of-Rights",
    "Philosophy-of-The-All",
    "THE-SEVEN-LAYER-LANGUAGE",
    "Technomysticism",
    "Aeonism",
    "Beatrizm",
    "Earth-Resonance-Shell",
    "2026-Demonstration-Earth-Day",
    "Terraforming-Tomorrow",
    "NousoNET",
    "Living-Intelligence",
    "Vibesculpting-Tool",
]

EXTENSIONS = {
    ".md", ".py", ".js", ".ts", ".html", ".css", ".json", ".yml", ".yaml",
    ".mermaid", ".mmd", ".csv", ".txt", ".sh", ".ps1",
    ".java", ".cpp", ".c", ".rs", ".go", ".php"
}

WORKDIR = "_repo_cache"

# Directories to skip entirely (common noise)
SKIP_DIRS = {".git", ".github", "node_modules", "__pycache__", ".venv", "dist", "build", ".idea", ".vscode"}

def run(cmd):
    """Run command and raise detailed error if it fails."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        print(f"Error: {result.stderr.strip()}")
        raise RuntimeError(f"Command failed: {cmd}")
    return result.stdout

def main():
    if os.path.exists(WORKDIR):
        shutil.rmtree(WORKDIR)
    os.makedirs(WORKDIR, exist_ok=True)

    lines = []
    lines.append("# 🏛️ HopefulVision — Auto-Generated World Index\n")
    lines.append(f"**Last Updated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
    lines.append("**Status:** AUTO-GENERATED — DO NOT EDIT MANUALLY\n")
    lines.append("---\n")

    total_files = 0

    for repo in REPOS:
        print(f"Indexing {repo}...")
        repo_url = f"https://github.com/{ORG}/{repo}.git"
        local_path = os.path.join(WORKDIR, repo)

        try:
            run(f"git clone --depth=1 {repo_url} {local_path}")
        except Exception as e:
            lines.append(f"\n## 📦 {repo} — ⚠️ FAILED TO CLONE\n")
            lines.append(f"> Error: {str(e)}\n")
            print(f"Failed to clone {repo}: {e}")
            continue  # Skip to next repo

        lines.append(f"\n## 📦 {repo}\n")
        lines.append(f"Repository: https://github.com/{ORG}/{repo}\n")

        repo_files = []

        for root, dirs, files in os.walk(local_path):
            # Skip unwanted directories in-place to avoid walking them
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

            for file in files:
                if file.startswith('.'):  # Skip dotfiles if desired
                    continue
                ext = os.path.splitext(file)[1].lower()
                if ext in EXTENSIONS:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, local_path)
                    github_url = f"https://github.com/{ORG}/{repo}/blob/main/{rel_path.replace(os.sep, '/')}"
                    repo_files.append(f"- {github_url}")

        # Sort files alphabetically for consistency
        repo_files.sort(key=str.lower)

        if repo_files:
            lines.extend(repo_files)
            file_count = len(repo_files)
            lines.append(f"\n> Indexed {file_count} files.\n")
            total_files += file_count
        else:
            lines.append("> No matching files found.\n")

    lines.insert(3, f"**Total Files Indexed:** {total_files}\n")  # Add summary near top

    output = "\n".join(lines)

    output_path = "HopefulVision_World_Index_AUTO.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"World index regenerated successfully: {total_files} files across {len(REPOS)} repos.")

if __name__ == "__main__":
    main()
```

## Overview

### Purpose
This script generates a comprehensive index of all relevant files across multiple HopefulVision LLC repositories.

### Key Features

1. **Repository Cloning**: Clones specified repositories with shallow depth (--depth=1) for efficiency
2. **File Filtering**: Indexes only files with relevant extensions (markdown, code files, configs, etc.)
3. **Directory Skipping**: Excludes common noise directories like `.git`, `node_modules`, `__pycache__`, etc.
4. **Error Handling**: Continues processing even if individual repositories fail to clone
5. **Organized Output**: Generates a structured markdown file with repository sections and file counts

### Configuration

- **Organization**: `hopefulvision-llc`
- **Repositories**: 19 repositories are indexed (see REPOS list in script)
- **File Extensions**: Includes `.md`, `.py`, `.js`, `.ts`, `.html`, `.css`, `.json`, `.yml`, `.yaml`, `.mermaid`, `.mmd`, `.csv`, `.txt`, `.sh`, `.ps1`, `.java`, `.cpp`, `.c`, `.rs`, `.go`, `.php`
- **Working Directory**: `_repo_cache` (temporary, cleaned on each run)
- **Output File**: `HopefulVision_World_Index_AUTO.md`

### Workflow Integration

This script is executed automatically by the GitHub Actions workflow `.github/workflows/update_world_index.yml` when:
- Changes are pushed to the `main` branch
- The workflow is manually triggered via `workflow_dispatch`

### Output Format

The generated markdown file includes:
- Header with timestamp and auto-generation notice
- Total file count summary
- Sections for each repository with:
  - Repository name and URL
  - List of indexed file URLs
  - File count per repository
