"""
Kubernetes manifest parser for SIS
"""
from typing import Dict, Any, List, Optional
import yaml

def parse_kubernetes(content: str, file_format: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Parse Kubernetes manifests and extract RBAC resources.
    
    Args:
        content: Kubernetes YAML content
        file_format: Optional format specifier (unused for Kubernetes)
    
    Returns:
        List of extracted resources
    """
    resources = []
    
    try:
        # Split YAML documents
        documents = list(yaml.safe_load_all(content))
        
        for doc in documents:
            if not isinstance(doc, dict):
                continue
            
            kind = doc.get('kind', '')
            metadata = doc.get('metadata', {})
            name = metadata.get('name', '')
            
            # Extract RBAC resources
            if any(rbac_kind in kind for rbac_kind in [
                'ClusterRole', 'ClusterRoleBinding', 'Role', 'RoleBinding', 'ServiceAccount'
            ]):
                resources.append({
                    'name': name,
                    'type': kind,
                    'spec': doc.get('spec', {}),
                    'metadata': metadata,
                    'source': 'kubernetes'
                })
        
        return resources
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse Kubernetes YAML: {str(e)}")
