"""
Settings specific to this application only (no Django or 3rd party settings)
"""

IN_DOCKER = True
ALLOWED_HOSTS = [
    "https://when2meet-backend-686579494898.asia-southeast1.run.app",
    "loclahost",
    "127.0.0.1",
]

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True  # For development - restrict in production
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8081",
    "http://localhost:8080",
    "http://localhost:19006",
    "exp://localhost:19000",
    "https://when2meet-test-686579494898.asia-southeast1.run.app",
]

CORS_ALLOWED_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CSRF_TRUSTED_ORIGINS = [
    "https://when2meet-test-686579494898.asia-southeast1.run.app"
]