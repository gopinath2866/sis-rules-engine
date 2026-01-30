#!/usr/bin/env python3
"""
Sign an exception file with a private key.
"""

import json
import sys
import os

# Add the sis-core/src directory to the path so we can import sis.signing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sis-core', 'src'))

from sis.signing import sign_exception

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <exception.json> <private_key.pem> [output.json]")
        sys.exit(1)

    exception_path = sys.argv[1]
    private_key_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else exception_path

    with open(exception_path, 'r') as f:
        exception_data = json.load(f)

    with open(private_key_path, 'r') as f:
        private_key_pem = f.read()

    signed_exception = sign_exception(exception_data, private_key_pem)

    with open(output_path, 'w') as f:
        json.dump(signed_exception, f, indent=2)

    print(f"Signed exception written to {output_path}")

if __name__ == '__main__':
    main()
