"""
Development settings for local work.
"""

from .settings_base import *  # noqa: F401,F403

DEBUG = env_bool("DJANGO_DEBUG", True)  # noqa: F405
