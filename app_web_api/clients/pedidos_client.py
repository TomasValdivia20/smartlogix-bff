# app_web_api/clients/pedidos_client.py
import os
import httpx

# URL del Microservicio de Pedidos (Puerto 8007 y la ruta base del MS)
URL_MS_PEDIDOS = os.environ.get('URL_MS_PEDIDOS', 'http://127.0.0.1:8007/pedidos/')

async def obtener_todos_los_pedidos():
    """Viaja al Microservicio de Pedidos a buscar la lista completa"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(URL_MS_PEDIDOS, timeout=5.0)
            # Devolvemos los datos del JSON y el código de estado (ej: 200)
            return response.json(), response.status_code
        except httpx.RequestError as exc:
            # Si el microservicio está apagado, avisamos al BFF de forma segura
            return {"error": f"Microservicio de pedidos no disponible: {str(exc)}"}, 503

async def enviar_nuevo_pedido(payload: dict, token_autorizacion: str = None):
    """Viaja al Microservicio de Pedidos a guardar un nuevo pedido"""
    headers = {}
    if token_autorizacion:
        headers["Authorization"] = token_autorizacion

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(URL_MS_PEDIDOS, json=payload, headers=headers, timeout=5.0)
            return response.json(), response.status_code
        except httpx.RequestError as exc:
            return {"error": f"No se pudo conectar con el servicio central: {str(exc)}"}, 503