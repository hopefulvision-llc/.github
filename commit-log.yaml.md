name: Log Commit to Supabase

on:
  push:
    branches:
      - main

jobs:
  log-commit:
    runs-on: ubuntu-latest
    steps:
      - name: Send commit info to Supabase
        run: |
          curl -X POST "${{ secrets.SUPABASE_URL }}/rest/v1/commit_log" \
            -H "apikey: ${{ secrets.SUPABASE_ANON_KEY }}" \
            -H "Authorization: Bearer ${{ secrets.SUPABASE_ANON_KEY }}" \
            -H "Content-Type: application/json" \
            -H "Prefer: return=minimal" \
            -d '{
              "commit_sha": "${{ github.sha }}",
              "commit_message": "${{ github.event.head_commit.message }}",
              "author": "${{ github.actor }}",
              "timestamp": "${{ github.event.head_commit.timestamp }}",
              "repo": "${{ github.repository }}",
              "branch": "main"
            }'