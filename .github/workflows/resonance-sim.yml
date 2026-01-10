#!/usr/bin/env python3
"""
Resonance Sim: Turn GitHub repo Markdown files + links + history into coherence geometry
Robust version with error handling and correct GitPython index usage
"""

import os
import sys
import re
from datetime import datetime, timezone
import traceback
from git import Repo, GitCommandError
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

# Config thresholds (from the simplicial coherence model)
CHI_L = 0.3          # below → Lorentzian (red, low coherence)
CHI_E = 0.7          # above → Euclidean (blue, high coherence)
CHI_C = 0.5          # critical zone (purple, χ_c)
NOISE = 0.05         # small random fluctuation for dynamics

# Paths (relative to repo root)
REPO_PATH = "."      # Current checkout from GitHub Actions
OUTPUT_SVG = "resonance_state.svg"

def log(msg):
    """Simple logging to stdout (visible in Actions logs)"""
    print(f"[Resonance] {msg}", file=sys.stdout, flush=True)

def get_tracked_md_files(repo):
    """
    Return list of currently tracked Markdown files (stage=0, clean index)
    Uses correct .entries.items() access
    """
    try:
        md_files = [
            path
            for path, entry in repo.index.entries.items()
            if path.endswith(('.md', '.markdown')) and entry.stage == 0
        ]
        log(f"Found {len(md_files)} tracked Markdown files")
        return md_files
    except Exception as e:
        log(f"Error reading index: {e}")
        return []

def compute_recency_bonus(repo, path):
    """Recency bonus: 1.0 = today, decays to ~0 over 90 days"""
    try:
        # Get the most recent commit touching this file
        commits = list(repo.iter_commits(paths=path, max_count=1))
        if not commits:
            return 0.1  # fallback for new/untouched files
        last_commit = commits[0]
        days_old = (datetime.now(timezone.utc) - last_commit.committed_datetime).days
        bonus = max(0.0, 1.0 - days_old / 90.0)
        return bonus
    except Exception as e:
        log(f"Recency fallback for {path}: {e}")
        return 0.1

def extract_links_from_md(content, current_path):
    """
    Extract links: Obsidian [[wiki-style]], Markdown [text](url/relative), bare URLs
    Returns potential target paths (normalized)
    """
    links = set()

    # Obsidian-style: [[target]] or [[target|alias]]
    for match in re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content):
        links.add(match.strip())

    # Markdown links: [text](target)
    for match in re.findall(r'\[.*?\]\((.*?)\)', content):
        if not match.startswith(('http://', 'https://', '#')):
            links.add(match.strip())

    # Bare URLs (optional, but useful)
    for match in re.findall(r'https?://[^\s<>\)]+', content):
        links.add(match)

    # Try to resolve to actual file paths (very approximate)
    candidates = []
    base_dir = os.path.dirname(current_path)
    for link in links:
        # Skip external/http
        if link.startswith(('http', '#')):
            continue
        # Clean up extensions if present
        link_clean = link.split('|')[0].strip()
        if not link_clean.endswith(('.md', '.markdown')):
            link_clean += '.md'
        # Relative path attempt
        possible = os.path.normpath(os.path.join(base_dir, link_clean))
        candidates.append(possible)

    return candidates

def build_graph(repo):
    """Build NetworkX graph from MD files + extracted links"""
    G = nx.Graph()
    md_files = get_tracked_md_files(repo)

    if not md_files:
        log("No Markdown files found - empty graph")
        return G

    # Add nodes with attributes
    for fpath in md_files:
        try:
            recency = compute_recency_bonus(repo, fpath)
            try:
                content = repo.git.show(f"HEAD:{fpath}")
            except GitCommandError:
                content = ""  # file might be deleted in HEAD but still in index
            G.add_node(fpath, recency=recency, content=content)
        except Exception as e:
            log(f"Failed to process node {fpath}: {e}")
            G.add_node(fpath, recency=0.1, content="")

    # Add edges based on links
    for node in list(G.nodes):
        content = G.nodes[node].get('content', '')
        targets = extract_links_from_md(content, node)
        for tgt_path in targets:
            if tgt_path in G.nodes:
                G.add_edge(node, tgt_path, weight=1.0)
            else:
                # Optional: add missing targets as ghost nodes?
                pass

    log(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G

def compute_chi(G):
    """χ ≈ normalized degree centrality + recency + small noise"""
    if len(G) == 0:
        log("Empty graph → no chi values")
        return {}

    deg = nx.degree_centrality(G)
    max_deg = max(deg.values()) if deg else 1.0

    chis = {}
    for node in G.nodes:
        base = deg.get(node, 0) / max_deg
        rec = G.nodes[node].get('recency', 0.1)
        chi = 0.65 * base + 0.35 * rec + np.random.normal(0, NOISE)
        chi = np.clip(chi, 0.0, 1.0)
        chis[node] = chi
    return chis

def signature(chi):
    if chi < CHI_L:
        return -1, 'Lorentzian', 'red'
    elif chi > CHI_E:
        return +1, 'Euclidean', 'blue'
    else:
        return 0, 'Critical', 'purple'

def plot_resonance(G, chis):
    """Generate spring-layout plot colored by signature"""
    if len(G) < 1:
        log("Nothing to plot")
        return

    try:
        pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
        node_colors = []
        node_sizes = []
        labels = {}

        for node, chi in chis.items():
            sig, label, color = signature(chi)
            node_colors.append(color)
            node_sizes.append(300 + 800 * chi)  # bigger = higher coherence
            short_name = os.path.basename(node)
            labels[node] = f"{short_name}\nχ={chi:.2f}"

        plt.figure(figsize=(14, 11))
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.9)
        nx.draw_networkx_edges(G, pos, alpha=0.25, width=0.8)
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_weight='bold')
        plt.title("Vault Resonance Geometry\n(red = Lorentzian • blue = Euclidean • purple = Critical)")
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(OUTPUT_SVG, format='svg', bbox_inches='tight')
        plt.close()
        log(f"Plot saved: {OUTPUT_SVG}")
    except Exception as e:
        log(f"Plotting failed: {e}\n{traceback.format_exc()}")

def main():
    try:
        repo = Repo(REPO_PATH)
        if repo.bare:
            log("Bare repository detected - skipping simulation")
            sys.exit(0)

        log("Starting resonance simulation...")
        G = build_graph(repo)
        chis = compute_chi(G)
        plot_resonance(G, chis)

        # Commit the result back (Actions runner has write access)
        if os.path.exists(OUTPUT_SVG):
            repo.index.add([OUTPUT_SVG])
            try:
                repo.index.commit("Update resonance state visualization [auto]")
                log("Successfully committed resonance plot")
            except Exception as commit_err:
                log(f"Commit skipped (maybe no change): {commit_err}")
        else:
            log("No plot generated - nothing to commit")

    except Exception as e:
        log(f"Critical error in main: {e}\n{traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
