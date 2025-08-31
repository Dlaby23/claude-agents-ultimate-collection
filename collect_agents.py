#!/usr/bin/env python3
"""
Agent Collection and Organization Script
Collects all agents from multiple repositories, deduplicates, and organizes them
"""

import os
import json
import hashlib
import shutil
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import yaml
from difflib import SequenceMatcher

@dataclass
class Agent:
    """Agent metadata structure"""
    original_path: str
    source_repo: str
    name: str
    description: str
    content: str
    content_hash: str
    yaml_frontmatter: dict
    tools: list
    category: str = ""
    subcategory: str = ""
    agent_id: int = 0
    quality_score: int = 0

class AgentCollector:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.all_agents = []
        self.unique_agents = []
        self.duplicates = []
        self.categories = {
            "languages": {
                "python": ["python", "py", "pip", "django", "flask", "fastapi"],
                "javascript": ["javascript", "js", "node", "npm"],
                "typescript": ["typescript", "ts", "tsx"],
                "java": ["java", "spring", "maven"],
                "csharp": ["c#", "csharp", "dotnet", ".net"],
                "cpp": ["c++", "cpp", "cmake"],
                "rust": ["rust", "cargo"],
                "go": ["go", "golang"],
                "ruby": ["ruby", "rails"],
                "php": ["php", "laravel"],
                "swift": ["swift", "ios"],
                "kotlin": ["kotlin", "android"]
            },
            "frameworks": {
                "react": ["react", "jsx", "hooks"],
                "vue": ["vue", "vuex", "pinia"],
                "angular": ["angular", "rxjs"],
                "nextjs": ["next", "nextjs", "vercel"],
                "express": ["express", "nodejs"],
                "django": ["django", "drf"],
                "flask": ["flask", "werkzeug"],
                "fastapi": ["fastapi", "pydantic"],
                "spring": ["spring", "boot"],
                "rails": ["rails", "activerecord"]
            },
            "tasks": {
                "testing": ["test", "testing", "tdd", "bdd", "jest", "pytest", "unit"],
                "debugging": ["debug", "fix", "bug", "error", "troubleshoot"],
                "refactoring": ["refactor", "optimize", "clean", "improve"],
                "security": ["security", "audit", "vulnerability", "penetration"],
                "review": ["review", "code review", "quality"],
                "documentation": ["document", "docs", "readme", "api"],
                "deployment": ["deploy", "ci/cd", "docker", "kubernetes"],
                "automation": ["automate", "automation", "workflow", "pipeline"]
            },
            "specialized": {
                "devops": ["devops", "infrastructure", "terraform", "ansible"],
                "data": ["data", "analysis", "ml", "ai", "science", "pandas"],
                "mobile": ["mobile", "ios", "android", "react-native", "flutter"],
                "cloud": ["aws", "azure", "gcp", "cloud", "serverless"],
                "database": ["database", "sql", "nosql", "postgres", "mongodb"],
                "frontend": ["frontend", "ui", "ux", "css", "design"],
                "backend": ["backend", "api", "server", "microservice"],
                "blockchain": ["blockchain", "crypto", "web3", "solidity"],
                "game": ["game", "unity", "unreal", "godot"],
                "iot": ["iot", "embedded", "arduino", "raspberry"]
            }
        }
    
    def extract_yaml_frontmatter(self, content: str) -> Tuple[dict, str]:
        """Extract YAML frontmatter from markdown content"""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    return frontmatter or {}, parts[2].strip()
                except:
                    pass
        return {}, content
    
    def calculate_quality_score(self, agent: Agent) -> int:
        """Calculate quality score for an agent"""
        score = 0
        
        # Check for YAML frontmatter
        if agent.yaml_frontmatter:
            score += 10
            if 'name' in agent.yaml_frontmatter:
                score += 5
            if 'description' in agent.yaml_frontmatter:
                score += 5
            if 'tools' in agent.yaml_frontmatter:
                score += 5
        
        # Check content length
        content_length = len(agent.content)
        if content_length > 500:
            score += 5
        if content_length > 1000:
            score += 5
        if content_length > 2000:
            score += 5
        
        # Check for proper structure
        if '## ' in agent.content:
            score += 3
        if '### ' in agent.content:
            score += 2
        
        # Check for code blocks
        if '```' in agent.content:
            score += 5
        
        # Check for clear instructions
        keywords = ['responsibilities', 'guidelines', 'process', 'steps', 'workflow']
        for keyword in keywords:
            if keyword.lower() in agent.content.lower():
                score += 2
        
        return score
    
    def categorize_agent(self, agent: Agent) -> Tuple[str, str]:
        """Determine category and subcategory for an agent"""
        name_lower = agent.name.lower()
        desc_lower = agent.description.lower()
        content_lower = agent.content[:1000].lower()
        
        best_category = "specialized"
        best_subcategory = "general"
        best_score = 0
        
        for category, subcategories in self.categories.items():
            for subcategory, keywords in subcategories.items():
                score = 0
                for keyword in keywords:
                    if keyword in name_lower:
                        score += 3
                    if keyword in desc_lower:
                        score += 2
                    if keyword in content_lower:
                        score += 1
                
                if score > best_score:
                    best_score = score
                    best_category = category
                    best_subcategory = subcategory
        
        return best_category, best_subcategory
    
    def similarity_score(self, agent1: Agent, agent2: Agent) -> float:
        """Calculate similarity between two agents"""
        # Name similarity
        name_sim = SequenceMatcher(None, agent1.name, agent2.name).ratio()
        
        # Description similarity
        desc_sim = SequenceMatcher(None, agent1.description, agent2.description).ratio()
        
        # Content similarity (first 500 chars)
        content1 = agent1.content[:500]
        content2 = agent2.content[:500]
        content_sim = SequenceMatcher(None, content1, content2).ratio()
        
        # Weighted average
        return (name_sim * 0.3 + desc_sim * 0.2 + content_sim * 0.5)
    
    def find_duplicates(self):
        """Find and handle duplicate agents"""
        print("Analyzing for duplicates...")
        groups = {}
        
        for i, agent in enumerate(self.all_agents):
            found_group = False
            
            for group_id, group_agents in groups.items():
                # Check similarity with first agent in group
                if self.similarity_score(agent, group_agents[0]) > 0.8:
                    group_agents.append(agent)
                    found_group = True
                    break
            
            if not found_group:
                groups[len(groups)] = [agent]
        
        # Select best from each group
        for group_id, group_agents in groups.items():
            if len(group_agents) > 1:
                # Sort by quality score and select best
                group_agents.sort(key=lambda x: x.quality_score, reverse=True)
                self.unique_agents.append(group_agents[0])
                self.duplicates.extend(group_agents[1:])
                print(f"  Found duplicate group: {group_agents[0].name} ({len(group_agents)} versions)")
            else:
                self.unique_agents.append(group_agents[0])
    
    def collect_agents(self):
        """Collect all agents from cloned repositories"""
        print("Collecting agents from repositories...")
        
        repo_dirs = [d for d in self.base_dir.glob("temp_*") if d.is_dir()]
        
        for repo_dir in repo_dirs:
            repo_name = repo_dir.name.replace("temp_", "")
            print(f"  Processing {repo_name}...")
            
            # Find all potential agent files
            patterns = ["**/*.md", "**/*.yaml", "**/*.yml"]
            for pattern in patterns:
                for file_path in repo_dir.glob(pattern):
                    # Skip non-agent files
                    if any(skip in file_path.name.lower() for skip in 
                          ["readme", "license", "contributing", ".github", "node_modules"]):
                        continue
                    
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        
                        # Extract metadata
                        yaml_frontmatter, clean_content = self.extract_yaml_frontmatter(content)
                        
                        # Determine name and description
                        name = yaml_frontmatter.get('name', file_path.stem)
                        description = yaml_frontmatter.get('description', '')
                        tools = yaml_frontmatter.get('tools', [])
                        
                        # Skip if doesn't look like an agent
                        if not yaml_frontmatter and not any(marker in content[:200] 
                                                           for marker in ['You are', 'Your role', '## ']):
                            continue
                        
                        # Create agent object
                        agent = Agent(
                            original_path=str(file_path),
                            source_repo=repo_name,
                            name=name,
                            description=description,
                            content=content,
                            content_hash=hashlib.md5(content.encode()).hexdigest(),
                            yaml_frontmatter=yaml_frontmatter,
                            tools=tools
                        )
                        
                        # Calculate quality score
                        agent.quality_score = self.calculate_quality_score(agent)
                        
                        # Categorize
                        agent.category, agent.subcategory = self.categorize_agent(agent)
                        
                        self.all_agents.append(agent)
                    
                    except Exception as e:
                        print(f"    Error processing {file_path}: {e}")
        
        print(f"  Total agents collected: {len(self.all_agents)}")
    
    def organize_agents(self):
        """Organize agents into directory structure and number them"""
        print("Organizing agents...")
        
        # Create directory structure
        agents_dir = self.base_dir / "agents"
        agents_dir.mkdir(exist_ok=True)
        
        # Sort agents by category and name
        self.unique_agents.sort(key=lambda x: (x.category, x.subcategory, x.name))
        
        # Number and save agents
        for i, agent in enumerate(self.unique_agents, 1):
            agent.agent_id = i
            
            # Create category directory
            cat_dir = agents_dir / agent.category / agent.subcategory
            cat_dir.mkdir(parents=True, exist_ok=True)
            
            # Format filename
            filename = f"{i:03d}-{agent.category}-{agent.subcategory}-{agent.name}.md"
            filename = re.sub(r'[^\w\-\.]', '_', filename)
            
            # Save agent file
            file_path = cat_dir / filename
            file_path.write_text(agent.content, encoding='utf-8')
            
            print(f"  [{i:03d}] {agent.name} -> {agent.category}/{agent.subcategory}")
    
    def create_index(self):
        """Create JSON index of all agents"""
        print("Creating agents index...")
        
        index = {
            "total_agents": len(self.unique_agents),
            "total_duplicates_removed": len(self.duplicates),
            "categories": {},
            "agents": []
        }
        
        # Count by category
        for agent in self.unique_agents:
            if agent.category not in index["categories"]:
                index["categories"][agent.category] = {}
            if agent.subcategory not in index["categories"][agent.category]:
                index["categories"][agent.category][agent.subcategory] = 0
            index["categories"][agent.category][agent.subcategory] += 1
        
        # Add agent entries
        for agent in self.unique_agents:
            index["agents"].append({
                "id": agent.agent_id,
                "name": agent.name,
                "description": agent.description,
                "category": agent.category,
                "subcategory": agent.subcategory,
                "tools": agent.tools,
                "source": agent.source_repo,
                "quality_score": agent.quality_score
            })
        
        # Save index
        index_path = self.base_dir / "agents-index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)
        
        print(f"  Index created with {len(self.unique_agents)} agents")
    
    def create_readme(self):
        """Create comprehensive README"""
        print("Creating README...")
        
        readme = []
        readme.append("# Claude Code Agents Collection")
        readme.append("")
        readme.append("A comprehensive, curated collection of Claude Code subagents from the community.")
        readme.append("")
        readme.append(f"**Total Agents:** {len(self.unique_agents)}")
        readme.append(f"**Duplicates Removed:** {len(self.duplicates)}")
        readme.append(f"**Sources:** 12 community repositories")
        readme.append("")
        
        # Statistics
        readme.append("## 📊 Statistics")
        readme.append("")
        readme.append("| Category | Count |")
        readme.append("|----------|-------|")
        
        cat_counts = {}
        for agent in self.unique_agents:
            if agent.category not in cat_counts:
                cat_counts[agent.category] = 0
            cat_counts[agent.category] += 1
        
        for category, count in sorted(cat_counts.items()):
            readme.append(f"| {category.title()} | {count} |")
        
        readme.append("")
        
        # Navigation
        readme.append("## 🗂️ Categories")
        readme.append("")
        
        for category in sorted(self.categories.keys()):
            readme.append(f"### {category.title()}")
            readme.append("")
            
            # Get agents in this category
            cat_agents = [a for a in self.unique_agents if a.category == category]
            
            # Group by subcategory
            subcat_groups = {}
            for agent in cat_agents:
                if agent.subcategory not in subcat_groups:
                    subcat_groups[agent.subcategory] = []
                subcat_groups[agent.subcategory].append(agent)
            
            for subcategory in sorted(subcat_groups.keys()):
                readme.append(f"#### {subcategory.title()}")
                readme.append("")
                
                for agent in sorted(subcat_groups[subcategory], key=lambda x: x.agent_id):
                    path = f"agents/{agent.category}/{agent.subcategory}/{agent.agent_id:03d}-{agent.category}-{agent.subcategory}-{agent.name}.md"
                    path = re.sub(r'[^\w\-\./]', '_', path)
                    readme.append(f"- [{agent.agent_id:03d}. {agent.name}]({path}) - {agent.description[:100]}")
                
                readme.append("")
        
        # Installation
        readme.append("## 🚀 Installation")
        readme.append("")
        readme.append("### Quick Install")
        readme.append("```bash")
        readme.append("# Clone the repository")
        readme.append("git clone https://github.com/yourusername/claude-agents-ultimate-collection.git")
        readme.append("")
        readme.append("# Copy agents to your project")
        readme.append("cp -r claude-agents-ultimate-collection/agents/* .claude/agents/")
        readme.append("```")
        readme.append("")
        
        # Usage
        readme.append("## 📖 Usage")
        readme.append("")
        readme.append("1. Browse the categories above to find agents you need")
        readme.append("2. Copy specific agents to your project's `.claude/agents/` directory")
        readme.append("3. Use with Claude Code's Task tool")
        readme.append("")
        
        # Sources
        readme.append("## 🙏 Credits")
        readme.append("")
        readme.append("This collection aggregates agents from these amazing repositories:")
        readme.append("")
        readme.append("- [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)")
        readme.append("- [wshobson/agents](https://github.com/wshobson/agents)")
        readme.append("- [0xfurai/claude-code-subagents](https://github.com/0xfurai/claude-code-subagents)")
        readme.append("- [davepoon/claude-code-subagents-collection](https://github.com/davepoon/claude-code-subagents-collection)")
        readme.append("- [iannuttall/claude-agents](https://github.com/iannuttall/claude-agents)")
        readme.append("- [zhsama/claude-sub-agent](https://github.com/zhsama/claude-sub-agent)")
        readme.append("- [vanzan01/claude-code-sub-agent-collective](https://github.com/vanzan01/claude-code-sub-agent-collective)")
        readme.append("- [fengyunzaidushi/claude-code-subagents](https://github.com/fengyunzaidushi/claude-code-subagents)")
        readme.append("- [hesreallyhim/awesome-claude-code-agents](https://github.com/hesreallyhim/awesome-claude-code-agents)")
        readme.append("- [rahulvrane/awesome-claude-agents](https://github.com/rahulvrane/awesome-claude-agents)")
        readme.append("- [lst97/claude-code-sub-agents](https://github.com/lst97/claude-code-sub-agents)")
        readme.append("- [dl-ezo/claude-code-sub-agents](https://github.com/dl-ezo/claude-code-sub-agents)")
        readme.append("")
        
        # Save README
        readme_path = self.base_dir / "README.md"
        readme_path.write_text("\n".join(readme), encoding='utf-8')
        
        print("  README created")
    
    def cleanup(self):
        """Remove temporary directories"""
        print("Cleaning up temporary files...")
        for temp_dir in self.base_dir.glob("temp_*"):
            shutil.rmtree(temp_dir, ignore_errors=True)
        print("  Cleanup complete")
    
    def run(self):
        """Run the complete collection process"""
        print("=" * 60)
        print("CLAUDE AGENTS COLLECTION PROCESS")
        print("=" * 60)
        
        self.collect_agents()
        self.find_duplicates()
        self.organize_agents()
        self.create_index()
        self.create_readme()
        self.cleanup()
        
        print("=" * 60)
        print(f"✅ Collection complete!")
        print(f"   Total agents: {len(self.unique_agents)}")
        print(f"   Duplicates removed: {len(self.duplicates)}")
        print("=" * 60)

if __name__ == "__main__":
    collector = AgentCollector("/Users/vaclavdlabac/claude-agents-collection")
    collector.run()