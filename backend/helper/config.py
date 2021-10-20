import os
from fastapi import status, HTTPException
from dotenv import dotenv_values

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = dotenv_values(os.path.join(BASE_DIR, ".env"))

AUTH_EXCEPTION = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials, please try again", headers={"WWW-Authenticate": "Bearer"})
TOKEN_EXCEPTION = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is invalid or expired, please request a new one", headers={"WWW-Authenticate": "Bearer"})