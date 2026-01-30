#!/usr/bin/env python3
"""
Generate an RSA key pair for signing exceptions.
"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import sys

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

public_key = private_key.public_key()
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

private_key_path = 'private_key.pem'
public_key_path = 'public_key.pem'

with open(private_key_path, 'wb') as f:
    f.write(private_pem)

with open(public_key_path, 'wb') as f:
    f.write(public_pem)

print(f"Generated {private_key_path} and {public_key_path}")
