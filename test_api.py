#!/usr/bin/env python3
import requests
import json
import base64

# Базовый URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Тест health check endpoint."""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/healthz")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_medical_book_validation():
    """Тест валидации медицинской книжки."""
    print("\nTesting medical book validation...")
    
    # Basic Auth credentials
    username = "admin"
    password = "securepassword123"
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    
    # Тестовые данные
    test_data = {
        "elmk_number": "860102797025",
        "snils": "17648922116"
    }
    
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/medical-book/validate",
            json=test_data,
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_invalid_data():
    """Тест с невалидными данными."""
    print("\nTesting invalid data...")
    
    username = "admin"
    password = "securepassword123"
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    
    # Невалидные данные
    invalid_data = {
        "elmk_number": "12345678901",  # 11 цифр вместо 12
        "snils": "17648922116"
    }
    
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/medical-book/validate",
            json=invalid_data,
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_no_auth():
    """Тест без аутентификации."""
    print("\nTesting without authentication...")
    
    test_data = {
        "elmk_number": "860102797025",
        "snils": "17648922116"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/medical-book/validate",
            json=test_data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_health_check()
    test_medical_book_validation()
    test_invalid_data()
    test_no_auth()