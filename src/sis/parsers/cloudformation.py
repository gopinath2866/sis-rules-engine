"""CloudFormation parser for SIS."""
import yaml
import json

def parse_file(content: str):
    """Parse CloudFormation YAML/JSON."""
    try:
        if content.strip().startswith('{'):
            data = json.loads(content)
        else:
            data = yaml.safe_load(content)
        
        resources = []
        if 'Resources' in data:
            for resource_name, resource_data in data['Resources'].items():
                resources.append({
                    'kind': resource_data.get('Type', ''),
                    'name': resource_name,
                    'data': resource_data,
                    'line': 1
                })
        
        return resources
    except:
        return []