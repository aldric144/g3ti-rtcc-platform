"""
Unit tests for Secure Packaging module.
"""



class TestAES256Encryptor:
    """Tests for AES256Encryptor class."""

    def test_generate_key(self):
        """Test key generation."""
        from app.federal.secure_packaging import AES256Encryptor

        encryptor = AES256Encryptor()
        key = encryptor.generate_key()

        assert key is not None
        assert key.algorithm.value == "AES-256-GCM"
        assert len(key.key_bytes) == 32  # 256 bits

    def test_generate_iv(self):
        """Test IV generation."""
        from app.federal.secure_packaging import AES256Encryptor

        encryptor = AES256Encryptor()
        iv = encryptor.generate_iv()

        assert iv is not None
        assert len(iv) == 12  # 96 bits for GCM

    def test_encrypt_decrypt(self):
        """Test encryption and decryption."""
        from app.federal.secure_packaging import AES256Encryptor

        encryptor = AES256Encryptor()
        key = encryptor.generate_key()
        iv = encryptor.generate_iv()

        plaintext = b"Test data for encryption"

        encrypted, auth_tag = encryptor.encrypt(plaintext, key, iv)

        assert encrypted is not None
        assert encrypted != plaintext

        decrypted = encryptor.decrypt(encrypted, key, iv, auth_tag)

        assert decrypted == plaintext


class TestRSAKeyWrapper:
    """Tests for RSAKeyWrapper class."""

    def test_wrap_unwrap_key(self):
        """Test key wrapping and unwrapping."""
        from app.federal.secure_packaging import AES256Encryptor, RSAKeyWrapper

        wrapper = RSAKeyWrapper()
        encryptor = AES256Encryptor()

        # Generate a symmetric key to wrap
        sym_key = encryptor.generate_key()

        # Wrap the key
        wrapped = wrapper.wrap_key(sym_key.key_bytes)

        assert wrapped is not None
        assert wrapped != sym_key.key_bytes

        # Unwrap the key
        unwrapped = wrapper.unwrap_key(wrapped)

        assert unwrapped == sym_key.key_bytes


class TestSignatureGenerator:
    """Tests for SignatureGenerator class."""

    def test_generate_signature(self):
        """Test signature generation."""
        from app.federal.secure_packaging import SignatureAlgorithm, SignatureGenerator

        generator = SignatureGenerator()

        data = b"Test data for signing"
        signature = generator.generate_signature(data, SignatureAlgorithm.SHA256)

        assert signature is not None
        assert len(signature) == 64  # SHA-256 hex = 64 chars

    def test_verify_signature(self):
        """Test signature verification."""
        from app.federal.secure_packaging import SignatureAlgorithm, SignatureGenerator

        generator = SignatureGenerator()

        data = b"Test data for signing"
        signature = generator.generate_signature(data, SignatureAlgorithm.SHA256)

        is_valid = generator.verify_signature(data, signature, SignatureAlgorithm.SHA256)

        assert is_valid is True

    def test_verify_signature_invalid(self):
        """Test signature verification with invalid signature."""
        from app.federal.secure_packaging import SignatureAlgorithm, SignatureGenerator

        generator = SignatureGenerator()

        data = b"Test data for signing"
        signature = generator.generate_signature(data, SignatureAlgorithm.SHA256)

        # Modify data
        modified_data = b"Modified data"

        is_valid = generator.verify_signature(modified_data, signature, SignatureAlgorithm.SHA256)

        assert is_valid is False


class TestNonceManager:
    """Tests for NonceManager class."""

    def test_generate_nonce(self):
        """Test nonce generation."""
        from app.federal.secure_packaging import NonceManager

        manager = NonceManager()
        nonce = manager.generate_nonce()

        assert nonce is not None
        assert nonce.value is not None
        assert nonce.used is False

    def test_use_nonce(self):
        """Test using a nonce."""
        from app.federal.secure_packaging import NonceManager

        manager = NonceManager()
        nonce = manager.generate_nonce()

        # First use should succeed
        success = manager.use_nonce(nonce)
        assert success is True

        # Second use should fail (replay protection)
        success = manager.use_nonce(nonce)
        assert success is False

    def test_is_nonce_used(self):
        """Test checking if nonce is used."""
        from app.federal.secure_packaging import NonceManager

        manager = NonceManager()
        nonce = manager.generate_nonce()

        assert manager.is_nonce_used(nonce) is False

        manager.use_nonce(nonce)

        assert manager.is_nonce_used(nonce) is True


class TestSecurePackageBuilder:
    """Tests for SecurePackageBuilder class."""

    def test_build_package(self):
        """Test building a secure package."""
        from app.federal.secure_packaging import SecurePackageBuilder

        builder = SecurePackageBuilder()

        payload = {"person_id": "123", "name": "John Smith"}

        package = builder.build(
            payload=payload,
            message_type="ndex_person",
            originating_agency="FL0000000",
            destination_system="ndex",
        )

        assert package is not None
        assert package.header is not None
        assert package.header.message_type == "ndex_person"
        assert package.encrypted_payload is not None
        assert package.signature is not None
        assert package.nonce is not None
        assert package.status.value == "ready"

    def test_verify_package(self):
        """Test verifying a secure package."""
        from app.federal.secure_packaging import SecurePackageBuilder

        builder = SecurePackageBuilder()

        payload = {"incident_id": "456", "type": "Criminal"}

        package = builder.build(
            payload=payload,
            message_type="ndex_incident",
            originating_agency="FL0000000",
            destination_system="ndex",
        )

        is_valid = builder.verify_package(package)

        assert is_valid is True


class TestSecurePackagingManager:
    """Tests for SecurePackagingManager class."""

    def test_create_secure_package(self):
        """Test creating a secure package."""
        from app.federal.secure_packaging import secure_packaging_manager

        payload = {"sar_id": "789", "behavior": "surveillance"}

        package = secure_packaging_manager.create_secure_package(
            payload=payload,
            message_type="dhs_sar",
            originating_agency="FL0000000",
            destination_system="dhs_sar",
        )

        assert package is not None
        assert package.id is not None
        assert package.status.value == "ready"

    def test_get_package(self):
        """Test getting a package by ID."""
        from app.federal.secure_packaging import secure_packaging_manager

        payload = {"trace_id": "101", "firearm_type": "pistol"}

        package = secure_packaging_manager.create_secure_package(
            payload=payload,
            message_type="etrace_request",
            originating_agency="FL0000000",
            destination_system="etrace",
        )

        retrieved = secure_packaging_manager.get_package(package.id)

        assert retrieved is not None
        assert retrieved.id == package.id

    def test_get_packages_by_agency(self):
        """Test getting packages by agency."""
        from app.federal.secure_packaging import secure_packaging_manager

        packages = secure_packaging_manager.get_packages_by_agency("FL0000000")

        assert isinstance(packages, list)

    def test_get_encryption_status(self):
        """Test getting encryption status."""
        from app.federal.secure_packaging import secure_packaging_manager

        status = secure_packaging_manager.get_encryption_status()

        assert status is not None
        assert "status" in status
        assert "encryption" in status
        assert status["encryption"]["algorithm"] == "AES-256-GCM"

    def test_register_recipient_key(self):
        """Test registering a recipient public key."""
        from app.federal.secure_packaging import secure_packaging_manager

        # This is a sample public key for testing
        sample_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0Z3VS5JJcds3xfn/ygWyf8sS
-----END PUBLIC KEY-----"""

        result = secure_packaging_manager.register_recipient_key(
            system_id="test_system",
            public_key_pem=sample_key,
        )

        assert result is True


class TestSecurePackage:
    """Tests for SecurePackage class."""

    def test_to_dict(self):
        """Test converting package to dictionary."""
        from app.federal.secure_packaging import SecurePackageBuilder

        builder = SecurePackageBuilder()

        payload = {"test": "data"}

        package = builder.build(
            payload=payload,
            message_type="test",
            originating_agency="FL0000000",
            destination_system="test",
        )

        package_dict = package.to_dict()

        assert isinstance(package_dict, dict)
        assert "header" in package_dict
        assert "payload_encrypted" in package_dict
        assert "signature" in package_dict

    def test_to_json(self):
        """Test converting package to JSON."""
        import json

        from app.federal.secure_packaging import SecurePackageBuilder

        builder = SecurePackageBuilder()

        payload = {"test": "data"}

        package = builder.build(
            payload=payload,
            message_type="test",
            originating_agency="FL0000000",
            destination_system="test",
        )

        package_json = package.to_json()

        assert isinstance(package_json, str)

        # Should be valid JSON
        parsed = json.loads(package_json)
        assert "header" in parsed


class TestEncryptionKey:
    """Tests for EncryptionKey class."""

    def test_to_base64(self):
        """Test converting key to base64."""
        from app.federal.secure_packaging import AES256Encryptor

        encryptor = AES256Encryptor()
        key = encryptor.generate_key()

        base64_key = key.to_base64()

        assert base64_key is not None
        assert isinstance(base64_key, str)

    def test_from_base64(self):
        """Test creating key from base64."""
        from app.federal.secure_packaging import AES256Encryptor, EncryptionKey

        encryptor = AES256Encryptor()
        key = encryptor.generate_key()

        base64_key = key.to_base64()

        restored_key = EncryptionKey.from_base64(base64_key, key.algorithm)

        assert restored_key.key_bytes == key.key_bytes


class TestNonce:
    """Tests for Nonce class."""

    def test_to_hex(self):
        """Test converting nonce to hex."""
        from app.federal.secure_packaging import NonceManager

        manager = NonceManager()
        nonce = manager.generate_nonce()

        hex_nonce = nonce.to_hex()

        assert hex_nonce is not None
        assert isinstance(hex_nonce, str)

    def test_to_base64(self):
        """Test converting nonce to base64."""
        from app.federal.secure_packaging import NonceManager

        manager = NonceManager()
        nonce = manager.generate_nonce()

        base64_nonce = nonce.to_base64()

        assert base64_nonce is not None
        assert isinstance(base64_nonce, str)
