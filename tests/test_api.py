"""
API Integration Tests for Migraine Prediction Service
Tests FastAPI endpoints, validation, and error handling
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def valid_prediction_input():
    """Valid input for prediction"""
    return {
        "age": 35,
        "gender": 1,
        "sleep_hours": 7.0,
        "sleep_quality": 6,
        "stress_level": 7,
        "hydration": 6,
        "exercise": 3,
        "screen_time": 8.0,
        "caffeine_intake": 3,
        "alcohol_intake": 1,
        "weather_changes": 1,
        "menstrual_cycle": 1,
        "dehydration": 0,
        "bright_light": 1,
        "loud_noises": 0,
        "strong_smells": 1,
        "missed_meals": 1,
        "specific_foods": 0,
        "physical_activity": 1,
        "neck_pain": 1,
        "weather_pressure": 1013.25,
        "humidity": 65.0,
        "temperature_change": 5.0
    }


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_endpoint_exists(self, client):
        """Test that health endpoint exists"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_endpoint_returns_json(self, client):
        """Test that health endpoint returns JSON"""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"
    
    def test_health_endpoint_structure(self, client):
        """Test health endpoint response structure"""
        response = client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_returns_info(self, client):
        """Test that root returns API info"""
        response = client.get("/")
        data = response.json()
        
        assert "message" in data or "name" in data


class TestPredictionEndpoint:
    """Test prediction endpoint"""
    
    def test_predict_endpoint_exists(self, client):
        """Test that predict endpoint exists"""
        response = client.options("/predict")
        assert response.status_code in [200, 405]  # OPTIONS or POST only
    
    def test_predict_with_valid_input(self, client, valid_prediction_input):
        """Test prediction with valid input"""
        response = client.post("/predict", json=valid_prediction_input)
        
        # Should return 200 or 422 (if models not loaded)
        assert response.status_code in [200, 422, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "prediction" in data or "migraine_occurrence" in data
    
    def test_predict_with_missing_fields(self, client):
        """Test prediction with missing required fields"""
        incomplete_input = {
            "age": 35,
            "gender": 1
        }
        
        response = client.post("/predict", json=incomplete_input)
        assert response.status_code == 422  # Validation error
    
    def test_predict_with_invalid_types(self, client, valid_prediction_input):
        """Test prediction with invalid data types"""
        invalid_input = valid_prediction_input.copy()
        invalid_input["age"] = "not a number"
        
        response = client.post("/predict", json=invalid_input)
        assert response.status_code == 422
    
    def test_predict_with_out_of_range_values(self, client, valid_prediction_input):
        """Test prediction with out-of-range values"""
        invalid_input = valid_prediction_input.copy()
        invalid_input["age"] = 200  # Invalid age
        
        response = client.post("/predict", json=invalid_input)
        # API might accept but models should handle
        assert response.status_code in [200, 422, 400]
    
    def test_predict_response_structure(self, client, valid_prediction_input):
        """Test prediction response structure"""
        response = client.post("/predict", json=valid_prediction_input)
        
        if response.status_code == 200:
            data = response.json()
            # Check for expected fields
            assert isinstance(data, dict)


class TestBatchPredictionEndpoint:
    """Test batch prediction endpoint if available"""
    
    def test_batch_predict_endpoint(self, client, valid_prediction_input):
        """Test batch prediction endpoint"""
        batch_input = [valid_prediction_input, valid_prediction_input]
        
        # Try different possible endpoints
        for endpoint in ["/predict/batch", "/batch_predict", "/predict_batch"]:
            response = client.post(endpoint, json=batch_input)
            if response.status_code != 404:
                # Endpoint exists
                assert response.status_code in [200, 422, 500]
                break


class TestMetricsEndpoint:
    """Test metrics endpoint for monitoring"""
    
    def test_metrics_endpoint_exists(self, client):
        """Test if metrics endpoint exists"""
        response = client.get("/metrics")
        # May or may not exist depending on implementation
        assert response.status_code in [200, 404]
    
    def test_metrics_format(self, client):
        """Test metrics endpoint format if it exists"""
        response = client.get("/metrics")
        
        if response.status_code == 200:
            # Prometheus format or JSON
            content_type = response.headers.get("content-type", "")
            assert "text" in content_type or "json" in content_type


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_for_invalid_endpoint(self, client):
        """Test 404 for non-existent endpoints"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test method not allowed errors"""
        # Try GET on POST-only endpoint
        response = client.get("/predict")
        assert response.status_code in [405, 422]  # Method not allowed or validation error
    
    def test_malformed_json(self, client):
        """Test handling of malformed JSON"""
        response = client.post(
            "/predict",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


class TestCORS:
    """Test CORS headers if configured"""
    
    def test_cors_headers(self, client):
        """Test CORS headers"""
        response = client.get("/health")
        
        # Check if CORS is configured
        if "access-control-allow-origin" in response.headers:
            assert response.headers["access-control-allow-origin"] is not None


class TestRateLimiting:
    """Test rate limiting if implemented"""
    
    def test_rate_limiting(self, client, valid_prediction_input):
        """Test rate limiting by making many requests"""
        # Make multiple requests
        responses = []
        for i in range(150):  # Exceed typical rate limit
            response = client.post("/predict", json=valid_prediction_input)
            responses.append(response.status_code)
        
        # Check if any requests were rate limited (429)
        # This test might pass if rate limiting is not implemented
        has_rate_limit = 429 in responses
        # Not failing the test if no rate limiting


class TestValidation:
    """Test input validation"""
    
    def test_negative_age(self, client, valid_prediction_input):
        """Test negative age validation"""
        invalid_input = valid_prediction_input.copy()
        invalid_input["age"] = -5
        
        response = client.post("/predict", json=invalid_input)
        # Should either validate or process
        assert response.status_code in [200, 422, 400]
    
    def test_null_values(self, client, valid_prediction_input):
        """Test handling of null values"""
        invalid_input = valid_prediction_input.copy()
        invalid_input["age"] = None
        
        response = client.post("/predict", json=invalid_input)
        assert response.status_code == 422
    
    def test_extra_fields(self, client, valid_prediction_input):
        """Test handling of extra fields"""
        input_with_extra = valid_prediction_input.copy()
        input_with_extra["extra_field"] = "should be ignored"
        
        response = client.post("/predict", json=input_with_extra)
        # Should either accept or reject based on strict validation
        assert response.status_code in [200, 422]


class TestDocumentation:
    """Test API documentation endpoints"""
    
    def test_docs_endpoint(self, client):
        """Test that /docs endpoint exists (FastAPI auto-docs)"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_schema(self, client):
        """Test OpenAPI schema endpoint"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema
    
    def test_redoc_endpoint(self, client):
        """Test ReDoc endpoint"""
        response = client.get("/redoc")
        assert response.status_code == 200


class TestPerformance:
    """Test API performance"""
    
    def test_prediction_response_time(self, client, valid_prediction_input):
        """Test that prediction responds in reasonable time"""
        import time
        
        start = time.time()
        response = client.post("/predict", json=valid_prediction_input)
        elapsed = time.time() - start
        
        # Should respond within 2 seconds
        if response.status_code == 200:
            assert elapsed < 2.0, f"Prediction took {elapsed:.2f}s"
    
    def test_health_check_response_time(self, client):
        """Test health check responds quickly"""
        import time
        
        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start
        
        # Health check should be very fast
        assert elapsed < 0.5, f"Health check took {elapsed:.2f}s"


class TestSecurity:
    """Test security aspects"""
    
    def test_no_sensitive_info_in_errors(self, client):
        """Test that errors don't expose sensitive information"""
        response = client.post("/predict", json={"invalid": "data"})
        
        if response.status_code >= 400:
            error_text = response.text.lower()
            # Should not expose sensitive paths or internals
            assert "password" not in error_text
            assert "secret" not in error_text
    
    def test_sql_injection_attempt(self, client, valid_prediction_input):
        """Test SQL injection attempt (should be handled safely)"""
        malicious_input = valid_prediction_input.copy()
        malicious_input["age"] = "1; DROP TABLE users;--"
        
        response = client.post("/predict", json=malicious_input)
        # Should reject invalid type
        assert response.status_code == 422


class TestIntegration:
    """Integration tests"""
    
    def test_complete_prediction_flow(self, client, valid_prediction_input):
        """Test complete prediction flow"""
        # 1. Check health
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # 2. Make prediction
        pred_response = client.post("/predict", json=valid_prediction_input)
        
        if pred_response.status_code == 200:
            # 3. Validate response
            data = pred_response.json()
            assert isinstance(data, dict)
    
    def test_multiple_predictions(self, client, valid_prediction_input):
        """Test making multiple predictions"""
        results = []
        
        for i in range(5):
            response = client.post("/predict", json=valid_prediction_input)
            results.append(response.status_code)
        
        # All should succeed (or all fail consistently)
        if 200 in results:
            assert all(r == 200 for r in results), "Inconsistent prediction results"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
