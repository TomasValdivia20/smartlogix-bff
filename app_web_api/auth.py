import jwt
import os

JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'default_secret')
JWT_ALGO   = os.environ.get('JWT_ALGORITHM', 'HS256')


def extract_tenant_rut(request) -> str | None:
    auth = request.headers.get('Authorization', '')
    print(f"[DEBUG AUTH] Authorization header presente: {'si' if auth else 'no'}")
    if auth:
        print(f"[DEBUG AUTH] Authorization header (primeros 50 chars): '{auth[:50]}...'")
    if not auth.startswith('Bearer '):
        print(f"[DEBUG AUTH] No comienza con 'Bearer ', auth='{auth[:30]}'")
        return None
    try:
        payload = jwt.decode(auth[7:], JWT_SECRET, algorithms=[JWT_ALGO])
        print(f"[DEBUG AUTH] JWT decodificado OK, keys del payload: {list(payload.keys())}")
        rut = payload.get('rut')
        print(f"[DEBUG AUTH] rut extraído: '{rut}'")
        return rut
    except jwt.PyJWTError as e:
        print(f"[DEBUG AUTH] Error decodificando JWT: {e}")
        return None


def make_tenant_headers(request) -> dict:
    rut = extract_tenant_rut(request)
    if rut:
        return {'X-Tenant-RUT': rut}
    return {}
