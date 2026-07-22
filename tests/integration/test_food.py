"""
Integration Tests — Food Routes
================================

Tests the food blueprint HTTP endpoints.
More complete tests are added in Phase 7 once the services are implemented.
"""


class TestFoodRoutes:
    """Integration tests for /food/* endpoints."""

    def test_upload_redirects_unauthenticated(self, client):
        """GET /food/upload should redirect unauthenticated users to login."""
        response = client.get("/food/upload")
        assert response.status_code == 302

    def test_history_redirects_unauthenticated(self, client):
        """GET /food/history should redirect unauthenticated users to login."""
        response = client.get("/food/history")
        assert response.status_code == 302

    def test_prediction_redirects_unauthenticated(self, client):
        """GET /food/prediction should redirect unauthenticated users to login."""
        response = client.get("/food/prediction")
        assert response.status_code == 302
