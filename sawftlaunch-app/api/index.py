"""Vercel serverless entrypoint.

Vercel's Python runtime looks for an ASGI `app` object in this file. We add the
project root to sys.path and import the FastAPI app from main.py.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app  # noqa: E402  (exposed for Vercel's ASGI detection)
