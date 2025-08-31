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

## ⚠️ IMPORTANT: Smart Usage Recommended

### 🚫 DON'T Install All 470 Agents!
Installing the entire collection will bloat your system unnecessarily. Instead, use our intelligent **Subagent-Selector** system that automatically installs only the agents you need for each project.

### ✅ Recommended Approach: Subagent-Selector

The **Subagent-Selector** is a meta-agent that:
1. **Analyzes each prompt** you give to Claude Code
2. **Automatically identifies** which agents would be helpful
3. **Installs only those agents** to your current project
4. **Keeps your system clean** - no unnecessary agents

#### How to Set It Up:

1. **Install the Subagent-Selector globally** (one-time setup):
```bash
# Create global agents directory
mkdir -p ~/.claude/agents

# Download the subagent-selector
curl -O https://raw.githubusercontent.com/Dlaby23/claude-agents-ultimate-collection/main/agents/specialized/general/subagent-selector.md
mv subagent-selector.md ~/.claude/agents/
```

2. **Install the smart installer**:
```bash
# Download the smart installer
curl -O https://raw.githubusercontent.com/Dlaby23/claude-agents-ultimate-collection/main/smart-agent-installer.py
chmod +x smart-agent-installer.py
mv smart-agent-installer.py ~/.claude/
```

3. **Use it naturally** - Just work normally and agents will be installed as needed:
```bash
# Start a new project
cd my-new-project

# The selector will automatically install relevant agents based on your prompts:
# "Help me build a React app" → Installs React, JavaScript, Frontend agents
# "I need to add testing" → Installs Testing, Jest, QA agents
# "Deploy with Docker" → Installs Docker, DevOps, Deployment agents
```

### 🎯 Benefits of This Approach:
- **No System Bloat** - Only install what you actually use
- **Project-Specific** - Each project gets its own tailored agent set
- **Automatic** - No manual agent selection needed
- **Intelligent** - Learns from your prompts to fetch the right tools
- **Efficient** - Typically installs 5-10 agents per project instead of 470

### 📊 Example Scenarios:

| Your Task | Agents Auto-Installed | Total Agents |
|-----------|----------------------|--------------|
| "Build a Python FastAPI app" | python-pro, fastapi-expert, backend-architect, api-designer, testing | 5 agents |
| "Create React TypeScript app" | react-pro, typescript-pro, frontend-developer, component-designer | 4 agents |
| "Debug database performance" | database-optimizer, sql-expert, debugger, performance-engineer | 4 agents |
| "Setup CI/CD pipeline" | devops-engineer, docker-expert, github-actions, deployment-engineer | 4 agents |

**Result**: Instead of 470 agents cluttering your system, you'll have exactly what you need for each project!

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

## 🚀 Installation Options

### Option 1: Smart Installation (STRONGLY RECOMMENDED) ✅
See the **"⚠️ IMPORTANT: Smart Usage Recommended"** section above for the subagent-selector approach that:
- Installs agents automatically based on your needs
- Keeps your system clean
- Typically uses only 5-10 agents per project

### Option 2: Manual Selection
Browse the repository and copy specific agents you need:
```bash
# Clone the repository
git clone https://github.com/Dlaby23/claude-agents-ultimate-collection.git

# Copy only specific agents you want
cp claude-agents-ultimate-collection/agents/languages/python/294_526_python-pro.md ~/.claude/agents/
```

### Option 3: Full Installation (NOT Recommended) ⚠️
Only if you really need all 470 agents (unlikely):
```bash
git clone https://github.com/Dlaby23/claude-agents-ultimate-collection.git
cp -r claude-agents-ultimate-collection/agents/* ~/.claude/agents/
# Warning: This will add 470 agents to your system!
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