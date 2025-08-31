#!/usr/bin/env python3
"""
Quick Agent Collection Script - Optimized for speed
"""

import os
import json
import hashlib
import shutil
import re
from pathlib import Path
from typing import Dict, List
import concurrent.futures

class QuickCollector:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.agents = []
        self.unique = {}
        
    def process_file(self, file_path: Path, repo_name: str) -> dict:
        """Process a single agent file"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Quick check if it's an agent
            if not any(marker in content[:500].lower() for marker in 
                      ['name:', 'description:', 'you are', 'your role', '---']):
                return None
            
            # Extract name
            name = file_path.stem
            if '---' in content[:50]:
                lines = content.split('\n')
                for line in lines[:20]:
                    if 'name:' in line.lower():
                        name = line.split(':', 1)[1].strip().strip('"\'')
                        break
            
            # Simple hash for deduplication
            content_hash = hashlib.md5(content[:1000].encode()).hexdigest()
            
            return {
                'path': str(file_path),
                'repo': repo_name,
                'name': name,
                'content': content,
                'hash': content_hash,
                'size': len(content)
            }
        except:
            return None
    
    def collect_all(self):
        """Collect all agents quickly"""
        print("Quick collecting agents...")
        
        files_to_process = []
        for repo_dir in self.base_dir.glob("temp_*"):
            repo_name = repo_dir.name.replace("temp_", "")
            
            for pattern in ["**/*.md", "**/*.yaml", "**/*.yml"]:
                for file_path in repo_dir.glob(pattern):
                    # Skip obvious non-agents
                    if any(skip in file_path.name.lower() for skip in 
                          ["readme", "license", "contributing", ".github"]):
                        continue
                    files_to_process.append((file_path, repo_name))
        
        print(f"Processing {len(files_to_process)} files...")
        
        # Process files in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.process_file, f[0], f[1]) 
                      for f in files_to_process]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    self.agents.append(result)
        
        print(f"Collected {len(self.agents)} potential agents")
    
    def deduplicate(self):
        """Quick deduplication based on hash and name"""
        print("Deduplicating...")
        
        for agent in self.agents:
            key = f"{agent['name']}_{agent['hash'][:8]}"
            
            if key not in self.unique:
                self.unique[key] = agent
            elif agent['size'] > self.unique[key]['size']:
                # Keep the larger version
                self.unique[key] = agent
        
        print(f"Unique agents: {len(self.unique)}")
    
    def categorize_simple(self, name: str, content: str) -> tuple:
        """Simple categorization"""
        name_lower = name.lower()
        content_lower = content[:500].lower()
        combined = name_lower + " " + content_lower
        
        # Language detection
        languages = {
            'python': ['python', 'py', 'django', 'flask'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue'],
            'typescript': ['typescript', 'ts', 'angular'],
            'java': ['java', 'spring'],
            'csharp': ['c#', 'csharp', 'dotnet'],
            'rust': ['rust', 'cargo'],
            'go': ['go', 'golang'],
            'ruby': ['ruby', 'rails'],
            'php': ['php', 'laravel']
        }
        
        # Task detection
        tasks = {
            'testing': ['test', 'tdd', 'jest', 'pytest'],
            'debugging': ['debug', 'fix', 'bug'],
            'refactoring': ['refactor', 'optimize', 'clean'],
            'security': ['security', 'audit', 'vulnerability'],
            'deployment': ['deploy', 'ci/cd', 'docker'],
            'documentation': ['document', 'docs', 'readme']
        }
        
        # Find best match
        for lang, keywords in languages.items():
            if any(k in combined for k in keywords):
                return 'languages', lang
        
        for task, keywords in tasks.items():
            if any(k in combined for k in keywords):
                return 'tasks', task
        
        # Framework detection
        if any(k in combined for k in ['react', 'vue', 'angular', 'next', 'nuxt']):
            return 'frameworks', 'frontend'
        if any(k in combined for k in ['express', 'fastapi', 'django', 'flask']):
            return 'frameworks', 'backend'
        
        # Default
        return 'specialized', 'general'
    
    def organize(self):
        """Organize agents into directories"""
        print("Organizing agents...")
        
        agents_dir = self.base_dir / "agents"
        agents_dir.mkdir(exist_ok=True)
        
        # Sort agents by name
        sorted_agents = sorted(self.unique.values(), key=lambda x: x['name'])
        
        agent_list = []
        
        for i, agent in enumerate(sorted_agents, 1):
            # Categorize
            category, subcategory = self.categorize_simple(agent['name'], agent['content'])
            
            # Create directory
            cat_dir = agents_dir / category / subcategory
            cat_dir.mkdir(parents=True, exist_ok=True)
            
            # Clean filename
            clean_name = re.sub(r'[^\w\-]', '_', agent['name'])
            filename = f"{i:03d}_{clean_name}.md"
            
            # Save file
            file_path = cat_dir / filename
            file_path.write_text(agent['content'], encoding='utf-8')
            
            # Add to list
            agent_list.append({
                'id': i,
                'name': agent['name'],
                'category': category,
                'subcategory': subcategory,
                'source': agent['repo'],
                'path': f"{category}/{subcategory}/{filename}"
            })
            
            if i % 50 == 0:
                print(f"  Organized {i} agents...")
        
        # Save index
        index = {
            'total': len(agent_list),
            'agents': agent_list
        }
        
        with open(self.base_dir / 'agents-index.json', 'w') as f:
            json.dump(index, f, indent=2)
        
        print(f"Organized {len(agent_list)} agents")
        
        return agent_list
    
    def create_simple_readme(self, agent_list):
        """Create a simple README"""
        print("Creating README...")
        
        readme = []
        readme.append("# Ultimate Claude Agents Collection")
        readme.append("")
        readme.append(f"**Total Unique Agents:** {len(agent_list)}")
        readme.append("")
        readme.append("## Categories")
        readme.append("")
        
        # Group by category
        categories = {}
        for agent in agent_list:
            cat = agent['category']
            subcat = agent['subcategory']
            
            if cat not in categories:
                categories[cat] = {}
            if subcat not in categories[cat]:
                categories[cat][subcat] = []
            
            categories[cat][subcat].append(agent)
        
        # Write categories
        for cat in sorted(categories.keys()):
            readme.append(f"### {cat.title()}")
            readme.append("")
            
            for subcat in sorted(categories[cat].keys()):
                agents = categories[cat][subcat]
                readme.append(f"#### {subcat.title()} ({len(agents)} agents)")
                readme.append("")
                
                # List first 10 agents
                for agent in agents[:10]:
                    readme.append(f"- {agent['id']:03d}. {agent['name']}")
                
                if len(agents) > 10:
                    readme.append(f"- ... and {len(agents) - 10} more")
                
                readme.append("")
        
        # Quick install
        readme.append("## Installation")
        readme.append("")
        readme.append("```bash")
        readme.append("git clone https://github.com/yourusername/claude-agents-collection.git")
        readme.append("cp -r claude-agents-collection/agents/* .claude/agents/")
        readme.append("```")
        readme.append("")
        
        # Credits
        readme.append("## Credits")
        readme.append("")
        readme.append("Aggregated from 12 community repositories. See agents-index.json for sources.")
        readme.append("")
        
        # Save
        with open(self.base_dir / 'README.md', 'w') as f:
            f.write('\n'.join(readme))
        
        print("README created")
    
    def cleanup(self):
        """Remove temp directories"""
        print("Cleaning up...")
        for temp_dir in self.base_dir.glob("temp_*"):
            shutil.rmtree(temp_dir, ignore_errors=True)
        print("Cleanup complete")
    
    def run(self):
        """Run the quick collection"""
        print("=" * 60)
        print("QUICK AGENT COLLECTION")
        print("=" * 60)
        
        self.collect_all()
        self.deduplicate()
        agent_list = self.organize()
        self.create_simple_readme(agent_list)
        self.cleanup()
        
        print("=" * 60)
        print(f"✅ Collection complete: {len(agent_list)} unique agents")
        print("=" * 60)

if __name__ == "__main__":
    collector = QuickCollector("/Users/vaclavdlabac/claude-agents-collection")
    collector.run()