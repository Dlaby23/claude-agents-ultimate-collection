#!/usr/bin/env python3
"""
Intelligent Agent Deduplication Script
Analyzes and removes semantic duplicates, keeping only the best version
"""

import os
import json
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from difflib import SequenceMatcher
import yaml

@dataclass
class Agent:
    """Agent with quality metrics"""
    path: Path
    name: str
    content: str
    yaml_data: dict
    quality_score: float = 0
    content_length: int = 0
    has_yaml: bool = False
    has_tools: bool = False
    has_structure: bool = False
    has_examples: bool = False
    source_repo: str = ""

class IntelligentDeduplicator:
    def __init__(self, agents_dir: str):
        self.agents_dir = Path(agents_dir)
        self.all_agents = []
        self.duplicate_groups = {}
        self.unique_agents = []
        self.decision_log = []
        
        # Common duplicate patterns
        self.duplicate_patterns = [
            (r'(.+)[-_]?pro$', r'(.+)[-_]?expert$', r'(.+)[-_]?developer$', r'(.+)[-_]?engineer$', r'(.+)[-_]?specialist$'),
            (r'(.+)[-_]?architect$', r'(.+)[-_]?architecture$'),
            (r'(.+)[-_]?test(?:er|ing)?$', r'(.+)[-_]?qa$'),
            (r'(.+)[-_]?debug(?:ger)?$', r'(.+)[-_]?troubleshoot(?:er)?$'),
            (r'(.+)[-_]?optimize(?:r)?$', r'(.+)[-_]?performance$'),
            (r'ml[-_]?engineer$', r'machine[-_]?learning[-_]?engineer$'),
            (r'ai[-_]?engineer$', r'artificial[-_]?intelligence[-_]?engineer$'),
        ]
    
    def extract_yaml(self, content: str) -> Tuple[dict, str]:
        """Extract YAML frontmatter from content"""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    yaml_data = yaml.safe_load(parts[1])
                    return yaml_data or {}, parts[2].strip()
                except:
                    pass
        return {}, content
    
    def calculate_quality_score(self, agent: Agent) -> float:
        """Calculate comprehensive quality score"""
        score = 0
        
        # 1. Content length (max 20 points)
        if agent.content_length > 3000:
            score += 20
        elif agent.content_length > 2000:
            score += 15
        elif agent.content_length > 1000:
            score += 10
        elif agent.content_length > 500:
            score += 5
        
        # 2. YAML frontmatter quality (max 25 points)
        if agent.has_yaml:
            score += 5
            if 'name' in agent.yaml_data:
                score += 5
            if 'description' in agent.yaml_data:
                score += 5
                # Longer descriptions are better
                desc_len = len(agent.yaml_data.get('description', ''))
                if desc_len > 100:
                    score += 5
                elif desc_len > 50:
                    score += 3
            if 'tools' in agent.yaml_data:
                score += 5
                # More tools specified = more specific
                tool_count = len(agent.yaml_data.get('tools', []))
                if tool_count > 5:
                    score += 5
                elif tool_count > 2:
                    score += 3
        
        # 3. Content structure (max 20 points)
        content_lower = agent.content.lower()
        
        # Check for clear sections
        if '## responsibilities' in content_lower or '## your role' in content_lower:
            score += 5
        if '## guidelines' in content_lower or '## principles' in content_lower:
            score += 5
        if '## workflow' in content_lower or '## process' in content_lower:
            score += 5
        if '## examples' in content_lower or '```' in agent.content:
            score += 5
            agent.has_examples = True
        
        # 4. Specificity indicators (max 15 points)
        if 'you are' in content_lower or 'your role' in content_lower:
            score += 5
        if 'must' in content_lower or 'should' in content_lower:
            score += 5
        if 'step' in content_lower or 'process' in content_lower:
            score += 5
        
        # 5. Code examples bonus (max 10 points)
        code_blocks = agent.content.count('```')
        if code_blocks >= 4:
            score += 10
        elif code_blocks >= 2:
            score += 5
        
        # 6. Source repository quality bonus (max 10 points)
        quality_repos = ['voltagent', 'wshobson', '0xfurai', 'davepoon']
        if any(repo in agent.source_repo.lower() for repo in quality_repos):
            score += 10
        
        return score
    
    def get_semantic_key(self, name: str) -> str:
        """Extract semantic key from agent name"""
        # Remove numbers and special characters
        clean = re.sub(r'^\d+[-_]', '', name)
        clean = re.sub(r'[-_]', ' ', clean)
        clean = clean.lower().strip()
        
        # Apply pattern matching to normalize variants
        for pattern_group in self.duplicate_patterns:
            for pattern in pattern_group:
                match = re.match(pattern, clean)
                if match:
                    # Return the base name without suffix
                    return match.group(1).strip() if match.groups() else clean
        
        return clean
    
    def name_similarity(self, name1: str, name2: str) -> float:
        """Calculate name similarity"""
        # Clean names
        clean1 = re.sub(r'[^a-z0-9]', '', name1.lower())
        clean2 = re.sub(r'[^a-z0-9]', '', name2.lower())
        
        # Check if one is substring of other
        if clean1 in clean2 or clean2 in clean1:
            return 0.9
        
        # Use sequence matcher
        return SequenceMatcher(None, clean1, clean2).ratio()
    
    def content_similarity(self, content1: str, content2: str) -> float:
        """Calculate content similarity (first 500 chars)"""
        # Compare first 500 characters
        snippet1 = content1[:500].lower()
        snippet2 = content2[:500].lower()
        
        return SequenceMatcher(None, snippet1, snippet2).ratio()
    
    def load_agents(self):
        """Load all agents from directory"""
        print("Loading agents...")
        
        for agent_file in self.agents_dir.rglob("*.md"):
            try:
                content = agent_file.read_text(encoding='utf-8', errors='ignore')
                yaml_data, clean_content = self.extract_yaml(content)
                
                # Extract source repo from path
                parts = agent_file.parts
                source_repo = ""
                if len(parts) > 2:
                    # Try to identify source from numbering or path
                    source_repo = parts[-3] if len(parts) > 3 else ""
                
                agent = Agent(
                    path=agent_file,
                    name=agent_file.stem,
                    content=content,
                    yaml_data=yaml_data,
                    content_length=len(content),
                    has_yaml=bool(yaml_data),
                    has_tools='tools' in yaml_data,
                    has_structure='##' in content,
                    source_repo=source_repo
                )
                
                agent.quality_score = self.calculate_quality_score(agent)
                self.all_agents.append(agent)
                
            except Exception as e:
                print(f"Error loading {agent_file}: {e}")
        
        print(f"Loaded {len(self.all_agents)} agents")
    
    def find_duplicates(self):
        """Find semantic duplicate groups"""
        print("Finding duplicate groups...")
        
        processed = set()
        groups = {}
        group_id = 0
        
        for i, agent1 in enumerate(self.all_agents):
            if agent1.path in processed:
                continue
            
            # Get semantic key
            key1 = self.get_semantic_key(agent1.name)
            
            # Start new group
            current_group = [agent1]
            processed.add(agent1.path)
            
            # Find similar agents
            for agent2 in self.all_agents[i+1:]:
                if agent2.path in processed:
                    continue
                
                key2 = self.get_semantic_key(agent2.name)
                
                # Check semantic similarity
                is_duplicate = False
                
                # 1. Same semantic key
                if key1 == key2:
                    is_duplicate = True
                
                # 2. High name similarity
                elif self.name_similarity(agent1.name, agent2.name) > 0.7:
                    is_duplicate = True
                
                # 3. Very similar content
                elif self.content_similarity(agent1.content, agent2.content) > 0.8:
                    is_duplicate = True
                
                # 4. Check for common patterns (python-pro vs python-expert)
                name1_clean = re.sub(r'[-_](pro|expert|developer|engineer|specialist)$', '', agent1.name.lower())
                name2_clean = re.sub(r'[-_](pro|expert|developer|engineer|specialist)$', '', agent2.name.lower())
                if name1_clean == name2_clean and name1_clean:
                    is_duplicate = True
                
                if is_duplicate:
                    current_group.append(agent2)
                    processed.add(agent2.path)
            
            # Save group if it has duplicates
            if len(current_group) > 1:
                groups[group_id] = current_group
                group_id += 1
                print(f"  Found duplicate group: {key1} ({len(current_group)} variants)")
        
        self.duplicate_groups = groups
        print(f"Found {len(groups)} duplicate groups")
    
    def select_best_from_groups(self):
        """Select best agent from each duplicate group"""
        print("Selecting best agents from groups...")
        
        # Add agents that aren't in any duplicate group
        in_groups = set()
        for group in self.duplicate_groups.values():
            for agent in group:
                in_groups.add(agent.path)
        
        # Add unique agents (not in any group)
        for agent in self.all_agents:
            if agent.path not in in_groups:
                self.unique_agents.append(agent)
        
        # Select best from each group
        for group_id, agents in self.duplicate_groups.items():
            # Sort by quality score
            agents.sort(key=lambda x: x.quality_score, reverse=True)
            
            best = agents[0]
            self.unique_agents.append(best)
            
            # Log decision
            decision = {
                'group': self.get_semantic_key(best.name),
                'selected': best.name,
                'score': best.quality_score,
                'rejected': [a.name for a in agents[1:]],
                'reason': f"Highest quality score ({best.quality_score:.1f})"
            }
            self.decision_log.append(decision)
            
            print(f"  Selected: {best.name} (score: {best.quality_score:.1f}) from {len(agents)} variants")
    
    def save_deduplicated_collection(self, output_dir: str):
        """Save the deduplicated collection"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"Saving {len(self.unique_agents)} unique agents...")
        
        # Clear existing agents directory
        agents_output = output_path / "agents"
        if agents_output.exists():
            import shutil
            shutil.rmtree(agents_output)
        agents_output.mkdir()
        
        # Sort agents by name for consistent numbering
        self.unique_agents.sort(key=lambda x: x.name.lower())
        
        # Save agents with new numbering
        saved_agents = []
        for i, agent in enumerate(self.unique_agents, 1):
            # Determine category
            name_lower = agent.name.lower()
            
            # Categorize
            category = "specialized"
            subcategory = "general"
            
            # Language detection
            if any(lang in name_lower for lang in ['python', 'py', 'django', 'flask', 'fastapi']):
                category, subcategory = "languages", "python"
            elif any(lang in name_lower for lang in ['javascript', 'js', 'node', 'react', 'vue']):
                category, subcategory = "languages", "javascript"
            elif any(lang in name_lower for lang in ['typescript', 'ts']):
                category, subcategory = "languages", "typescript"
            elif any(lang in name_lower for lang in ['rust', 'cargo']):
                category, subcategory = "languages", "rust"
            elif any(lang in name_lower for lang in ['go', 'golang']):
                category, subcategory = "languages", "go"
            elif any(lang in name_lower for lang in ['java', 'spring']):
                category, subcategory = "languages", "java"
            elif any(lang in name_lower for lang in ['ruby', 'rails']):
                category, subcategory = "languages", "ruby"
            elif any(lang in name_lower for lang in ['php', 'laravel']):
                category, subcategory = "languages", "php"
            elif any(lang in name_lower for lang in ['csharp', 'c#', 'dotnet']):
                category, subcategory = "languages", "csharp"
            
            # Task detection
            elif any(task in name_lower for task in ['test', 'qa', 'jest', 'pytest']):
                category, subcategory = "tasks", "testing"
            elif any(task in name_lower for task in ['debug', 'fix', 'troubleshoot']):
                category, subcategory = "tasks", "debugging"
            elif any(task in name_lower for task in ['refactor', 'optimize', 'clean']):
                category, subcategory = "tasks", "refactoring"
            elif any(task in name_lower for task in ['security', 'audit', 'vulnerability']):
                category, subcategory = "tasks", "security"
            elif any(task in name_lower for task in ['deploy', 'ci', 'cd', 'docker']):
                category, subcategory = "tasks", "deployment"
            elif any(task in name_lower for task in ['document', 'docs', 'readme']):
                category, subcategory = "tasks", "documentation"
            
            # Create directory
            cat_dir = agents_output / category / subcategory
            cat_dir.mkdir(parents=True, exist_ok=True)
            
            # Clean filename
            clean_name = re.sub(r'[^\w\-]', '_', agent.name)
            filename = f"{i:03d}_{clean_name}.md"
            
            # Save file
            file_path = cat_dir / filename
            file_path.write_text(agent.content, encoding='utf-8')
            
            saved_agents.append({
                'id': i,
                'name': agent.name,
                'category': category,
                'subcategory': subcategory,
                'path': f"{category}/{subcategory}/{filename}",
                'quality_score': agent.quality_score
            })
        
        # Save decision log
        log_path = output_path / "deduplication_log.json"
        with open(log_path, 'w') as f:
            json.dump({
                'original_count': len(self.all_agents),
                'unique_count': len(self.unique_agents),
                'duplicate_groups': len(self.duplicate_groups),
                'decisions': self.decision_log
            }, f, indent=2)
        
        # Save new index
        index_path = output_path / "agents-index.json"
        with open(index_path, 'w') as f:
            json.dump({
                'total': len(saved_agents),
                'agents': saved_agents
            }, f, indent=2)
        
        print(f"✅ Deduplication complete!")
        print(f"   Original: {len(self.all_agents)} agents")
        print(f"   Unique: {len(self.unique_agents)} agents")
        print(f"   Removed: {len(self.all_agents) - len(self.unique_agents)} duplicates")
    
    def run(self, output_dir: str):
        """Run the complete deduplication process"""
        print("=" * 60)
        print("INTELLIGENT AGENT DEDUPLICATION")
        print("=" * 60)
        
        self.load_agents()
        self.find_duplicates()
        self.select_best_from_groups()
        self.save_deduplicated_collection(output_dir)
        
        print("=" * 60)

if __name__ == "__main__":
    deduper = IntelligentDeduplicator("/Users/vaclavdlabac/claude-agents-collection/agents")
    deduper.run("/Users/vaclavdlabac/claude-agents-collection-clean")