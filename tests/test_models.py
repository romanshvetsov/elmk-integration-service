import pytest
from pydantic import ValidationError

from app.models import MedicalBookRequest


class TestMedicalBookRequest:
    """Test cases for MedicalBookRequest model validation."""
    
    def test_valid_elmk_and_snils(self):
        """Test valid ELMK and SNILS numbers."""
        request = MedicalBookRequest(
            elmk_number="123456789012",
            snils="12345678901"
        )
        assert request.elmk_number == "123456789012"
        assert request.snils == "12345678901"
    
    def test_invalid_elmk_too_short(self):
        """Test ELMK number that is too short."""
        with pytest.raises(ValidationError) as exc_info:
            MedicalBookRequest(
                elmk_number="12345678901",  # 11 digits
                snils="12345678901"
            )
        assert "ELMK number must be exactly 12 digits" in str(exc_info.value)
    
    def test_invalid_elmk_too_long(self):
        """Test ELMK number that is too long."""
        with pytest.raises(ValidationError) as exc_info:
            MedicalBookRequest(
                elmk_number="1234567890123",  # 13 digits
                snils="12345678901"
            )
        assert "ELMK number must be exactly 12 digits" in str(exc_info.value)
    
    def test_invalid_elmk_with_letters(self):
        """Test ELMK number with non-digit characters."""
        with pytest.raises(ValidationError) as exc_info:
            MedicalBookRequest(
                elmk_number="12345678901a",
                snils="12345678901"
            )
        assert "ELMK number must be exactly 12 digits" in str(exc_info.value)
    
    def test_invalid_snils_too_short(self):
        """Test SNILS number that is too short."""
        with pytest.raises(ValidationError) as exc_info:
            MedicalBookRequest(
                elmk_number="123456789012",
                snils="1234567890"  # 10 digits
            )
        assert "SNILS must be exactly 11 digits" in str(exc_info.value)
    
    def test_invalid_snils_too_long(self):
        """Test SNILS number that is too long."""
        with pytest.raises(ValidationError) as exc_info:
            MedicalBookRequest(
                elmk_number="123456789012",
                snils="123456789012"  # 12 digits
            )
        assert "SNILS must be exactly 11 digits" in str(exc_info.value)
    
    def test_invalid_snils_with_letters(self):
        """Test SNILS number with non-digit characters."""
        with pytest.raises(ValidationError) as exc_info:
            MedicalBookRequest(
                elmk_number="123456789012",
                snils="1234567890a"
            )
        assert "SNILS must be exactly 11 digits" in str(exc_info.value)
    
    def test_edge_cases(self):
        """Test edge cases with all zeros and all nines."""
        # All zeros
        request1 = MedicalBookRequest(
            elmk_number="000000000000",
            snils="00000000000"
        )
        assert request1.elmk_number == "000000000000"
        assert request1.snils == "00000000000"
        
        # All nines
        request2 = MedicalBookRequest(
            elmk_number="999999999999",
            snils="99999999999"
        )
        assert request2.elmk_number == "999999999999"
        assert request2.snils == "99999999999"