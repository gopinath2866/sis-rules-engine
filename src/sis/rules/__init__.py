"""
SIS 25 Canonical Rules Implementation
"""
from typing import Dict, List, Any

def load_rules(file_type: str = 'all') -> List[Dict[str, Any]]:
    """Load rules based on file type"""
    if file_type == 'terraform':
        return TERRAFORM_RULES
    elif file_type == 'kubernetes':
        return KUBERNETES_RULES
    elif file_type == 'docker':
        return DOCKER_RULES
    elif file_type == 'cloudformation':
        return CLOUDFORMATION_RULES
    elif file_type == 'all':
        return ALL_RULES
    else:
        return []

# ==================== TERRAFORM RULES ====================
TERRAFORM_RULES = [
    # IRR-DEC-01: Irreversible admin policy
    {
        'rule_id': 'IRR-DEC-01',
        'rule_type': 'irreversible_decision',
        'applies_to': {
            'resource_kinds': ['aws_iam_policy', 'aws_iam_role_policy', 'aws_iam_user_policy']
        },
        'detection': {
            'match_logic': 'ANY',
            'conditions': [
                {'path': 'policy.Statement[].Effect', 'operator': 'EQUALS', 'value': 'Allow'},
                {'path': 'policy.Statement[].Action', 'operator': 'EQUALS', 'value': '*'},
                {'path': 'policy.Statement[].Resource', 'operator': 'EQUALS', 'value': '*'}
            ]
        },
        'severity': 'CRITICAL',
        'message': 'Irreversible admin policy allows all actions on all resources',
        'remediation': 'Follow principle of least privilege. Use specific actions and resources.'
    },
    
    # IRR-DEC-02: Irreversible resource (prevent_destroy)
    {
        'rule_id': 'IRR-DEC-02',
        'rule_type': 'irreversible_decision',
        'applies_to': {
            'resource_kinds': ['aws_s3_bucket', 'aws_db_instance', 'aws_vpc']
        },
        'detection': {
            'match_logic': 'ALL',
            'conditions': [
                {'path': 'lifecycle.prevent_destroy', 'operator': 'EQUALS', 'value': True}
            ]
        },
        'severity': 'HIGH',
        'message': 'Resource cannot be destroyed (prevent_destroy = true)',
        'remediation': 'Use with caution. Ensure you have backup and migration plans.'
    },
    
    # ID-BIND-01: Identity delegation risk
    {
        'rule_id': 'ID-BIND-01',
        'rule_type': 'identity_binding',
        'applies_to': {
            'resource_kinds': ['aws_iam_role']
        },
        'detection': {
            'match_logic': 'ANY',
            'conditions': [
                {'path': 'assume_role_policy.Statement[].Principal.AWS', 'operator': 'CONTAINS', 'value': 'arn:aws:iam::*:role/Admin'},
                {'path': 'assume_role_policy.Statement[].Principal.AWS', 'operator': 'REGEX', 'value': '.*:root'}
            ]
        },
        'severity': 'HIGH',
        'message': 'Role can be assumed by admin/root identities',
        'remediation': 'Restrict assume role to specific, non-admin identities.'
    },
    
    # TF-001: Public S3 bucket
    {
        'rule_id': 'TF-001',
        'rule_type': 'vulnerability',
        'applies_to': {
            'resource_kinds': ['aws_s3_bucket']
        },
        'detection': {
            'match_logic': 'ANY',
            'conditions': [
                {'path': 'acl', 'operator': 'EQUALS', 'value': 'public-read'},
                {'path': 'acl', 'operator': 'EQUALS', 'value': 'public-read-write'}
            ]
        },
        'severity': 'HIGH',
        'message': 'S3 bucket has public access',
        'remediation': 'Set ACL to "private" or use bucket policies for specific access.'
    },
    
    # TF-002: Overly permissive security group
    {
        'rule_id': 'TF-002',
        'rule_type': 'vulnerability',
        'applies_to': {
            'resource_kinds': ['aws_security_group']
        },
        'detection': {
            'match_logic': 'ANY',
            'conditions': [
                {'path': 'ingress[].cidr_blocks[]', 'operator': 'EQUALS', 'value': '0.0.0.0/0'},
                {'path': 'egress[].cidr_blocks[]', 'operator': 'EQUALS', 'value': '0.0.0.0/0'}
            ]
        },
        'severity': 'HIGH',
        'message': 'Security group allows all traffic from/to internet',
        'remediation': 'Restrict CIDR blocks to specific IP ranges.'
    },
    
    # TF-003: Plaintext secrets
    {
        'rule_id': 'TF-003',
        'rule_type': 'secrets',
        'applies_to': {
            'resource_kinds': ['*']  # Applies to all resources
        },
        'detection': {
            'match_logic': 'ANY',
            'conditions': [
                {'path': 'config', 'operator': 'REGEX', 'value': '(?i)(password|secret|token|key)\\s*[=:]\\s*["\']?[\\w-]+["\']?'}
            ]
        },
        'severity': 'CRITICAL',
        'message': 'Plaintext secret detected in configuration',
        'remediation': 'Use secrets manager (AWS Secrets Manager, HashiCorp Vault).'
    }
]

# ==================== KUBERNETES RULES ====================
KUBERNETES_RULES = [
    # K8S-001: Privileged container
    {
        'rule_id': 'K8S-001',
        'rule_type': 'container_security',
        'applies_to': {
            'resource_kinds': ['Pod', 'Deployment', 'StatefulSet', 'DaemonSet']
        },
        'detection': {
            'match_logic': 'ALL',
            'conditions': [
                {'path': 'spec.containers[].securityContext.privileged', 'operator': 'EQUALS', 'value': True}
            ]
        },
        'severity': 'HIGH',
        'message': 'Container runs with privileged security context',
        'remediation': 'Remove privileged: true or use specific capabilities.'
    },
    
    # K8S-002: Root container
    {
        'rule_id': 'K8S-002',
        'rule_type': 'container_security',
        'applies_to': {
            'resource_kinds': ['Pod', 'Deployment', 'StatefulSet', 'DaemonSet']
        },
        'detection': {
            'match_logic': 'ALL',
            'conditions': [
                {'path': 'spec.containers[].securityContext.runAsUser', 'operator': 'EQUALS', 'value': 0}
            ]
        },
        'severity': 'MEDIUM',
        'message': 'Container runs as root user',
        'remediation': 'Add securityContext.runAsUser with non-root UID (e.g., 1000).'
    },
    
    # K8S-003: Host network access
    {
        'rule_id': 'K8S-003',
        'rule_type': 'network_security',
        'applies_to': {
            'resource_kinds': ['Pod', 'Deployment', 'StatefulSet', 'DaemonSet']
        },
        'detection': {
            'match_logic': 'ALL',
            'conditions': [
                {'path': 'spec.hostNetwork', 'operator': 'EQUALS', 'value': True}
            ]
        },
        'severity': 'HIGH',
        'message': 'Pod uses host network namespace',
        'remediation': 'Avoid hostNetwork unless absolutely necessary.'
    }
]

# ==================== DOCKER COMPOSE RULES ====================
DOCKER_RULES = [
    # DC-001: Privileged service
    {
        'rule_id': 'DC-001',
        'rule_type': 'container_security',
        'applies_to': {
            'resource_kinds': ['docker_service']
        },
        'detection': {
            'match_logic': 'ALL',
            'conditions': [
                {'path': 'config.privileged', 'operator': 'EQUALS', 'value': True}
            ]
        },
        'severity': 'HIGH',
        'message': 'Docker service runs with privileged mode',
        'remediation': 'Remove privileged: true or use specific capabilities.'
    },
    
    # DC-002: Root user
    {
        'rule_id': 'DC-002',
        'rule_type': 'container_security',
        'applies_to': {
            'resource_kinds': ['docker_service']
        },
        'detection': {
            'match_logic': 'ALL',
            'conditions': [
                {'path': 'config.user', 'operator': 'EQUALS', 'value': 'root'},
                {'path': 'config.user', 'operator': 'EQUALS', 'value': '0:0'}
            ]
        },
        'severity': 'MEDIUM',
        'message': 'Docker service runs as root',
        'remediation': 'Add user: non-root user (e.g., "1000:1000").'
    }
]

# ==================== CLOUDFORMATION RULES ====================
CLOUDFORMATION_RULES = [
    # CF-001: Public S3 bucket
    {
        'rule_id': 'CF-001',
        'rule_type': 'vulnerability',
        'applies_to': {
            'resource_kinds': ['AWS::S3::Bucket']
        },
        'detection': {
            'match_logic': 'ANY',
            'conditions': [
                {'path': 'Properties.AccessControl', 'operator': 'EQUALS', 'value': 'PublicRead'},
                {'path': 'Properties.AccessControl', 'operator': 'EQUALS', 'value': 'PublicReadWrite'}
            ]
        },
        'severity': 'HIGH',
        'message': 'CloudFormation S3 bucket has public access',
        'remediation': 'Set AccessControl to Private or use bucket policies.'
    }
]

# Combine all rules
ALL_RULES = TERRAFORM_RULES + KUBERNETES_RULES + DOCKER_RULES + CLOUDFORMATION_RULES
