import jwt
import os

JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'default_secret')
JWT_ALGO   = os.environ.get('JWT_ALGORITHM', 'HS256')


def extract_tenant_rut(request) -> str | None:
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    try:
        payload = jwt.decode(auth[7:], JWT_SECRET, algorithms=[JWT_ALGO])
        return payload.get('rut')
    except jwt.PyJWTError:
        return None


def make_tenant_headers(request) -> dict:
    rut = extract_tenant_rut(request)
    if rut:
        return {'X-Tenant-RUT': rut}
    return {}
