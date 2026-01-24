"""Docker Compose parser for SIS."""
import yaml

def parse_file(content: str):
    """Parse Docker Compose YAML."""
    try:
        data = yaml.safe_load(content)
        resources = []
        
        if data and 'services' in data:
            for service_name, service_data in data['services'].items():
                resources.append({
                    'kind': 'service',
                    'name': service_name,
                    'data': service_data,
                    'line': 1
                })
        
        return resources
    except:
        return []