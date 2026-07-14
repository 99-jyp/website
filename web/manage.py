#!/usr/bin/env python
"""
Django management script.
Run from AI_AGENT root:
    python run_web.py <command>

Or directly (ensure CWD is AI_AGENT):
    python web/manage.py <command>
"""
import os
import sys
from pathlib import Path


def main():
    # Ensure CWD is AI_AGENT root for relative path resolution.
    root = Path(__file__).resolve().parent.parent
    os.chdir(root)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.config.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
