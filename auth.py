# auth.py

from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import Optional
import os


API_KEY_NAME = os.getenv('API_KEY_NAME')
API_KEY =  os.getenv('API_KEY')

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_current_token(api_key: Optional[str] = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=403,
            detail="Not authenticated",
        )