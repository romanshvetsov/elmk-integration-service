import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import httpx

from app.main import app
from app.models import ExternalAPIResponse

client = TestClient(app)


class TestHealthCheck:
    """Test cases for health check endpoint."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"


class TestMedicalBookValidation:
    """Test cases for medical book validation endpoint."""
    
    def test_validate_medical_book_success(self):
        """Test successful medical book validation."""
        mock_response_data = {
            "elmk_status_name": "Действует",
            "elmk_number": "86-01-027970-25",
            "first_name": "Хуснигул",
            "last_name": "О***",
            "middle_name": "Абдусатторовна",
            "snils": "176***16",
            "work_type": [
                "Работы, при выполнении которых осуществляется контакт с пищевыми продуктами в процессе их производства, хранения, транспортировки и реализации"
            ],
            "decision_dt": "2025-07-11T07:52:57Z",
            "med_opinions_dt": "2026-07-02",
            "certification_dt": "2025-07-11",
            "recertification_dt": "2026-07-11",
            "fbuz_short_name": "ФБУЗ «ЦГиЭ в ХМАО-Югре»",
            "created_fullname": "ЕПГУ"
        }
        
        with patch('app.external_api.external_api_client.get_medical_book_info') as mock_get:
            mock_get.return_value = ExternalAPIResponse(**mock_response_data)
            
            response = client.post(
                "/api/v1/medical-book/validate",
                json={
                    "elmk_number": "860102797025",
                    "snils": "17648922116"
                },
                headers={"Authorization": "Basic YWRtaW46c2VjdXJlcGFzc3dvcmQxMjM="}  # admin:securepassword123
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["elmk_status_name"] == "Действует"
            assert data["elmk_number"] == "86-01-027970-25"
            assert data["first_name"] == "Хуснигул"
            assert data["last_name"] == "О***"
            assert data["middle_name"] == "Абдусатторовна"
            assert data["snils"] == "176***16"
            assert len(data["work_type"]) == 1
            assert "пищевыми продуктами" in data["work_type"][0]
    
    def test_validate_medical_book_invalid_elmk(self):
        """Test validation with invalid ELMK number."""
        response = client.post(
            "/api/v1/medical-book/validate",
            json={
                "elmk_number": "12345678901",  # 11 digits
                "snils": "17648922116"
            },
            headers={"Authorization": "Basic YWRtaW46c2VjdXJlcGFzc3dvcmQxMjM="}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "value error" in data["detail"][0]["msg"].lower()
        assert "elmk number must be exactly 12 digits" in data["detail"][0]["msg"].lower()
    
    def test_validate_medical_book_invalid_snils(self):
        """Test validation with invalid SNILS number."""
        response = client.post(
            "/api/v1/medical-book/validate",
            json={
                "elmk_number": "123456789012",
                "snils": "1764892211"  # 10 digits
            },
            headers={"Authorization": "Basic YWRtaW46c2VjdXJlcGFzc3dvcmQxMjM="}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "value error" in data["detail"][0]["msg"].lower()
        assert "snils must be exactly 11 digits" in data["detail"][0]["msg"].lower()
    
    def test_validate_medical_book_no_auth(self):
        """Test validation without authentication."""
        response = client.post(
            "/api/v1/medical-book/validate",
            json={
                "elmk_number": "123456789012",
                "snils": "17648922116"
            }
        )
        
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers
    
    def test_validate_medical_book_wrong_auth(self):
        """Test validation with wrong authentication."""
        response = client.post(
            "/api/v1/medical-book/validate",
            json={
                "elmk_number": "123456789012",
                "snils": "17648922116"
            },
            headers={"Authorization": "Basic d3Jvbmc6d3Jvbmc="}  # wrong:wrong
        )
        
        assert response.status_code == 401
    
    def test_validate_medical_book_external_api_error(self):
        """Test validation when external API returns error."""
        with patch('app.external_api.external_api_client.get_medical_book_info') as mock_get:
            mock_get.side_effect = httpx.HTTPStatusError(
                "404 Not Found",
                request=httpx.Request("GET", "http://example.com"),
                response=httpx.Response(404, request=httpx.Request("GET", "http://example.com"))
            )
            
            response = client.post(
                "/api/v1/medical-book/validate",
                json={
                    "elmk_number": "123456789012",
                    "snils": "17648922116"
                },
                headers={"Authorization": "Basic YWRtaW46c2VjdXJlcGFzc3dvcmQxMjM="}
            )
            
            assert response.status_code == 404
    
    def test_validate_medical_book_timeout(self):
        """Test validation when external API times out."""
        with patch('app.external_api.external_api_client.get_medical_book_info') as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Request timed out")
            
            response = client.post(
                "/api/v1/medical-book/validate",
                json={
                    "elmk_number": "123456789012",
                    "snils": "17648922116"
                },
                headers={"Authorization": "Basic YWRtaW46c2VjdXJlcGFzc3dvcmQxMjM="}
            )
            
            assert response.status_code == 504


class TestMetrics:
    """Test cases for metrics endpoint."""
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "metrics endpoint"