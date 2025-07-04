from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import json

def verify_metadata_signature(public_key_pem, metadata, signature_b64):
    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        data = json.dumps(metadata, separators=(',', ':')).encode()
        signature = base64.b64decode(signature_b64)
        public_key.verify(
            signature,
            data,
            padding.PKCS1v15(),
            hashes.SHA512()
        )
        return True
    except Exception as e:
        print(f"Signature verification failed: {e}")
        return False
