from datetime import timedelta
import json
import hmac
import base64
import asyncio
import functools

from fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from contextlib import contextmanager
from redis import Redis
from pydantic import BaseModel

from helper.config import AUTH_EXCEPTION, config, TOKEN_EXCEPTION


redis_conn = Redis(host="localhost", port=6379, db=0, decode_responses=True)

class Settings(BaseModel):
    authjwt_secret_key:str=config['SECRET_KEY']
    authjwt_denylist_enabled:bool=True
    authjwt_denylist_token_checks:set={"access", "refresh"}
    access_expires:int=timedelta(minutes=15)
    refresh_expires:int=timedelta(days=30)


settings=Settings()
@AuthJWT.load_config
def get_config():
    return settings


@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti']
    entry = redis_conn.get(jti)
    return entry and entry == "true"


def create_signed_token(key, data):
    header = json.dumps({"typ": "JWT", "alg": "HS256"}).encode('utf-8')
    henc = base64.urlsafe_b64encode(header).decode().strip('=')

    payload = json.dumps(data).encode('utf-8')
    penc = base64.urlsafe_b64encode(payload).decode().strip('=')

    hdata = henc + '.' + penc
    d = hmac.new(key, hdata.encode('utf-8'), 'sha256')
    dig = d.digest()
    denc = base64.urlsafe_b64encode(dig).decode().strip('=')

    token = hdata + '.' + denc
    return token


def verify_signed_token(key, token):
    (header, payload, signature) = token.split('.')
    hdata = header + '.' + payload

    d = hmac.new(key, hdata.encode('utf-8'), 'sha256')
    dig = d.digest()
    denc = base64.urlsafe_b64encode(dig).decode().strip('=')

    verified = hmac.compare_digest(denc, signature)
    print(payload)
    payload += '=' * (-len(payload) % 4)
    print(payload)
    payload_data = json.loads(base64.urlsafe_b64decode(payload).decode())
    return (verified, payload_data)


def decorating_sync_async(context, func):
    if asyncio.iscoroutinefunction(func):
        async def decorated(Authorize: AuthJWT=Depends()):
            with context(Authorize):
                return await func(Authorize)
    else:
        def decorated(Authorize: AuthJWT=Depends()):
            with context(Authorize):
                return func(Authorize)
    return functools.wraps(func)(decorated)


@contextmanager
def wrapper(Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise AUTH_EXCEPTION
    yield


def validate_token(func, Authorize: AuthJWT=Depends):
    context = lambda Authorize: wrapper(Authorize)
    return decorating_sync_async(context, func)