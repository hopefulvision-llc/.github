
#!/usr/bin/env python3
"""
Auto-generate HopefulVision World Index
Scans all repositories in hopefulvision-llc org and creates an index of all files.
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Tuple
import requests

# Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
ORG_NAME = 'hopefulvision-llc'
OUTPUT_FILE = 'HopefulVision_World_Index_AUTO.md'

# File extensions to index
INDEXED_EXTENSIONS = {
    '.md', '.py', '. js', '.html', '.css', '.json', 
    '.mermaid', '.txt', '.yaml', '.yml', '.toml'
}

# Headers for GitHub API
HEADERS = {
    'Accept': 'application/vnd.github.v3+json',
}

if GITHUB_TOKEN:
    HEADERS['Authorization'] = f'token {GITHUB_TOKEN}'


def get_org_repositories() -> List[Dict]:
    """Fetch all repositories from the organization."""
    repos = []
    page = 1
    per_page = 100
    
    while True:
        url = f'https://api.github.com/orgs/{ORG_NAME}/repos'
        params = {
            'per_page': per_page,
            'page': page,
            'sort': 'name',
            'type': 'public'
        }
        
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code != 200:
            print(f"❌ Error fetching repositories: {response.status_code}")
            print(response.json())
            sys.exit(1)
        
        page_repos = response. json()
        
        if not page_repos:
            break
            
        repos.extend(page_repos)
        page += 1
    
    return repos


def get_repo_files(repo_name: str, branch: str, path: str = '') -> List[str]:
    """Recursively get all files from a repository."""
    files = []
    
    url = f'https://api.github.com/repos/{ORG_NAME}/{repo_name}/contents/{path}'
    params = {'ref': branch}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        
        if response. status_code != 200:
            print(f"   ⚠️  Warning: Could not fetch {repo_name}/{path} (Status: {response.status_code})")
            return files
        
        contents = response.json()
        
        # Handle case where response is not a list (single file)
        if not isinstance(contents, list):
            return files
        
        for item in contents:
            if item['type'] == 'file':
                # Check if file extension is in our indexed list
                file_path = item['path']
                _, ext = os.path.splitext(file_path)
                
                if ext.lower() in INDEXED_EXTENSIONS:
                    files.append(file_path)
            elif item['type'] == 'dir':
                # Recursively get files from subdirectories
                files.extend(get_repo_files(repo_name, branch, item['path']))
                
    except Exception as e:
        print(f"   ⚠️  Exception processing {repo_name}/{path}: {str(e)}")
    
    return files


def generate_index_content(repos_data: List[Tuple[str, List[str], str]]) -> str:
    """Generate the markdown content for the index."""
    timestamp = datetime. utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    total_files = sum(len(files) for _, files, _ in repos_data)
    
    content = f"""# 🏛️ HopefulVision — Auto-Generated World Index

**Last Updated:** {timestamp}

**Status:** AUTO-GENERATED — DO NOT EDIT MANUALLY

**Total Files Indexed:** {total_files}

---

"""
    
    for repo_name, files, branch in repos_data:
        if not files:
            continue
            
        content += f"\n## 📦 {repo_name}\n\n"
        content += f"Repository: https://github.com/{ORG_NAME}/{repo_name}\n\n"
        
        for file_path in sorted(files):
            file_url = f"https://github.com/{ORG_NAME}/{repo_name}/blob/{branch}/{file_path}"
            content += f"- {file_url}\n"
        
        content += f"\n> Indexed **{len(files)}** files.\n\n"
    
    return content


def main():
    """Main function to generate the index."""
    print("🔍 Fetching repositories from hopefulvision-llc organization...")
    repos = get_org_repositories()
    print(f"✅ Found {len(repos)} repositories\n")
    
    repos_data = []
    
    for repo in repos:
        repo_name = repo['name']
        print(f"📂 Processing: {repo_name}")
        
        # Get default branch
        branch = repo. get('default_branch', 'main')
        print(f"   Branch: {branch}")
        
        # Skip archived repositories
        if repo.get('archived', False):
            print(f"   ⏭️  Skipped (archived)")
            continue
        
        # Get all files
        files = get_repo_files(repo_name, branch)
        print(f"   ✓ Files found: {len(files)}")
        
        repos_data. append((repo_name, files, branch))
    
    print("\n📝 Generating index content...")
    content = generate_index_content(repos_data)
    
    print(f"💾 Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    total_files = sum(len(files) for _, files, _ in repos_data)
    active_repos = len([r for r in repos_data if r[1]])  # repos with files
    
    print(f"\n✨ Successfully generated index!")
    print(f"   📊 Total:  {total_files} files from {active_repos} repositories")


if __name__ == '__main__':
    if not GITHUB_TOKEN:
        print("⚠️  Warning: GITHUB_TOKEN not set. API rate limits will be lower.")
        print("   Set GITHUB_TOKEN environment variable for better performance.\n")
    
    main()
