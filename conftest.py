"""
Pytest configuration for Evennia tests.

This file sets up Django properly for pytest to work with Evennia.
"""

import os
import django
from django.conf import settings


def pytest_configure():
    """Configure Django settings for pytest."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
    django.setup()


def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    # Ensure Django is set up
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
        django.setup() 