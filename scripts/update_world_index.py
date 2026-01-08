import os
import subprocess
from datetime import datetime

ORG = "hopefulvision-llc"

# List of core repos to index (you can expand this anytime)
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

def main():
    lines = []
    lines.append("# 🏛️ HopefulVision — Auto-Generated World Index\n")
    lines.append(f"**Last Updated:** {datetime.utcnow().isoformat()} UTC\n")
    lines.append("**Status:** AUTO-GENERATED — DO NOT EDIT MANUALLY\n\n")
    lines.append("---\n")

    for repo in REPOS:
        base = f"https://github.com/{ORG}/{repo}"
        lines.append(f"## 📦 {repo}\n")
        lines.append(f"- Repository: {base}\n")
        lines.append(f"- README: {base}/blob/main/README.md\n")
        lines.append("")

    output = "\n".join(lines)

    with open("HopefulVision_World_Index_AUTO.md", "w", encoding="utf-8") as f:
        f.write(output)

    print("World index regenerated.")

if __name__ == "__main__":
    main()
