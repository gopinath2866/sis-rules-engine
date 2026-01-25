#!/usr/bin/env python3
"""Generate license keys for premium features"""

import hashlib
import uuid
import json
from datetime import datetime, timedelta

def generate_license(tier="pro", customer_name="", email="", duration_days=365):
    """Generate a license key"""
    
    license_id = str(uuid.uuid4())[:8].upper()
    issue_date = datetime.now().strftime("%Y-%m-%d")
    expiry_date = (datetime.now() + timedelta(days=duration_days)).strftime("%Y-%m-%d")
    
    license_data = {
        "license_id": license_id,
        "tier": tier,
        "customer_name": customer_name,
        "email": email,
        "issue_date": issue_date,
        "expiry_date": expiry_date,
        "duration_days": duration_days
    }
    
    data_string = json.dumps(license_data, sort_keys=True)
    hash_object = hashlib.sha256(data_string.encode())
    license_hash = hash_object.hexdigest()[:16].upper()
    
    if tier == "pro":
        license_key = f"SIS-PRO-{license_id}-{license_hash}"
    elif tier == "enterprise":
        license_key = f"SIS-ENT-{license_id}-{license_hash}"
    else:
        license_key = f"SIS-FREE-{license_id}-{license_hash}"
    
    license_content = {
        "license_key": license_key,
        "license_data": license_data
    }
    
    return license_content

def save_license(license_content, filename=None):
    """Save license to file"""
    if filename is None:
        tier = license_content["license_data"]["tier"]
        customer = license_content["license_data"]["customer_name"].replace(" ", "_").lower()
        filename = f"sis_license_{tier}_{customer}.json"
    
    with open(filename, 'w') as f:
        json.dump(license_content, f, indent=2)
    
    print(f"✅ License saved to {filename}")
    print(f"📋 License Key: {license_content['license_key']}")
    
    key_filename = "sis_license.key"
    with open(key_filename, 'w') as f:
        f.write(license_content['license_key'])
    print(f"🔑 CLI license file: {key_filename}")
    
    return filename

if __name__ == "__main__":
    print("🎫 SIS Rules Engine License Generator")
    print("="*40)
    
    tier = input("License Tier (pro/enterprise): ").strip().lower()
    customer_name = input("Customer Name: ").strip()
    email = input("Customer Email: ").strip()
    duration = int(input("Duration (days) [365]: ").strip() or "365")
    
    license_content = generate_license(tier, customer_name, email, duration)
    
    print(f"\n✅ Generated {tier.upper()} License:")
    print(f"   Customer: {customer_name}")
    print(f"   Email: {email}")
    print(f"   Valid until: {license_content['license_data']['expiry_date']}")
    
    save = input("\nSave license? (y/n): ").strip().lower()
    if save == 'y':
        filename = input(f"Filename [sis_license_{tier}_{customer_name.replace(' ', '_').lower()}.json]: ").strip()
        if not filename:
            filename = None
        save_license(license_content, filename)
