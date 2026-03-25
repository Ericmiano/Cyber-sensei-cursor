"""Tests for authentication endpoints."""
import pytest
from fastapi import status


def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "user" in data
    assert "access_token" in data


def test_register_weak_password(client):
    """Test registration with weak password."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "username": "user",
            "password": "weak",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login(client, test_user):
    """Test user login."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "test@example.com",
            "password": "TestPass123!",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "test@example.com",
            "password": "WrongPassword123!",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
