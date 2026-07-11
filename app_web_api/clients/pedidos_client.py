# app_web_api/clients/pedidos_client.py
import os
import httpx
from urllib.parse import urlparse
from app_web_api.auth import make_tenant_headers

# URL del Microservicio de Pedidos (Puerto 8007 y la ruta base del MS)
URL_MS_PEDIDOS = os.environ.get('URL_MS_PEDIDOS', 'http://127.0.0.1:8007/pedidos/')


def _safe_json(response):
    try:
        return response.json()
    except Exception:
        return {"error": f"Respuesta inesperada (status {response.status_code})"}


async def enviar_crear_pedido(datos_pedido: dict, request=None):
    """Viaja al MS de Pedidos a guardar un nuevo pedido en la base de datos"""
    headers = make_tenant_headers(request) if request else {}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(URL_MS_PEDIDOS, json=datos_pedido, headers=headers, timeout=5.0)
            if response.status_code == 201:
                return response.json(), 201
            return response.json(), response.status_code
        except httpx.RequestError:
            return {"error": "No se pudo conectar con el microservicio de Pedidos"}, 503
        
async def obtener_todos_los_pedidos(request=None):
    """Viaja al Microservicio de Pedidos a buscar la lista completa"""
    headers = make_tenant_headers(request) if request else {}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(URL_MS_PEDIDOS, headers=headers, timeout=5.0)
            return response.json(), response.status_code
        except httpx.RequestError as exc:
            return {"error": f"Microservicio de pedidos no disponible: {str(exc)}"}, 503

async def enviar_nuevo_pedido(payload: dict, token_autorizacion: str = None, request=None):
    """Viaja al Microservicio de Pedidos a guardar un nuevo pedido"""
    headers = {}
    if token_autorizacion:
        headers["Authorization"] = token_autorizacion
    headers.update(make_tenant_headers(request) if request else {})

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(URL_MS_PEDIDOS, json=payload, headers=headers, timeout=5.0)
            return response.json(), response.status_code
        except httpx.RequestError as exc:
            return {"error": f"No se pudo conectar con el servicio central: {str(exc)}"}, 503

async def obtener_pedido_por_id(pedido_id: str, request=None):
    """Viaja al MS de Pedidos a buscar un pedido específico usando su UUID"""
    url = f"{URL_MS_PEDIDOS}{pedido_id}/"
    headers = make_tenant_headers(request) if request else {}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=5.0)
            if response.status_code == 200:
                return response.json()
            return None
        except httpx.RequestError:
            return None


async def aprobar_pedido(pedido_id: str, request=None):
    """Pendiente → Aprobado"""
    headers = make_tenant_headers(request) if request else {}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(f"{URL_MS_PEDIDOS}{pedido_id}/aprobar/", headers=headers, timeout=5.0)
            return _safe_json(response), response.status_code
        except httpx.RequestError:
            return {"error": "No se pudo conectar con el microservicio de Pedidos"}, 503


async def enviar_pedido(pedido_id: str, request=None):
    """Aprobado → Enviado"""
    headers = make_tenant_headers(request) if request else {}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(f"{URL_MS_PEDIDOS}{pedido_id}/enviar/", headers=headers, timeout=5.0)
            return _safe_json(response), response.status_code
        except httpx.RequestError:
            return {"error": "No se pudo conectar con el microservicio de Pedidos"}, 503


async def entregar_pedido(pedido_id: str, request=None):
    """Enviado → Entregado"""
    headers = make_tenant_headers(request) if request else {}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(f"{URL_MS_PEDIDOS}{pedido_id}/entregar/", headers=headers, timeout=5.0)
            return _safe_json(response), response.status_code
        except httpx.RequestError:
            return {"error": "No se pudo conectar con el microservicio de Pedidos"}, 503


async def obtener_guia(pedido_id: str, request=None):
    """Obtiene la guía de despacho de un pedido"""
    headers = make_tenant_headers(request) if request else {}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{URL_MS_PEDIDOS}{pedido_id}/guia/", headers=headers, timeout=5.0)
            return _safe_json(response), response.status_code
        except httpx.RequestError:
            return {"error": "No se pudo conectar con el microservicio de Pedidos"}, 503


async def generar_guia(pedido_id: str, request=None):
    """Genera una guía de despacho para un pedido aprobado"""
    headers = make_tenant_headers(request) if request else {}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{URL_MS_PEDIDOS}{pedido_id}/guia/", headers=headers, timeout=5.0)
            data = _safe_json(response)
            if response.status_code == 201:
                return data, 201
            return data, response.status_code
        except httpx.RequestError:
            return {"error": "No se pudo conectar con el microservicio de Pedidos"}, 503


async def listar_bodegas(request=None):
    """Lista todas las bodegas activas"""
    url_base = os.environ.get('URL_MS_PEDIDOS', 'http://127.0.0.1:8007/api/pedidos/')
    parsed = urlparse(url_base)
    root_url = f"{parsed.scheme}://{parsed.netloc}/"
    headers = make_tenant_headers(request) if request else {}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{root_url}bodegas/", headers=headers, timeout=5.0)
            return _safe_json(response), response.status_code
        except httpx.RequestError:
            return {"error": "No se pudo conectar con el microservicio de Pedidos"}, 503