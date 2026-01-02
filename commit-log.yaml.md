# Commit Log Workflow

This repository includes an automated workflow that logs all commits made to the `main` branch into a `commit-log.yaml` file.

## How It Works

The workflow (`.github/workflows/commit-log.yml`) automatically:
1. Triggers on every push to the `main` branch
2. Captures commit information (SHA, message, author, timestamp, repository, branch)
3. Appends the information to `commit-log.yaml` in a structured format
4. Commits and pushes the updated log back to the repository

## Features

- **Automatic Logging**: Every commit to main is automatically logged
- **Loop Prevention**: The workflow skips execution for commits containing `[skip ci]` in the message
- **Safe Character Handling**: Uses `jq` for JSON generation to safely handle special characters in commit messages
- **Security**: yq binary is pinned to version v4.40.5 with SHA256 checksum verification

## Log Format

The `commit-log.yaml` file contains a list of commits with the following structure:

```yaml
commits:
  - sha: "abc123..."
    message: "commit message"
    author: "username"
    timestamp: "2026-01-02T02:30:00Z"
    repository: "hopefulvision-llc/.github"
    branch: "main"
```

## Technical Details

The workflow uses:
- **yq v4.40.5**: YAML processor for manipulating the commit-log.yaml file
- **jq**: JSON processor for safe variable handling
- **github-actions[bot]**: Bot account for committing the updated log

## Why This Exists

This provides a human-readable audit trail of all changes to the main branch, stored directly in the repository for easy access and historical tracking.
