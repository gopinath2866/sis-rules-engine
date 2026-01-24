"""Azure ARM parser for SIS."""
import json

def parse_file(content: str):
    """Parse Azure ARM JSON."""
    try:
        data = json.loads(content)
        resources = []
        
        if 'resources' in data:
            for resource in data['resources']:
                resources.append({
                    'kind': resource.get('type', ''),
                    'name': resource.get('name', ''),
                    'data': resource,
                    'line': 1
                })
        
        return resources
    except:
        return []