"""
Basic functionality tests for CSH-256
"""

import pytest
import csh256


class TestBasicHashing:
    """Test basic hashing functionality"""
    
    def test_hash_returns_hex_string(self):
        """Hash should return 64-character hex string"""
        result = csh256.hash(b"test_password")
        assert isinstance(result, str)
        assert len(result) == 64
        assert all(c in '0123456789abcdef' for c in result)
    
    def test_hash_with_string_password(self):
        """Hash should accept string passwords"""
        result = csh256.hash("test_password")
        assert isinstance(result, str)
        assert len(result) == 64
    
    def test_hash_with_custom_salt(self):
        """Hash should accept custom salt"""
        salt = csh256.generate_salt()
        result = csh256.hash(b"password", salt=salt)
        assert isinstance(result, str)
        assert len(result) == 64
    
    def test_hash_with_custom_iterations(self):
        """Hash should accept custom iteration count"""
        result = csh256.hash(b"password", iterations=1024)
        assert isinstance(result, str)
        assert len(result) == 64
    
    def test_hash_deterministic_with_same_salt(self):
        """Same password and salt should produce same hash"""
        salt = csh256.generate_salt()
        hash1 = csh256.hash(b"password", salt=salt, iterations=100)
        hash2 = csh256.hash(b"password", salt=salt, iterations=100)
        assert hash1 == hash2
    
    def test_hash_different_with_different_salt(self):
        """Different salts should produce different hashes"""
        salt1 = csh256.generate_salt()
        salt2 = csh256.generate_salt()
        hash1 = csh256.hash(b"password", salt=salt1, iterations=100)
        hash2 = csh256.hash(b"password", salt=salt2, iterations=100)
        assert hash1 != hash2
    
    def test_invalid_salt_size(self):
        """Should raise error for invalid salt size"""
        with pytest.raises(ValueError, match="Salt must be exactly 16 bytes"):
            csh256.hash(b"password", salt=b"short")
    
    def test_invalid_iterations(self):
        """Should raise error for iterations below minimum"""
        with pytest.raises(ValueError, match="Iterations must be at least 64"):
            csh256.hash(b"password", iterations=10)


class TestHashFull:
    """Test hash_full functionality"""
    
    def test_hash_full_returns_dict(self):
        """hash_full should return dictionary with all components"""
        result = csh256.hash_full("password", iterations=100)
        assert isinstance(result, dict)
        assert 'hash' in result
        assert 'salt' in result
        assert 'iterations' in result
        assert 'formatted' in result
    
    def test_hash_full_components_valid(self):
        """All components should have valid values"""
        result = csh256.hash_full("password", iterations=100)
        assert len(result['hash']) == 64
        assert len(result['salt']) == 16
        assert result['iterations'] == 100
        assert result['formatted'].startswith('$csh256$')
    
    def test_hash_full_auto_salt(self):
        """hash_full should auto-generate salt if not provided"""
        result1 = csh256.hash_full("password", iterations=100)
        result2 = csh256.hash_full("password", iterations=100)
        assert result1['salt'] != result2['salt']
        assert result1['hash'] != result2['hash']


class TestVerify:
    """Test password verification"""
    
    def test_verify_correct_password(self):
        """Verify should return True for correct password"""
        result = csh256.hash_full("correct_password", iterations=100)
        is_valid = csh256.verify(
            "correct_password",
            hash_value=result['hash'],
            salt=result['salt'],
            iterations=result['iterations']
        )
        assert is_valid is True
    
    def test_verify_incorrect_password(self):
        """Verify should return False for incorrect password"""
        result = csh256.hash_full("correct_password", iterations=100)
        is_valid = csh256.verify(
            "wrong_password",
            hash_value=result['hash'],
            salt=result['salt'],
            iterations=result['iterations']
        )
        assert is_valid is False
    
    def test_verify_with_formatted_string(self):
        """Verify should work with PHC-formatted string"""
        result = csh256.hash_full("test_password", iterations=100)
        is_valid = csh256.verify("test_password", formatted=result['formatted'])
        assert is_valid is True
    
    def test_verify_formatted_wrong_password(self):
        """Verify with formatted string should reject wrong password"""
        result = csh256.hash_full("correct", iterations=100)
        is_valid = csh256.verify("wrong", formatted=result['formatted'])
        assert is_valid is False


class TestUtilities:
    """Test utility functions"""
    
    def test_generate_salt_size(self):
        """generate_salt should return 16 bytes by default"""
        salt = csh256.generate_salt()
        assert len(salt) == 16
    
    def test_generate_salt_custom_size(self):
        """generate_salt should accept custom size"""
        salt = csh256.generate_salt(32)
        assert len(salt) == 32
    
    def test_generate_salt_randomness(self):
        """generate_salt should produce different values"""
        salt1 = csh256.generate_salt()
        salt2 = csh256.generate_salt()
        assert salt1 != salt2
    
    def test_format_hash(self):
        """format_hash should create valid PHC string"""
        hash_val = "a" * 64
        salt = b"1234567890123456"
        formatted = csh256.format_hash(hash_val, salt, 4096)
        assert formatted.startswith('$csh256$')
        assert 'i=4096' in formatted
    
    def test_parse_hash(self):
        """parse_hash should extract components correctly"""
        original = csh256.hash_full("password", iterations=100)
        parsed = csh256.parse_hash(original['formatted'])
        assert parsed['hash'] == original['hash']
        assert parsed['salt'] == original['salt']
        assert parsed['iterations'] == original['iterations']
    
    def test_get_backend(self):
        """get_backend should return valid backend name"""
        backend = csh256.get_backend()
        assert backend in ['C', 'Python']


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_empty_password(self):
        """Should handle empty password"""
        result = csh256.hash(b"", iterations=100)
        assert len(result) == 64
    
    def test_long_password(self):
        """Should handle very long password"""
        long_password = b"x" * 10000
        result = csh256.hash(long_password, iterations=100)
        assert len(result) == 64
    
    def test_unicode_password(self):
        """Should handle unicode characters"""
        result = csh256.hash("مرحبا🔐", iterations=100)
        assert len(result) == 64
    
    def test_minimum_iterations(self):
        """Should work with minimum iterations"""
        result = csh256.hash(b"password", iterations=64)
        assert len(result) == 64
    
    def test_binary_data(self):
        """Should handle arbitrary binary data"""
        binary_data = bytes(range(256))
        result = csh256.hash(binary_data, iterations=100)
        assert len(result) == 64


if __name__ == '__main__':
    pytest.main([__file__, '-v'])