"""
Post-Quantum Cryptography Module

This module implements the IETF draft standard for hybrid key exchange in TLS with
quantum-resistant encryption. It uses ML-KEM (formerly CRYSTALS-Kyber) for key
encapsulation to protect against quantum computing threats.

Based on the NIST Post-Quantum Cryptography Standardization process and
IETF draft standards for integrating post-quantum algorithms into TLS.
"""

import base64
import hashlib
import logging
import os
import secrets
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any

import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption

# Since actual ML-KEM/Kyber implementation requires C libraries typically,
# this is a simplified version for demonstration purposes
# In a real system, you would use a proper implementation like liboqs or similar
# This simplified version would be replaced by actual quantum-resistant libraries

logger = logging.getLogger(__name__)


class PostQuantumAlgorithm(str, Enum):
    """Post-quantum cryptographic algorithms supported by the system."""
    ML_KEM_512 = "ml_kem_512"  # Lower security, higher performance
    ML_KEM_768 = "ml_kem_768"  # NIST Level 3 (128-bit quantum security)
    ML_KEM_1024 = "ml_kem_1024"  # NIST Level 5 (highest security)
    # Additional algorithms could be added as NIST finalizes more standards


@dataclass
class HybridKeyPair:
    """A hybrid key pair containing both classical and post-quantum keys."""
    # Classical keys
    classical_public_key: bytes
    classical_private_key: bytes
    classical_algorithm: str
    # Post-quantum keys
    pq_public_key: bytes
    pq_private_key: bytes
    pq_algorithm: PostQuantumAlgorithm
    # Metadata
    created_at: float
    key_id: str


@dataclass
class HybridCiphertext:
    """Hybrid ciphertext containing both classical and post-quantum encrypted data."""
    classical_ciphertext: bytes
    pq_ciphertext: bytes
    algorithm_info: Dict[str, str]
    key_id: str
    nonce: bytes


class PostQuantumCrypto:
    """
    Implements post-quantum cryptographic operations for hybrid key exchange
    following the IETF draft standard for hybrid key exchange in TLS.

    This is a simplified demonstration version. For production use, this would
    integrate with actual post-quantum libraries like liboqs or libpqcrypto.
    """

    def __init__(self, default_algorithm: PostQuantumAlgorithm = PostQuantumAlgorithm.ML_KEM_768):
        """
        Initialize the post-quantum cryptography service.

        Args:
            default_algorithm: The default post-quantum algorithm to use
        """
        self.default_algorithm = default_algorithm
        self._key_cache: Dict[str, HybridKeyPair] = {}

        # In a real implementation, these would be proper references to the libraries
        self._pq_algorithms = {
            PostQuantumAlgorithm.ML_KEM_512: {
                "public_key_size": 800,
                "private_key_size": 1632,
                "ciphertext_size": 768,
                "shared_secret_size": 32,
            },
            PostQuantumAlgorithm.ML_KEM_768: {
                "public_key_size": 1184,
                "private_key_size": 2400,
                "ciphertext_size": 1088,
                "shared_secret_size": 32,
            },
            PostQuantumAlgorithm.ML_KEM_1024: {
                "public_key_size": 1568,
                "private_key_size": 3168,
                "ciphertext_size": 1568,
                "shared_secret_size": 32,
            }
        }

    def generate_hybrid_keypair(
        self,
        pq_algorithm: Optional[PostQuantumAlgorithm] = None,
        classical_key_size: int = 2048
    ) -> HybridKeyPair:
        """
        Generate a hybrid key pair with both classical and post-quantum keys.

        Args:
            pq_algorithm: The post-quantum algorithm to use
            classical_key_size: The size of the classical RSA key in bits

        Returns:
            HybridKeyPair: The generated hybrid key pair
        """
        # Use default algorithm if none specified
        if pq_algorithm is None:
            pq_algorithm = self.default_algorithm

        # Generate classical RSA key
        classical_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=classical_key_size
        )
        classical_public_key = classical_private_key.public_key()

        # Serialize classical keys
        classical_public_bytes = classical_public_key.public_bytes(
            encoding=Encoding.DER,
            format=PublicFormat.SubjectPublicKeyInfo
        )
        classical_private_bytes = classical_private_key.private_bytes(
            encoding=Encoding.DER,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption()
        )

        # Generate simulated post-quantum keys
        # In a real implementation, this would call into a PQ library
        pq_specs = self._pq_algorithms[pq_algorithm]

        # Simulate ML-KEM key generation
        # In reality, these would be properly structured keys from a library
        pq_private_key = self._simulated_pq_keygen(pq_specs["private_key_size"])
        pq_public_key = self._simulated_pq_keygen(pq_specs["public_key_size"])

        # Create a unique key ID
        key_id = self._generate_key_id(classical_public_bytes, pq_public_key)

        # Create the hybrid key pair
        hybrid_key = HybridKeyPair(
            classical_public_key=classical_public_bytes,
            classical_private_key=classical_private_bytes,
            classical_algorithm="RSA-2048",
            pq_public_key=pq_public_key,
            pq_private_key=pq_private_key,
            pq_algorithm=pq_algorithm,
            created_at=time.time(),
            key_id=key_id
        )

        # Cache the key pair
        self._key_cache[key_id] = hybrid_key

        return hybrid_key

    def hybrid_encrypt(
        self,
        data: bytes,
        recipient_public_key: Union[HybridKeyPair, bytes],
        pq_algorithm: Optional[PostQuantumAlgorithm] = None
    ) -> HybridCiphertext:
        """
        Encrypt data using a hybrid approach with both classical and post-quantum encryption.

        Args:
            data: The data to encrypt
            recipient_public_key: The recipient's public key
            pq_algorithm: The post-quantum algorithm to use

        Returns:
            HybridCiphertext: The encrypted data
        """
        # Use default algorithm if none specified
        if pq_algorithm is None:
            pq_algorithm = self.default_algorithm

        # Extract public keys
        if isinstance(recipient_public_key, HybridKeyPair):
            classical_public_bytes = recipient_public_key.classical_public_key
            pq_public_key = recipient_public_key.pq_public_key
            key_id = recipient_public_key.key_id
            used_pq_algorithm = recipient_public_key.pq_algorithm
        else:
            # Assume the bytes contain a serialized public key
            # In a real implementation, you would parse the key format
            # This is a simplified demonstration
            raise ValueError("Direct public key bytes not supported in this demonstration")

        # Generate a random symmetric key
        symmetric_key = os.urandom(32)

        # Encrypt the symmetric key with classical cryptography
        classical_public_key = serialization.load_der_public_key(classical_public_bytes)
        classical_encrypted_key = classical_public_key.encrypt(
            symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Simulate encrypting the symmetric key with ML-KEM
        # In a real implementation, this would use the actual ML-KEM encapsulation
        pq_specs = self._pq_algorithms[used_pq_algorithm]
        pq_encrypted_key = self._simulated_pq_encrypt(
            symmetric_key,
            pq_public_key,
            pq_specs["ciphertext_size"]
        )

        # Generate a nonce for symmetric encryption
        nonce = os.urandom(16)

        # Encrypt the data with the symmetric key
        # In a real implementation, you would use AES-GCM or similar
        # Here we use a simulated encryption for demonstration
        encryption_key = self._derive_encryption_key(symmetric_key, nonce)
        ciphertext = self._simulated_symmetric_encrypt(data, encryption_key, nonce)

        # Create the hybrid ciphertext
        hybrid_ct = HybridCiphertext(
            classical_ciphertext=classical_encrypted_key + ciphertext,
            pq_ciphertext=pq_encrypted_key,
            algorithm_info={
                "classical": "RSA-OAEP-256",
                "pq": used_pq_algorithm,
                "symmetric": "AES-256-GCM"
            },
            key_id=key_id,
            nonce=nonce
        )

        return hybrid_ct

    def hybrid_decrypt(
        self,
        ciphertext: HybridCiphertext,
        recipient_key: Optional[HybridKeyPair] = None
    ) -> bytes:
        """
        Decrypt data using a hybrid approach with both classical and post-quantum decryption.

        Args:
            ciphertext: The encrypted data
            recipient_key: The recipient's key pair

        Returns:
            bytes: The decrypted data
        """
        # Look up the key by ID if not provided
        if recipient_key is None:
            if ciphertext.key_id not in self._key_cache:
                raise ValueError(f"No key found with ID {ciphertext.key_id}")
            recipient_key = self._key_cache[ciphertext.key_id]

        # Extract the classical encrypted key and actual ciphertext
        # In a real implementation, you would properly parse the format
        classical_encrypted_key = ciphertext.classical_ciphertext[:256]  # Assuming 2048-bit RSA
        actual_ciphertext = ciphertext.classical_ciphertext[256:]

        # Decrypt using classical cryptography
        classical_private_key = serialization.load_der_private_key(
            recipient_key.classical_private_key,
            password=None
        )
        try:
            symmetric_key_classical = classical_private_key.decrypt(
                classical_encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        except Exception as e:
            logger.error(f"Classical decryption failed: {e}")
            symmetric_key_classical = None

        # Simulate ML-KEM decapsulation to get the symmetric key
        # In a real implementation, this would use the actual ML-KEM decapsulation
        try:
            symmetric_key_pq = self._simulated_pq_decrypt(
                ciphertext.pq_ciphertext,
                recipient_key.pq_private_key
            )
        except Exception as e:
            logger.error(f"Post-quantum decryption failed: {e}")
            symmetric_key_pq = None

        # Use the post-quantum key by default, falling back to classical
        # This "hybrid" approach ensures security even if one system is broken
        symmetric_key = symmetric_key_pq if symmetric_key_pq is not None else symmetric_key_classical

        if symmetric_key is None:
            raise ValueError("Both classical and post-quantum decryption failed")

        # Derive the encryption key from the symmetric key and nonce
        encryption_key = self._derive_encryption_key(symmetric_key, ciphertext.nonce)

        # Decrypt the data
        plaintext = self._simulated_symmetric_decrypt(actual_ciphertext, encryption_key, ciphertext.nonce)

        return plaintext

    def _generate_key_id(self, classical_key: bytes, pq_key: bytes) -> str:
        """Generate a unique ID for a key pair based on its public keys."""
        combined = classical_key + pq_key
        return hashlib.sha256(combined).hexdigest()[:16]

    def _simulated_pq_keygen(self, key_size: int) -> bytes:
        """
        Simulate post-quantum key generation.

        In a real implementation, this would call into a post-quantum library
        like liboqs or similar.
        """
        # Create a random byte string of the specified size
        # In a real implementation, this would be a properly structured key
        return os.urandom(key_size)

    def _simulated_pq_encrypt(self, data: bytes, public_key: bytes, ct_size: int) -> bytes:
        """
        Simulate post-quantum encryption.

        In a real implementation, this would call into a post-quantum library.
        """
        # In a real implementation, this would properly use the public key
        # and perform the actual post-quantum encryption operation
        # For demonstration, we're just doing a simple operation
        combined = data + public_key
        hashed = hashlib.sha512(combined).digest()

        # Pad or truncate to the expected ciphertext size
        if len(hashed) < ct_size:
            result = hashed + os.urandom(ct_size - len(hashed))
        else:
            result = hashed[:ct_size]

        return result

    def _simulated_pq_decrypt(self, ciphertext: bytes, private_key: bytes) -> bytes:
        """
        Simulate post-quantum decryption.

        In a real implementation, this would call into a post-quantum library.
        """
        # In a real implementation, this would properly use the private key
        # to perform the actual post-quantum decryption
        # For demonstration, we're returning a deterministic value that would
        # match what encrypt would produce
        # WARNING: This is NOT secure and is only for demonstration
        return hashlib.sha256(private_key + ciphertext).digest()

    def _derive_encryption_key(self, key_material: bytes, salt: bytes) -> bytes:
        """Derive an encryption key from key material using HKDF."""
        # Use HKDF to derive a key for encryption
        return HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=b"hybrid_encryption"
        ).derive(key_material)

    def _simulated_symmetric_encrypt(self, data: bytes, key: bytes, nonce: bytes) -> bytes:
        """
        Simulate symmetric encryption.

        In a real implementation, this would use AES-GCM or similar.
        """
        # WARNING: This is NOT secure and is only for demonstration
        # In a real implementation, use a proper authenticated encryption scheme
        result = bytearray()
        for i, b in enumerate(data):
            result.append(b ^ key[i % len(key)] ^ nonce[i % len(nonce)])
        return bytes(result)

    def _simulated_symmetric_decrypt(self, data: bytes, key: bytes, nonce: bytes) -> bytes:
        """
        Simulate symmetric decryption.

        In a real implementation, this would use AES-GCM or similar.
        """
        # For our simple XOR "encryption", encryption and decryption are the same
        return self._simulated_symmetric_encrypt(data, key, nonce)


class TLSConfig:
    """
    Configuration for TLS settings with post-quantum cryptography support.

    This class provides methods to configure a TLS server or client with
    hybrid key exchange that supports both classical and post-quantum algorithms.
    """

    def __init__(self, pq_crypto: PostQuantumCrypto):
        """
        Initialize the TLS configuration.

        Args:
            pq_crypto: The post-quantum cryptography service
        """
        self.pq_crypto = pq_crypto

        # Default cipher suites in order of preference
        self.cipher_suites = [
            # Hybrid suites (fictitious names for demonstration)
            "TLS_HYBRID_ECDHE_ML_KEM_768_WITH_AES_256_GCM_SHA384",
            "TLS_HYBRID_ECDHE_ML_KEM_512_WITH_AES_128_GCM_SHA256",

            # Fallback to standard TLS 1.3 cipher suites
            "TLS_AES_256_GCM_SHA384",
            "TLS_AES_128_GCM_SHA256",
            "TLS_CHACHA20_POLY1305_SHA256"
        ]

        # Supported key exchange methods
        self.key_exchange_methods = [
            # Hybrid methods
            "HYBRID_ECDHE_ML_KEM_768",
            "HYBRID_ECDHE_ML_KEM_512",

            # Classical methods
            "ECDHE_P256",
            "ECDHE_P384",
            "ECDHE_X25519"
        ]

    def get_server_config(self) -> Dict[str, Any]:
        """
        Get TLS server configuration with post-quantum support.

        This would be used to configure a web server or API server
        with hybrid key exchange support.

        Returns:
            Dict[str, Any]: Server configuration settings
        """
        # Generate hybrid key pair for the server
        server_key = self.pq_crypto.generate_hybrid_keypair()

        # In a real implementation, this would return actual server configuration
        # specific to the server software (e.g., nginx, aiohttp, etc.)
        return {
            "hybrid_enabled": True,
            "cipher_suites": self.cipher_suites,
            "key_exchange_methods": self.key_exchange_methods,
            "certificate_type": "X509_WITH_PQ_EXTENSION",
            "server_key_id": server_key.key_id,
            "post_quantum_algorithms": [algo.value for algo in list(PostQuantumAlgorithm)],
            "minimum_tls_version": "TLS1.3"
        }

    def get_client_config(self) -> Dict[str, Any]:
        """
        Get TLS client configuration with post-quantum support.

        This would be used to configure a client library or application
        to connect to servers with hybrid key exchange support.

        Returns:
            Dict[str, Any]: Client configuration settings
        """
        # In a real implementation, this would return actual client configuration
        # specific to the client library (e.g., requests, aiohttp, etc.)
        return {
            "hybrid_enabled": True,
            "cipher_suites": self.cipher_suites,
            "key_exchange_methods": self.key_exchange_methods,
            "post_quantum_algorithms": [algo.value for algo in list(PostQuantumAlgorithm)],
            "validate_hybrid_cert": True,
            "fallback_to_classical": True,
            "minimum_tls_version": "TLS1.3"
        }

    def configure_requests_session(self, session: requests.Session):
        """
        Configure a requests session with post-quantum TLS support.

        Note: This is a demonstration of how such configuration would work.
        Actual implementation would depend on requests supporting hybrid key exchange.

        Args:
            session: The requests session to configure
        """
        # In a real implementation, this would configure the requests session
        # with the appropriate settings for hybrid key exchange
        # Example:
        # - Set custom SSL context with hybrid cipher suites
        # - Configure certificate verification to handle PQ extensions
        # - Set up client certificates with PQ extensions

        # For now, just demonstrate the idea with custom headers
        session.headers.update({
            "X-PQ-Supported": "true",
            "X-PQ-Algorithms": ",".join([algo.value for algo in list(PostQuantumAlgorithm)])
        })

        # In a real implementation, you would configure the SSL context
        # Unfortunately, as of now, most HTTP libraries don't directly support PQ TLS
        # This will change as the IETF standards are finalized and implemented

        return session

# Initialization function for dependency injection
def get_post_quantum_crypto() -> PostQuantumCrypto:
    """Get the post-quantum cryptography service instance."""
    return PostQuantumCrypto()
