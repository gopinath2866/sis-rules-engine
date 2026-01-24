"""Kubernetes parser for SIS."""
import yaml

def parse_file(content: str):
    """Parse Kubernetes YAML."""
    try:
        documents = list(yaml.safe_load_all(content))
        resources = []
        
        for doc in documents:
            if doc and 'kind' in doc and 'metadata' in doc:
                resources.append({
                    'kind': doc['kind'],
                    'name': doc['metadata'].get('name', ''),
                    'data': doc,
                    'line': 1
                })
        
        return resources
    except:
        return []