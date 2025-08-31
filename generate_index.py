import os
import json
import re

def extract_agent_info(filepath):
    """Extract agent name and description from markdown file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract name from frontmatter or filename
    name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
    else:
        # Use filename without number prefix and .md
        basename = os.path.basename(filepath)
        name = re.sub(r'^\d+_', '', basename).replace('.md', '')
    
    # Extract description from frontmatter
    desc_match = re.search(r'^description:\s*(.+)$', content, re.MULTILINE)
    description = desc_match.group(1).strip() if desc_match else ""
    
    return {
        "name": name,
        "path": filepath.replace('/Users/vaclavdlabac/claude-agents-collection/', ''),
        "description": description
    }

def generate_index():
    """Generate index of all agents"""
    agents = []
    
    for root, dirs, files in os.walk('agents'):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                try:
                    agent_info = extract_agent_info(filepath)
                    agents.append(agent_info)
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    # Sort by name
    agents.sort(key=lambda x: x['name'].lower())
    
    index = {
        "version": "2.0",
        "total_agents": len(agents),
        "agents": agents
    }
    
    with open('agents-index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"Generated index with {len(agents)} agents")
    return len(agents)

if __name__ == "__main__":
    count = generate_index()
