"""Test environment setup.

Settings are imported at module import time across the app, so required env
vars must exist before any application module is imported.
"""

import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://campus:campus@localhost/test")
os.environ.setdefault("JWT_SECRET", "test-secret-not-for-production-but-long-enough")
