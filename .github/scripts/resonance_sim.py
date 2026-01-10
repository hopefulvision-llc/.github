#!/usr/bin/env python3
"""
Resonance Sim: Turn GitHub repo history + markdown links into coherence geometry
"""

import os
import sys
import re
from datetime import datetime, timezone
from git import Repo
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from markdown import markdown  # for basic link extraction if needed

# Config thresholds (from your model)
CHI_L = 0.3     # below → Lorentzian (red)
CHI_E = 0.7     # above → Euclidean (blue)
CHI_C = 0.5     # critical zone (purple)
NOISE = 0.05    # small random kick for dynamics

# Paths
REPO_PATH = "."  # current repo context from Actions checkout
OUTPUT_SVG = "resonance_state.svg"

def get_tracked_md_files(repo):
    """List all .md files currently tracked"""
    return [item.a_path for item in repo.index.iter_entries()
            if item.a_path and item.a_path.endswith(('.md', '.markdown'))]

def compute_recency_bonus(commit_date):
    """Bonus for recent activity: 1.0 = today, decays to 0 over ~90 days"""
    days_old = (datetime.now(timezone.utc) - commit_date).days
    return max(0.0, 1.0 - days_old / 90.0)

def extract_links_from_md(content):
    """Simple extraction of wiki-style [[links]] and plain http(s) URLs"""
    wiki_links = re.findall(r'\[\[([^\]]+)\]\]', content)
    url_links = re.findall(r'https?://[^\s<>\)]+', content)
    return wiki_links + url_links  # treat as target node names for now

def build_graph(repo):
    G = nx.Graph()
    md_files = get_tracked_md_files(repo)

    # Add nodes + basic χ seed from file age/activity
    for fpath in md_files:
        try:
            blame = repo.blame(fpath)[-1]  # last commit touching the file
            last_commit = blame.commit
            recency = compute_recency_bonus(last_commit.committed_datetime)
            G.add_node(fpath, recency=recency, content=repo.git.show(f"{last_commit.hexsha}:{fpath}"))
        except:
            G.add_node(fpath, recency=0.1, content="")

    # Add edges from links
    for node in list(G.nodes):
        content = G.nodes[node]['content']
        targets = extract_links_from_md(content)
        for tgt in targets:
            # Rough match: if target basename appears in any node
            candidate = next((n for n in G.nodes if os.path.basename(tgt) in n), None)
            if candidate and candidate != node:
                G.add_edge(node, candidate, weight=1.0)

    return G

def compute_chi(G):
    """χ ≈ degree centrality normalized + recency bonus + tiny noise"""
    if len(G) == 0:
        return {}
    deg = nx.degree_centrality(G)
    max_deg = max(deg.values()) if deg else 1
    chis = {}
    for node in G.nodes:
        base = deg.get(node, 0) / max_deg
        rec = G.nodes[node]['recency']
        chi = 0.7 * base + 0.3 * rec + np.random.normal(0, NOISE)
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
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
    node_colors = []
    node_labels = {}
    for node, chi in chis.items():
        sig, label, color = signature(chi)
        node_colors.append(color)
        node_labels[node] = f"{os.path.basename(node)}\nχ={chi:.2f}"

    plt.figure(figsize=(12, 10))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800, alpha=0.9)
    nx.draw_networkx_edges(G, pos, alpha=0.3)
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8)
    plt.title("Vault Resonance Geometry\n(red = Lorentzian, blue = Euclidean, purple = Critical)")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(OUTPUT_SVG, format='svg')
    plt.close()

def main():
    try:
        repo = Repo(REPO_PATH)
        if not repo.bare:
            print("Building resonance graph...")
            G = build_graph(repo)
            chis = compute_chi(G)
            plot_resonance(G, chis)
            print(f"Done! Plot saved to {OUTPUT_SVG}")
            # Git add & commit (Actions will push)
            repo.index.add([OUTPUT_SVG])
            repo.index.commit("Update resonance state visualization")
            print("Committed plot.")
        else:
            print("Bare repo - skipping.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
