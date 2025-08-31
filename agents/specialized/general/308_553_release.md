name: Release

on:
  push:
    branches:
      - main

concurrency: ${{ github.workflow }}-${{ github.ref }}

jobs:
  release:
    name: Release
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      packages: write
      issues: read
    steps:
      - name: Checkout Repo
        uses: actions/checkout@v4
        with:
          # This makes Actions fetch all Git history so that Changesets can generate changelogs with the correct commits
          fetch-depth: 0
          # Use a Personal Access Token to allow PR creation
          token: ${{ secrets.RELEASE_TOKEN || secrets.GITHUB_TOKEN }}

      - name: Setup Node.js 20.x
        uses: actions/setup-node@v4
        with:
          node-version: 20.x
          cache: 'npm'

      - name: Install Dependencies
        run: npm ci

      - name: Create Release Pull Request or Publish to npm
        id: changesets
        uses: changesets/action@v1
        with:
          # This expects you to have a script called changeset:publish which publishes your packages
          publish: npm run release
          # This expects you to have a script called changeset:version which updates versions and changelogs
          version: npm run version-packages
          commit: "chore: release packages"
          title: "chore: release packages"
          createGithubReleases: true
        env:
          GITHUB_TOKEN: ${{ secrets.RELEASE_TOKEN || secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}

      - name: Comment on PR
        if: steps.changesets.outputs.pullRequestNumber
        uses: actions/github-script@v7
        with:
          script: |
            const prNumber = ${{ steps.changesets.outputs.pullRequestNumber }};
            const hasChangesets = ${{ steps.changesets.outputs.hasChangesets }};
            const publishedPackages = ${{ steps.changesets.outputs.publishedPackages || '[]' }};
            
            if (hasChangesets === 'true' && publishedPackages.length > 0) {
              const packages = publishedPackages.map(pkg => `- ${pkg.name}@${pkg.version}`).join('\n');
              const body = `## 🚀 Released Packages\n\nThe following packages have been published:\n\n${packages}`;
              
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: prNumber,
                body: body
              });
            }