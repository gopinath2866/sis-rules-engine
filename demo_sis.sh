#!/bin/bash
echo "🚀 SIS SECURITY SCANNER DEMO"
echo "=============================="
echo ""

echo "1. Show version:"
echo "----------------"
./sis_wrapper version
echo ""

echo "2. List available rules:"
echo "------------------------"
./sis_wrapper rules --type terraform | head -20
echo ""

echo "3. Scan a Terraform file (text output):"
echo "---------------------------------------"
./sis_wrapper scan test_clean.tf --format text
echo ""

echo "4. Scan a Terraform file (JSON output):"
echo "---------------------------------------"
./sis_wrapper scan test_clean.tf --format json --output /tmp/demo.json
echo "JSON report saved to /tmp/demo.json"
echo ""

echo "5. Scan a directory:"
echo "--------------------"
./sis_wrapper scan . --severity HIGH --quiet
echo ""

echo "6. Create HTML report:"
echo "----------------------"
./sis_wrapper scan test_clean.tf --format html --output /tmp/demo.html
echo "HTML report saved to /tmp/demo.html"
echo ""

echo "7. Summary of all findings:"
echo "---------------------------"
find . -name "*.tf" -exec ./sis_wrapper scan {} --quiet \; 2>/dev/null | grep -E "(Found|✅|❌)" | sort | uniq -c | sort -rn
echo ""

echo "✅ DEMO COMPLETE!"
echo ""
echo "📁 Reports created:"
echo "  - /tmp/demo.json  (JSON format)"
echo "  - /tmp/demo.html  (HTML format)"
echo ""
echo "🔧 Try these commands:"
echo "  ./sis_wrapper scan your-terraform.tf"
echo "  ./sis_wrapper scan ./your-infra/ --format json"
echo "  ./sis_wrapper scan ./your-infra/ --severity CRITICAL,HIGH"
