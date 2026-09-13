"""
Compatibility settings entrypoint.

Use DJANGO_SETTINGS_ENV=production to load production settings, otherwise
development settings are used.
"""

import os

if os.getenv("DJANGO_SETTINGS_ENV") == "production":
    from .settings_production import *  # noqa: F401,F403
else:
    from .settings_development import *  # noqa: F401,F403
