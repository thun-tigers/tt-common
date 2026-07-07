import pytest
from flask import Flask


@pytest.fixture()
def app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="test-secret",
        SSO_SHARED_SECRET="test-sso-secret",
        SSO_EXPECTED_AUDIENCE="tt-members",
        AUTH_BASE_URL="http://localhost:8085",
    )
    return app
