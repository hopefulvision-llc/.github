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

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

def main():
    if os.path.exists(WORKDIR):
        shutil.rmtree(WORKDIR)
    os.mkdir(WORKDIR)

    lines = []
    lines.append("# 🏛️ HopefulVision — Auto-Generated World Index\n")
    lines.append(f"**Last Updated:** {datetime.utcnow().isoformat()} UTC\n")
    lines.append("**Status:** AUTO-GENERATED — DO NOT EDIT MANUALLY\n")
    lines.append("---\n")

    for repo in REPOS:
        print(f"Indexing {repo}...")
        repo_url = f"https://github.com/{ORG}/{repo}.git"
        local_path = os.path.join(WORKDIR, repo)

        run(f"git clone --depth=1 {repo_url} {local_path}")

        lines.append(f"\n## 📦 {repo}\n")
        lines.append(f"Repository: https://github.com/{ORG}/{repo}\n")

        file_count = 0

        for root, dirs, files in os.walk(local_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in EXTENSIONS:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, local_path)
                    github_url = f"https://github.com/{ORG}/{repo}/blob/main/{rel_path.replace(os.sep, '/')}"
                    lines.append(f"- {github_url}")
                    file_count += 1

        lines.append(f"\n> Indexed {file_count} files.\n")

    output = "\n".join(lines)

    with open("HopefulVision_World_Index_AUTO.md", "w", encoding="utf-8") as f:
        f.write(output)

    print("World index regenerated.")

if __name__ == "__main__":
    main()
