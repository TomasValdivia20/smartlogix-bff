import httpx
from django.conf import settings

BASE_URL = f"{settings.MS_LOGIN_URL}/api/login/"

async def procesar_login(credenciales: dict):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(BASE_URL, json=credenciales)
            
            if response.status_code >= 400:
                try:
                    return response.json(), response.status_code
                except:
                    return {"error": f"Página no encontrada (404). URL intentada: {response.url}"}, response.status_code
                    
            return response.json(), 200
        except Exception as e:
            return {"error": f"Error de conexión con MS-Login: {str(e)}"}, 500