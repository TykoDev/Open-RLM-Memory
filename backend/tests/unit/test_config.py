import os
from unittest import mock
from app.core.config import Settings

@mock.patch.dict(os.environ, {}, clear=True)
def test_config_no_default_passwords():
    # Make sure we don't pick up DATABASE_URL or POSTGRES_PASSWORD from the environment
    settings = Settings(_env_file=None)
    assert settings.DATABASE_URL is None
    assert settings.POSTGRES_PASSWORD is None
