import httpx
from django.conf import settings

async def obtener_todos_los_productos():
    """
    Va al MS-Inventario de forma asíncrona y trae la lista de productos.
    """
    url = f"{settings.MS_INVENTARIO_URL}/api/inventario/productos/"
    
    # Abrimos un cliente asíncrono temporal
    async with httpx.AsyncClient() as client:
        try:
            # Hacemos la petición GET y ESPERAMOS (await) la respuesta
            response = await client.get(url)
            
            # Si el MS-Inventario devuelve error (ej. 404 o 500), lanza una excepción
            response.raise_for_status() 
            
            # Devolvemos el JSON crudo
            return response.json()
            
        except httpx.RequestError as e:
            # ¡Aquí a futuro entrará el Circuit Breaker! Por ahora, imprimimos el error.
            print(f"Error de conexión con MS-Inventario: {e}")
            return [] # Devolvemos lista vacía para no romper el frontend