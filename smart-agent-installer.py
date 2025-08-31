#!/usr/bin/env python3
"""
Smart Agent Installer for Claude Code
Uses the deduplicated Ultimate Claude Agents Collection
Automatically installs only the agents you need based on your prompts
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Set
import tempfile
import re

class SmartAgentInstaller:
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).absolute()
        self.agents_dir = self.project_path / ".claude" / "agents"
        self.cache_file = self.project_path / ".claude" / "agent-cache.json"
        
        # Single unified repository - YOUR deduplicated collection
        self.repo_url = "https://github.com/Dlaby23/claude-agents-ultimate-collection.git"
        self.index_url = "https://raw.githubusercontent.com/Dlaby23/claude-agents-ultimate-collection/main/agents-index.json"
        
        self.agent_index = None
        self.installed_agents = set()
        
        # Enhanced keyword mapping for better agent selection
        self.task_keywords = {
            # Languages
            "python": {
                "keywords": ["python", "py", "pip", "poetry", "venv", "requirements.txt"],
                "agents": ["python-pro", "python-expert", "python-backend-engineer"]
            },
            "javascript": {
                "keywords": ["javascript", "js", "node", "npm", "yarn", "pnpm", "package.json"],
                "agents": ["javascript-pro", "nodejs-expert"]
            },
            "typescript": {
                "keywords": ["typescript", "ts", "tsx", "types", "interface", "tsconfig"],
                "agents": ["typescript-pro"]
            },
            "react": {
                "keywords": ["react", "jsx", "hooks", "component", "useState", "useEffect", "redux", "create react"],
                "agents": ["react-pro", "frontend-developer", "typescript-pro"]
            },
            "vue": {
                "keywords": ["vue", "vuex", "pinia", "composition", "vuetify", "nuxt"],
                "agents": ["vue-expert", "frontend-developer"]
            },
            "angular": {
                "keywords": ["angular", "ng", "rxjs", "ngrx", "decorator"],
                "agents": ["angular-architect", "frontend-developer"]
            },
            
            # Frameworks
            "fastapi": {
                "keywords": ["fastapi", "pydantic", "uvicorn", "async", "await"],
                "agents": ["python-pro", "python-backend-engineer", "api-designer"]
            },
            "django": {
                "keywords": ["django", "drf", "orm", "models", "views", "migrations"],
                "agents": ["django-developer", "python-backend-engineer"]
            },
            "flask": {
                "keywords": ["flask", "werkzeug", "jinja", "blueprint"],
                "agents": ["python-pro", "python-backend-engineer"]
            },
            "express": {
                "keywords": ["express", "middleware", "router", "app.get", "app.post"],
                "agents": ["express-expert", "nodejs-expert", "backend-architect"]
            },
            "nextjs": {
                "keywords": ["next", "nextjs", "vercel", "ssr", "ssg", "app router"],
                "agents": ["nextjs-developer", "react-pro", "frontend-developer"]
            },
            
            # Tasks
            "testing": {
                "keywords": ["test", "testing", "tdd", "bdd", "unit", "integration", "e2e", "jest", "pytest", "vitest"],
                "agents": ["test-automator", "qa-expert", "testing-implementation-agent"]
            },
            "debugging": {
                "keywords": ["debug", "fix", "bug", "error", "issue", "troubleshoot", "diagnose", "problem"],
                "agents": ["debugger", "error-detective", "troubleshooter"]
            },
            "refactoring": {
                "keywords": ["refactor", "optimize", "clean", "improve", "performance", "restructure", "cleanup"],
                "agents": ["refactoring-specialist", "code-refactorer-agent", "performance-engineer"]
            },
            "security": {
                "keywords": ["security", "audit", "vulnerability", "penetration", "xss", "csrf", "injection", "auth"],
                "agents": ["security-auditor", "security-engineer"]
            },
            "deployment": {
                "keywords": ["deploy", "ci", "cd", "pipeline", "docker", "kubernetes", "k8s", "helm", "aws", "azure"],
                "agents": ["deployment-engineer", "devops-engineer", "containerize-application", "kubernetes-specialist", "cloud-architect"]
            },
            "database": {
                "keywords": ["database", "sql", "nosql", "postgres", "mysql", "mongodb", "redis", "query", "migration"],
                "agents": ["database-optimizer", "sql-pro", "postgres-pro", "mongodb-expert"]
            },
            "api": {
                "keywords": ["api", "rest", "graphql", "grpc", "websocket", "endpoint", "swagger", "openapi"],
                "agents": ["api-designer", "api-documenter", "graphql-architect", "websocket-engineer"]
            }
        }
        
        self.load_cache()
        self.load_index()
    
    def load_cache(self):
        """Load the local cache of installed agents"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    self.installed_agents = set(cache.get('installed', []))
            except:
                self.installed_agents = set()
        else:
            self.installed_agents = set()
    
    def save_cache(self):
        """Save the cache of installed agents"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump({'installed': list(self.installed_agents)}, f, indent=2)
    
    def load_index(self):
        """Load the agent index from the repository"""
        try:
            # Try to fetch the index using curl (more reliable than requests)
            result = subprocess.run(
                ["curl", "-s", self.index_url],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.agent_index = json.loads(result.stdout)
                print(f"✓ Loaded index: {self.agent_index['total']} agents available")
            else:
                print("⚠️ Could not fetch index, will clone repository if needed")
                self.agent_index = None
        except Exception as e:
            print(f"⚠️ Could not load index: {e}")
            self.agent_index = None
    
    def analyze_prompt(self, prompt: str) -> Dict[str, List[str]]:
        """Analyze prompt to determine needed agents"""
        prompt_lower = prompt.lower()
        detected = {
            "categories": [],
            "suggested_agents": [],
            "keywords_found": []
        }
        
        # Check each category
        for category, info in self.task_keywords.items():
            for keyword in info["keywords"]:
                if keyword in prompt_lower:
                    detected["categories"].append(category)
                    detected["suggested_agents"].extend(info["agents"])
                    detected["keywords_found"].append(keyword)
                    break  # Only match once per category
        
        # Remove duplicates
        detected["categories"] = list(set(detected["categories"]))
        detected["suggested_agents"] = list(set(detected["suggested_agents"]))
        
        return detected
    
    def find_agent_in_index(self, agent_name: str) -> Optional[Dict]:
        """Find an agent in the index by name"""
        if not self.agent_index:
            return None
        
        agent_name_lower = agent_name.lower()
        
        for agent in self.agent_index.get('agents', []):
            # Check exact match or partial match
            if (agent_name_lower in agent['name'].lower() or 
                agent['name'].lower() in agent_name_lower):
                return agent
        
        return None
    
    def install_agents_from_repo(self, agents_to_install: List[str]) -> List[str]:
        """Clone repo and install specific agents"""
        if not agents_to_install:
            return []
        
        installed = []
        temp_dir = Path(tempfile.mkdtemp(prefix="claude_agents_"))
        
        try:
            print("📦 Fetching agents from repository...")
            
            # Clone the repository (shallow clone for speed)
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "--quiet", self.repo_url, str(temp_dir)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"❌ Failed to clone repository: {result.stderr}")
                return []
            
            # Create agents directory
            self.agents_dir.mkdir(parents=True, exist_ok=True)
            
            # Install each agent
            for agent_name in agents_to_install:
                # Find agent in index
                agent_info = self.find_agent_in_index(agent_name)
                
                if agent_info:
                    # Construct path
                    agent_path = temp_dir / "agents" / agent_info['path']
                    
                    if agent_path.exists():
                        # Copy to project
                        dest = self.agents_dir / agent_path.name
                        if not dest.exists():  # Don't overwrite existing
                            shutil.copy2(agent_path, dest)
                            installed.append(agent_name)
                            self.installed_agents.add(agent_name)
                            print(f"  ✓ Installed: {agent_name}")
                        else:
                            print(f"  ⚠️ Already exists: {agent_name}")
                    else:
                        print(f"  ❌ Not found in repo: {agent_name}")
                else:
                    print(f"  ⚠️ Not in index: {agent_name}")
        
        finally:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Save cache
        if installed:
            self.save_cache()
        
        return installed
    
    def auto_install(self, prompt: str) -> Dict:
        """Main function to analyze prompt and install needed agents"""
        result = {
            "prompt": prompt,
            "analysis": {},
            "agents_installed": [],
            "agents_skipped": [],
            "message": ""
        }
        
        print(f"\n🔍 Analyzing: '{prompt[:100]}{'...' if len(prompt) > 100 else ''}'")
        
        # Analyze prompt
        analysis = self.analyze_prompt(prompt)
        result["analysis"] = analysis
        
        if not analysis["suggested_agents"]:
            result["message"] = "No specific agents identified for this task"
            print("ℹ️ No specific agents identified")
            return result
        
        print(f"📊 Detected: {', '.join(analysis['categories'])}")
        print(f"🎯 Suggested agents: {', '.join(analysis['suggested_agents'][:5])}")
        
        # Check what's already installed
        to_install = []
        for agent in analysis["suggested_agents"]:
            if agent in self.installed_agents:
                result["agents_skipped"].append(agent)
            else:
                to_install.append(agent)
        
        if result["agents_skipped"]:
            print(f"⏭️ Already installed: {', '.join(result['agents_skipped'])}")
        
        if not to_install:
            result["message"] = "All suggested agents already installed"
            print("✅ All suggested agents already installed")
            return result
        
        # Install new agents
        installed = self.install_agents_from_repo(to_install[:5])  # Limit to 5 per run
        result["agents_installed"] = installed
        
        if installed:
            result["message"] = f"Successfully installed {len(installed)} agents"
            print(f"\n✅ Installed {len(installed)} new agents")
        else:
            result["message"] = "No new agents installed"
            print("\n⚠️ No new agents installed")
        
        return result
    
    def list_installed(self):
        """List all installed agents in the project"""
        if not self.agents_dir.exists():
            print("No agents directory found")
            return []
        
        agents = []
        for agent_file in self.agents_dir.glob("*.md"):
            agents.append(agent_file.stem)
        
        return sorted(agents)

def main():
    """CLI interface for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Smart Agent Installer for Claude Code")
        print("=" * 50)
        print("\nUsage:")
        print("  python smart-agent-installer.py 'your task description'")
        print("\nExamples:")
        print("  python smart-agent-installer.py 'build a FastAPI app with PostgreSQL'")
        print("  python smart-agent-installer.py 'create React TypeScript app with testing'")
        print("  python smart-agent-installer.py 'debug performance issues'")
        print("\nInstalled agents:")
        
        installer = SmartAgentInstaller()
        agents = installer.list_installed()
        if agents:
            for agent in agents:
                print(f"  • {agent}")
        else:
            print("  (none)")
        
        sys.exit(1)
    
    prompt = " ".join(sys.argv[1:])
    installer = SmartAgentInstaller()
    
    print("=" * 60)
    print("SMART AGENT INSTALLER")
    print("=" * 60)
    
    result = installer.auto_install(prompt)
    
    print("=" * 60)
    print(f"Total installed in project: {len(installer.list_installed())} agents")

if __name__ == "__main__":
    main()