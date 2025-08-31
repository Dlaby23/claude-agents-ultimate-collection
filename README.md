# Ultimate Claude Agents Collection (Deduplicated)

**A meticulously curated and deduplicated collection of Claude Code subagents**

![Agents](https://img.shields.io/badge/Total%20Agents-470-blue)
![Duplicates Removed](https://img.shields.io/badge/Duplicates%20Removed-328-green)
![Categories](https://img.shields.io/badge/Categories-4-orange)

## 📊 Collection Statistics

| Metric | Value |
|--------|-------|
| **Total Unique Agents** | 470 |
| **Original Count** | 798 |
| **Duplicates Removed** | 328 (41%) |
| **Sources** | 12 repositories |
| **Deduplication Method** | Intelligent semantic analysis |

## 🗂️ Categories Breakdown

| Category | Count | Description |
|----------|-------|-------------|
| **Languages** | ~150 | Python, JavaScript, TypeScript, Go, Rust, Java, etc. |
| **Tasks** | ~120 | Testing, Debugging, Security, Deployment, Documentation |
| **Specialized** | ~150 | Domain-specific agents for various technologies |
| **Frameworks** | ~50 | React, Vue, Angular, Django, Rails, etc. |

## 🎯 Key Features

### Intelligent Deduplication
- **Semantic Analysis**: Agents with similar purposes (e.g., `python-pro`, `python-expert`, `python-developer`) were analyzed and only the highest quality version was kept
- **Quality Scoring**: Each agent was scored based on:
  - Content completeness and length
  - YAML frontmatter quality
  - Structured sections (responsibilities, guidelines, examples)
  - Code examples and specificity
  - Tool specifications

### What Was Removed
- Multiple versions of the same agent (e.g., 4 versions of `python-pro` → 1 best version)
- Agents with identical functionality but different names
- Lower quality duplicates with less documentation
- Redundant implementations from different sources

## 🚀 Installation

### Quick Install All Agents
```bash
git clone https://github.com/Dlaby23/claude-agents-ultimate-collection.git
cp -r claude-agents-ultimate-collection/agents/* ~/.claude/agents/
```

### Smart Installer (Recommended)
Install only the agents you need based on your task:

```bash
# Install the unified installer
curl -O https://raw.githubusercontent.com/Dlaby23/claude-agents-ultimate-collection/main/agent-installer-unified.py

# Use it to install relevant agents
python3 agent-installer-unified.py "help me build a React app with TypeScript"
```

## 📁 Repository Structure

```
agents/
├── languages/           # Language-specific agents
│   ├── python/         # Python development agents
│   ├── javascript/     # JavaScript/Node.js agents
│   ├── typescript/     # TypeScript agents
│   ├── go/            # Go/Golang agents
│   ├── rust/          # Rust agents
│   └── ...
├── tasks/              # Task-oriented agents
│   ├── testing/       # Testing and QA agents
│   ├── debugging/     # Debugging and troubleshooting
│   ├── security/      # Security audit and hardening
│   ├── deployment/    # CI/CD and deployment
│   └── ...
├── specialized/        # Domain-specific agents
│   └── general/       # Specialized tools and frameworks
└── frameworks/         # Framework-specific agents
    ├── frontend/      # React, Vue, Angular, etc.
    └── backend/       # Express, Django, Rails, etc.
```

## 🔍 Finding Agents

### By Language
- **Python**: Django, Flask, FastAPI, Data Science, ML
- **JavaScript**: Node.js, Express, React, Vue, Angular
- **TypeScript**: Full-stack, type-safe development
- **Go**: Microservices, system programming
- **Rust**: Systems programming, performance-critical

### By Task
- **Testing**: Unit tests, E2E, TDD, test automation
- **Debugging**: Error detection, troubleshooting, performance
- **Security**: Audits, vulnerability scanning, hardening
- **DevOps**: CI/CD, Docker, Kubernetes, deployment

### By Specialty
- **Frontend**: UI/UX, responsive design, accessibility
- **Backend**: APIs, databases, microservices
- **Data**: Analysis, ML/AI, data engineering
- **Cloud**: AWS, Azure, GCP, serverless

## 📋 Deduplication Details

See `deduplication_log.json` for complete details on:
- Which agents were merged
- Quality scores for each agent
- Decision rationale for keeping specific versions

### Example Deduplication
```json
{
  "group": "python",
  "selected": "python-pro",
  "score": 75.0,
  "rejected": ["python-expert", "python-developer", "python-engineer"],
  "reason": "Highest quality score (75.0)"
}
```

## 🤝 Contributing

This collection is aggregated from these amazing community repositories:

- [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)
- [wshobson/agents](https://github.com/wshobson/agents)
- [0xfurai/claude-code-subagents](https://github.com/0xfurai/claude-code-subagents)
- [davepoon/claude-code-subagents-collection](https://github.com/davepoon/claude-code-subagents-collection)
- [iannuttall/claude-agents](https://github.com/iannuttall/claude-agents)
- [zhsama/claude-sub-agent](https://github.com/zhsama/claude-sub-agent)
- [vanzan01/claude-code-sub-agent-collective](https://github.com/vanzan01/claude-code-sub-agent-collective)
- [fengyunzaidushi/claude-code-subagents](https://github.com/fengyunzaidushi/claude-code-subagents)
- [hesreallyhim/awesome-claude-code-agents](https://github.com/hesreallyhim/awesome-claude-code-agents)
- [rahulvrane/awesome-claude-agents](https://github.com/rahulvrane/awesome-claude-agents)
- [lst97/claude-code-sub-agents](https://github.com/lst97/claude-code-sub-agents)
- [dl-ezo/claude-code-sub-agents](https://github.com/dl-ezo/claude-code-sub-agents)

## 📄 License

This collection aggregates agents from various open-source repositories. Please refer to individual source repositories for specific licensing information.

## 👤 Maintained By

Created and maintained by Vaclav Dlabac

---

**Note**: This is a deduplicated collection. The original 798 agents were reduced to 470 unique agents through intelligent semantic analysis and quality scoring.