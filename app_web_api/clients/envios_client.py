import json
import httpx
from django.conf import settings

BASE_URL = settings.MS_ENVIOS_URL

async def proxy(request, path: str, method: str = "GET"):
    url = f"{BASE_URL}/{path}/"
    headers = {}
    if "Authorization" in request.headers:
        headers["Authorization"] = request.headers["Authorization"]

    body = None
    if method in ("POST", "PUT", "PATCH"):
        try:
            body = json.loads(request.body)
        except Exception:
            body = None

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, url, json=body, headers=headers, timeout=10.0)
            data = response.json() if response.text else None
            return data, response.status_code
        except httpx.RequestError as exc:
            return {"error": f"Error de conexión con MS-Envíos: {str(exc)}"}, 503
