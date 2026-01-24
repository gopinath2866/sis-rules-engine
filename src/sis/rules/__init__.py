"""
SIS Rules - Updated for better matching
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
            'resource_kinds': ['aws_iam_policy']
        },
        'detection': {
            'match_logic': 'ANY',
            'conditions': [
                {
                    'path': 'policy',
                    'operator': 'CONTAINS',
                    'value': '"Action":"*"'
                },
                {
                    'path': 'policy',
                    'operator': 'REGEX',
                    'value': 'action.*\*'
                }
            ]
        },
        'severity': 'CRITICAL',
        'message': 'IAM policy allows all actions (*)',
        'remediation': 'Follow principle of least privilege. Use specific actions.'
    },
    
    # IRR-DEC-02: Irreversible resource (prevent_destroy)
    {
        'rule_id': 'IRR-DEC-02',
        'rule_type': 'irreversible_decision',
        'applies_to': {
            'resource_kinds': ['aws_s3_bucket', 'aws_db_instance', 'aws_vpc']
        },
        'detection': {
            'match_logic': 'ANY',
            'conditions': [
                {
                    'path': 'lifecycle.prevent_destroy',
                    'operator': 'EQUALS',
                    'value': True
                },
                {
                    'path': 'lifecycle.prevent_destroy',
                    'operator': 'EQUALS',
                    'value': 'true'
                }
            ]
        },
        'severity': 'HIGH',
        'message': 'Resource cannot be destroyed (prevent_destroy = true)',
        'remediation': 'Use with caution. Ensure backup and migration plans exist.'
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
                {
                    'path': 'acl',
                    'operator': 'EQUALS',
                    'value': 'public-read'
                },
                {
                    'path': 'acl',
                    'operator': 'EQUALS', 
                    'value': 'public-read-write'
                },
                {
                    'path': 'acl',
                    'operator': 'CONTAINS',
                    'value': 'public'
                }
            ]
        },
        'severity': 'HIGH',
        'message': 'S3 bucket has public access',
        'remediation': 'Set ACL to "private" or use bucket policies.'
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
                {
                    'path': 'ingress.cidr_blocks',
                    'operator': 'CONTAINS',
                    'value': '0.0.0.0/0'
                },
                {
                    'path': 'config',
                    'operator': 'CONTAINS',
                    'value': '0.0.0.0/0'
                },
                {
                    'path': 'config',
                    'operator': 'REGEX',
                    'value': '0\\.0\\.0\\.0/0'
                }
            ]
        },
        'severity': 'HIGH',
        'message': 'Security group allows all traffic from internet',
        'remediation': 'Restrict CIDR blocks to specific IP ranges.'
    },
    
    # TF-003: Plaintext secrets
    {
        'rule_id': 'TF-003',
        'rule_type': 'secrets',
        'applies_to': {
            'resource_kinds': ['*']  # Applies to all
        },
        'detection': {
            'match_logic': 'ANY',
            'conditions': [
                {
                    'path': 'config',
                    'operator': 'REGEX',
                    'value': '(?i)(password|secret|token|key)\\s*[=:]\\s*["\']?[\\w-]+["\']?'
                },
                {
                    'path': 'default',
                    'operator': 'REGEX', 
                    'value': '(?i)(password|secret|token|key)'
                },
                {
                    'path': 'config',
                    'operator': 'CONTAINS',
                    'value': 'password'
                }
            ]
        },
        'severity': 'CRITICAL',
        'message': 'Plaintext secret detected',
        'remediation': 'Use secrets manager (AWS Secrets Manager, HashiCorp Vault).'
    },
    
    # TF-004: Missing encryption
    {
        'rule_id': 'TF-004',
        'rule_type': 'encryption',
        'applies_to': {
            'resource_kinds': ['aws_s3_bucket', 'aws_ebs_volume', 'aws_rds_cluster']
        },
        'detection': {
            'match_logic': 'ALL',
            'conditions': [
                {
                    'path': 'server_side_encryption_configuration',
                    'operator': 'NOT_EXISTS',
                    'value': ''
                }
            ]
        },
        'severity': 'MEDIUM',
        'message': 'Resource missing encryption configuration',
        'remediation': 'Enable encryption for data at rest.'
    },
    
    # TF-005: Wide open egress rules
    {
        'rule_id': 'TF-005',
        'rule_type': 'network',
        'applies_to': {
            'resource_kinds': ['aws_security_group']
        },
        'detection': {
            'match_logic': 'ANY',
            'conditions': [
                {
                    'path': 'egress.cidr_blocks',
                    'operator': 'CONTAINS',
                    'value': '0.0.0.0/0'
                }
            ]
        },
        'severity': 'MEDIUM',
        'message': 'Security group allows all outbound traffic',
        'remediation': 'Restrict egress to specific destinations.'
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
                {
                    'path': 'spec.containers.securityContext.privileged',
                    'operator': 'EQUALS',
                    'value': True
                }
            ]
        },
        'severity': 'HIGH',
        'message': 'Container runs with privileged security context',
        'remediation': 'Remove privileged: true or use specific capabilities.'
    }
]

# ==================== DOCKER COMPOSE RULES ====================
DOCKER_RULES = []

# ==================== CLOUDFORMATION RULES ====================
CLOUDFORMATION_RULES = []

# Combine all rules
ALL_RULES = TERRAFORM_RULES + KUBERNETES_RULES + DOCKER_RULES + CLOUDFORMATION_RULES
