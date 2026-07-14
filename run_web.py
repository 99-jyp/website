#!/usr/bin/env python
"""
Hospital AI Platform - Django Web Entry Point
Usage:
    python run_web.py runserver
    python run_web.py migrate
    python run_web.py createsuperuser
"""
import os
import sys
from pathlib import Path

# Always run from AI_AGENT root so relative paths in tools/db resolve correctly.
ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.config.settings")

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
