#!/bin/bash
echo "🚀 COMPLETE SIS TEST SUITE"
echo "=========================="

echo "\n1. Testing CLI Commands:"
echo "-----------------------"
./sis_wrapper version
./sis_wrapper --help

echo "\n2. Testing Rules Listing:"
echo "------------------------"
./sis_wrapper rules --type terraform
echo "\nAvailable rules by type:"
./sis_wrapper rules --type kubernetes

echo "\n3. Testing File Scans:"
echo "---------------------"
echo "\nScanning test_real.tf:"
./sis_wrapper scan test_real.tf --severity CRITICAL,HIGH

echo "\nScanning test_real.tf (JSON output):"
./sis_wrapper scan test_real.tf --format json --output /tmp/sis_test.json
echo "JSON output saved to /tmp/sis_test.json"
head -20 /tmp/sis_test.json

echo "\n4. Testing Directory Scan:"
echo "--------------------------"
./sis_wrapper scan . --severity CRITICAL,HIGH --quiet

echo "\n5. Creating Sample Reports:"
echo "--------------------------"
mkdir -p reports
./sis_wrapper scan . --format json --output reports/full_scan.json
./sis_wrapper scan . --format text --output reports/full_scan.txt
echo "Reports created in reports/ directory"
ls -la reports/

echo "\n✅ Test suite complete!"
