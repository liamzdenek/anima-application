"""
AWS Lambda handler for the FastAPI application.
This module adapts the FastAPI application to run in AWS Lambda.
"""

import os
import json
import base64
from typing import Dict, Any, Optional

from mangum import Mangum

# Import the FastAPI app directly
# Use the Lambda-specific app that uses absolute imports
from app_lambda import app

# Create a Mangum adapter for the FastAPI application
handler = Mangum(app)