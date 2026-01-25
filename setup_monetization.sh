#!/bin/bash
echo "🚀 Setting up monetization for SIS Rules Engine v1.0.0"

# 1. Update README with sponsorship section
echo "Updating README.md..."
cat >> README.md << 'EOR'

## 💰 Support & Monetization

### ✨ **Free Community Edition**
- Basic validation rules
- Community support via GitHub Issues
- MIT Licensed - Free forever

### 🚀 **Professional Services**
We offer custom development, training, and consulting:
- **Custom Rule Development**: $2,000 - $10,000 per rule set
- **Integration Services**: $5,000 - $25,000
- **Training & Workshops**: $3,000 per day
- **Compliance Audits**: Starting at $5,000

👉 [View Services & Pricing](SERVICES.md)

### ☕ **Support Development**
If SIS Rules Engine helps secure your infrastructure, consider supporting its development:

[![GitHub Sponsors](https://img.shields.io/github/sponsors/gopinath2866?style=for-the-badge)](https://github.com/sponsors/gopinath2866)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/gopinath)

### 🔐 **Free Security Audit**
We're offering **10 free security audits** for early adopters:
👉 [Read more & apply here](FREE_AUDIT.md)
EOR

# 2. Create SERVICES.md if it doesn't exist
if [ ! -f "SERVICES.md" ]; then
    echo "Creating SERVICES.md..."
    cat > SERVICES.md << 'EOS'
# Professional Services & Pricing

## 🎯 Our Services

### 1. Custom Rule Development
**Price: $2,000 - $10,000 per rule set**
- GDPR compliance rules
- HIPAA security rules  
- PCI-DSS validation rules
- Custom organizational policies

### 2. Integration Services
**Price: $5,000 - $25,000**
- Jira/ServiceNow integration
- Custom CI/CD pipeline setup
- Enterprise deployment
- Single Sign-On (SSO) integration

### 3. Training & Workshops
**Price: $3,000 per day**
- Team training sessions
- Custom workshops
- Security best practices
- Compliance training

### 4. Security Audits
**Price: Starting at $5,000**
- Comprehensive IaC security review
- Compliance gap analysis
- Risk assessment report
- Remediation guidance

## 📞 Get Started
1. **Email**: gopinath@example.com
2. **Schedule**: https://calendly.com/gopinath/consultation
3. **GitHub**: Open an issue with "SERVICE REQUEST" tag

## 🎁 Early Adopter Offer
**First 10 customers get 50% off** any service package!

---
*All prices in USD. Custom quotes available.*
EOS
fi

# 3. Add monetization info to CLI
echo "Adding monetization info to CLI..."
python3 -c "
import sys
import os

# Read the cli.py file
with open('src/sis/cli.py', 'r') as f:
    content = f.read()

# Add monetization function if not exists
if '_print_monetization_info' not in content:
    # Find where to add it (before main() function)
    lines = content.split('\n')
    new_lines = []
    added = False
    
    for i, line in enumerate(lines):
        if not added and line.strip().startswith('def main():'):
            # Add the function before main
            indent = ' ' * (len(line) - len(line.lstrip()))
            new_lines.append('')
            new_lines.append(indent + 'def _print_monetization_info():')
            new_lines.append(indent + '    \"\"\"Print monetization information\"\"\"')
            new_lines.append(indent + '    print(\"\\n\" + \"=\"*60)')
            new_lines.append(indent + '    print(\"🚀 ENTERPRISE FEATURES & SERVICES AVAILABLE\")')
            new_lines.append(indent + '    print(\"=\"*60)')
            new_lines.append(indent + '    print(\"\\n✨ Premium Features:\")')
            new_lines.append(indent + '    print(\"  • GDPR/HIPAA/PCI-DSS Compliance Rules\")')
            new_lines.append(indent + '    print(\"  • Custom Rule Development\")')
            new_lines.append(indent + '    print(\"  • Priority Support & Training\")')
            new_lines.append(indent + '    print(\"  • Enterprise Deployment\")')
            new_lines.append(indent + '    print(\"\\n💰 Pricing:\")')
            new_lines.append(indent + '    print(\"  • Custom Rules: \$2,000 - \$10,000 per set\")')
            new_lines.append(indent + '    print(\"  • Consulting: \$200 - \$500 per hour\")')
            new_lines.append(indent + '    print(\"  • Training: \$3,000 per day\")')
            new_lines.append(indent + '    print(\"\\n🎁 Special Offer:\")')
            new_lines.append(indent + '    print(\"  • First 10 customers: 50% OFF\")')
            new_lines.append(indent + '    print(\"  • Free security audit available\")')
            new_lines.append(indent + '    print(\"\\n📞 Contact:\")')
            new_lines.append(indent + '    print(\"  • Email: gopinath@example.com\")')
            new_lines.append(indent + '    print(\"  • Services: https://github.com/gopinath2866/sis-rules-engine/blob/main/SERVICES.md\")')
            new_lines.append(indent + '    print(\"  • Free Audit: https://github.com/gopinath2866/sis-rules-engine/blob/main/FREE_AUDIT.md\")')
            new_lines.append(indent + '    print(\"\\n☕ Support Development:\")')
            new_lines.append(indent + '    print(\"  • GitHub Sponsors: https://github.com/sponsors/gopinath2866\")')
            new_lines.append(indent + '    print(\"  • Buy Me a Coffee: https://buymeacoffee.com/gopinath\")')
            new_lines.append(indent + '    print(\"=\"*60)')
            new_lines.append('')
            added = True
        new_lines.append(line)
    
    # Now add call to _print_monetization_info in main()
    final_lines = []
    in_main = False
    main_indent = 0
    added_call = False
    
    for line in new_lines:
        final_lines.append(line)
        
        if line.strip().startswith('def main():'):
            in_main = True
            main_indent = len(line) - len(line.lstrip())
        
        if in_main and line.strip().startswith('return') and len(line) - len(line.lstrip()) == main_indent + 4 and not added_call:
            # Add monetization info before return
            indent = ' ' * (main_indent + 8)
            final_lines.append('')
            final_lines.append(indent + '# Display monetization information for free tier')
            final_lines.append(indent + 'if args.subcommand != \"validate\" and args.subcommand != \"scan\":')
            final_lines.append(indent + '    _print_monetization_info()')
            added_call = True
    
    content = '\n'.join(final_lines)

# Write back the file
with open('src/sis/cli.py', 'w') as f:
    f.write(content)

print('✅ Updated cli.py with monetization call-to-action')
"

# 4. Create simple MONETIZATION.md
echo "Creating MONETIZATION.md..."
cat > MONETIZATION.md << 'EOM'
# Monetization Strategy

## Quick Start Revenue Streams:

1. **GitHub Sponsors** - Micro-donations from users
2. **Professional Services** - $2k-$50k projects
3. **Free Audits → Paid Services** - Lead generation funnel
4. **Premium Features** - Future SaaS model

## Immediate Actions:
1. Set up GitHub Sponsors: https://github.com/sponsors
2. Create Buy Me a Coffee: https://buymeacoffee.com
3. Promote free audits on LinkedIn/Twitter
4. Reach out to 10 potential clients this week

## Revenue Timeline:
- Week 1: First consulting inquiries ($200-500)
- Month 1: First custom rule project ($2,000-5,000)
- Month 3: Multiple projects ($10,000+ total)
- Month 6: Start SaaS recurring revenue

Start earning today!
EOM

# 5. Commit changes
echo ""
echo "Committing monetization setup..."
git add .
git commit -m "feat: add monetization system

- Add sponsorship badges to README
- Create professional services page
- Add monetization call-to-action to CLI
- Create monetization strategy document
- Ready for revenue generation"

echo ""
echo "✅ Monetization setup complete!"
echo ""
echo "💰 Revenue streams now active:"
echo "1. GitHub Sponsors & Buy Me a Coffee"
echo "2. Professional Services ($2k-$50k projects)"
echo "3. Free Audit → Paid Services Funnel"
echo ""
echo "🚀 Next steps:"
echo "1. Set up GitHub Sponsors: https://github.com/sponsors"
echo "2. Create Buy Me a Coffee: https://buymeacoffee.com"
echo "3. Update email in SERVICES.md to your actual email"
echo "4. Start promoting free audits!"
