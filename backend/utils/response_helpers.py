"""
Response Helpers
================

Standardised JSON response builders for all API endpoints.

Using consistent response shapes makes it much easier to:
  - Test API responses.
  - Build frontend JavaScript that consumes the API.
  - Debug errors (every error has the same structure).

Standard Success Response Shape
--------------------------------
{
  "status": "success",
  "data": { ... },
  "message": "Optional human-readable message"
}

Standard Error Response Shape
------------------------------
{
  "status": "error",
  "message": "Human-readable error description",
  "errors": { "field": "error" }  # Optional field-level errors
}
"""

from flask import jsonify


def success_response(data: dict | list | None = None, message: str = "OK", status_code: int = 200):
    """
    Build a standardised success JSON response.

    Parameters
    ----------
    data : dict | list | None
        The payload to include in the response.
    message : str
        A human-readable success message.
    status_code : int
        HTTP status code (default 200).

    Returns
    -------
    Response
        A Flask JSON response object.
    """
    payload = {
        "status": "success",
        "message": message,
        "data": data or {},
    }
    return jsonify(payload), status_code


def error_response(
    message: str,
    errors: dict | None = None,
    status_code: int = 400,
):
    """
    Build a standardised error JSON response.

    Parameters
    ----------
    message : str
        A human-readable error description.
    errors : dict | None
        Optional dictionary of field-level validation errors.
    status_code : int
        HTTP status code (default 400).

    Returns
    -------
    Response
        A Flask JSON response object.
    """
    payload: dict = {
        "status": "error",
        "message": message,
    }
    if errors:
        payload["errors"] = errors
    return jsonify(payload), status_code


def created_response(data: dict | None = None, message: str = "Created"):
    """Convenience wrapper for 201 Created responses."""
    return success_response(data=data, message=message, status_code=201)


def not_found_response(message: str = "Resource not found"):
    """Convenience wrapper for 404 Not Found responses."""
    return error_response(message=message, status_code=404)


def unauthorized_response(message: str = "Authentication required"):
    """Convenience wrapper for 401 Unauthorized responses."""
    return error_response(message=message, status_code=401)


def server_error_response(message: str = "An internal server error occurred"):
    """Convenience wrapper for 500 Internal Server Error responses."""
    return error_response(message=message, status_code=500)
