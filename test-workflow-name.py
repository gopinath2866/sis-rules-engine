import yaml
import os

with open('.github/workflows/proxy-upgrade-gate.yml', 'r') as f:
    workflow = yaml.safe_load(f)
    
print("Workflow name in file:", workflow.get('name', 'NOT FOUND'))
print("Workflow filename:", 'proxy-upgrade-gate.yml')
print("")
print("What GitHub might call it:")
print("1.", workflow.get('name', 'proxy-upgrade-gate'))
print("2. 'sis-proxy-upgrade-gate' (from CLI)")
print("3. 'Proxy Upgrade Gate' (capitalized)")
