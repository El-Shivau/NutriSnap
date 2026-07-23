"""
Integration Tests — Authentication Routes
==========================================

Tests the auth blueprint HTTP endpoints using the Flask test client.
Verifies that routes return correct status codes and redirect correctly.

Phase 5 will add deeper tests once the services are implemented.
"""


class TestAuthRoutes:
    """Integration tests for /auth/* endpoints."""

    def test_login_page_loads(self, client):
        """GET /auth/login should return 200 OK."""
        response = client.get("/auth/login")
        assert response.status_code == 200
        assert b"Login" in response.data

    def test_register_page_loads(self, client):
        """GET /auth/register should return 200 OK."""
        response = client.get("/auth/register")
        assert response.status_code == 200
        assert b"Register" in response.data or b"Create" in response.data

    def test_logout_redirects_unauthenticated(self, client):
        """GET /auth/logout without login should redirect to login page."""
        response = client.get("/auth/logout")
        # Flask-Login redirects unauthenticated users to the login view
        assert response.status_code == 302

    def test_landing_page_loads(self, client):
        """GET / should return 200 OK."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"NutriSnap" in response.data
