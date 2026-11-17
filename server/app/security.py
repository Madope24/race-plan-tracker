import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, UTC

import jwt
from fastapi import Depends, HTTPException, Header

JWT_SECRET = os.environ.get('JWT_SECRET', '')
TOKEN_DAYS = int(os.environ.get('TOKEN_DAYS', '60'))
ITERATIONS = 240_000


def _secret() -> str:
    if len(JWT_SECRET) < 32:
        raise RuntimeError('JWT_SECRET must be set to at least 32 characters')
    return JWT_SECRET


def hash_password(pw: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt, ITERATIONS)
    return f'pbkdf2${ITERATIONS}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}'


def verify_password(pw: str, stored: str) -> bool:
    try:
        _, it, salt, dk = stored.split('$')
        test = hashlib.pbkdf2_hmac('sha256', pw.encode(), base64.b64decode(salt), int(it))
        return hmac.compare_digest(test, base64.b64decode(dk))
    except (ValueError, TypeError):
        return False


def make_token(user_id: str) -> str:
    exp = datetime.now(UTC) + timedelta(days=TOKEN_DAYS)
    return jwt.encode({'sub': user_id, 'exp': exp}, _secret(), algorithm='HS256')


def current_user_id(authorization: str = Header(default='')) -> str:
    scheme, _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        raise HTTPException(status_code=401, detail='Sign in first')
    try:
        payload = jwt.decode(token, _secret(), algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Your session expired. Sign in again.')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token. Sign in again.')
    return str(payload['sub'])


UserId = Depends(current_user_id)


def optional_user_id(authorization: str = Header(default='')) -> str | None:
    """Like current_user_id, but returns None when no token is sent (public default plan)."""
    if not authorization:
        return None
    return current_user_id(authorization)


OptionalUserId = Depends(optional_user_id)
