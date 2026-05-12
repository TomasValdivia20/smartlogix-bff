import httpx
from django.conf import settings

# URL base desde los settings
BASE_URL = f"{settings.MS_USUARIO_URL}/api/usuario/"

async def listar_usuarios_pyme():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BASE_URL)
            response.raise_for_status()
            return response.json()
        except Exception:
            return [] # Fallback: lista vacía

async def registrar_usuario_pyme(datos: dict):
    async with httpx.AsyncClient() as client:
        try:
            # Enviamos el POST al puerto 8001
            response = await client.post(BASE_URL, json=datos)
            
            # Si el microservicio devuelve un error (400, 500, etc.)
            if response.status_code >= 400:
                try:
                    return response.json(), response.status_code
                except:
                    return {"error": f"Error del servidor: {response.text[:100]}"}, response.status_code
            
            return response.json(), response.status_code
        except Exception as e:
            return {"error": f"Error de conexión: {str(e)}"}, 500

async def obtener_usuario_por_rut(rut: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}{rut}/")
            response.raise_for_status()
            return response.json()
        except Exception:
            return {"error": "Usuario no encontrado"}

async def actualizar_usuario_pyme(rut: str, datos: dict):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(f"{BASE_URL}{rut}/", json=datos)
            return response.json(), response.status_code
        except Exception as e:
            return {"error": str(e)}, 500

async def eliminar_usuario_pyme(rut: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(f"{BASE_URL}{rut}/")
            return {"mensaje": "Eliminado con éxito"}, 200
        except Exception as e:
            return {"error": str(e)}, 500