"""
Signing and verification for governance exceptions.
Requires cryptography library.
"""

import json
import base64
import hashlib

try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

def compute_exception_hash(exception_data: dict) -> bytes:
    """Compute SHA256 hash of the exception without the signature block."""
    exception_without_sig = exception_data.copy()
    exception_without_sig.pop('signature', None)
    canonical_json = json.dumps(exception_without_sig, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical_json.encode()).digest()

def verify_exception(exception_data: dict, public_key_pem: str) -> bool:
    """Verify the signature of an exception."""
    if not CRYPTOGRAPHY_AVAILABLE:
        raise RuntimeError("cryptography library not available")

    public_key = load_pem_public_key(public_key_pem.encode())
    signature_b64 = exception_data['signature']['signature_hash']
    signature_bytes = base64.b64decode(signature_b64)

    # Compute the hash of the exception (without signature)
    hash_bytes = compute_exception_hash(exception_data)

    try:
        public_key.verify(
            signature_bytes,
            hash_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

def sign_exception(exception_data: dict, private_key_pem: str) -> dict:
    """Sign an exception and return the signed exception."""
    if not CRYPTOGRAPHY_AVAILABLE:
        raise RuntimeError("cryptography library not available")

    private_key = load_pem_private_key(private_key_pem.encode(), password=None)
    hash_bytes = compute_exception_hash(exception_data)

    signature_bytes = private_key.sign(
        hash_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    signature_b64 = base64.b64encode(signature_bytes).decode()

    # Add the signature to the exception
    exception_data['signature'] = {
        "type": "detached",
        "required": True,
        "signer_identity": "RSA2048",
        "signature_hash": signature_b64
    }

    return exception_data
