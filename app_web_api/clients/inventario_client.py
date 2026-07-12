import httpx
from django.conf import settings
from app_web_api.auth import make_tenant_headers

MOCK_PRODUCTOS = [
    {
        "sku": "AUD-RZR-KV4X",
        "nombre": "Audífonos Razer Kraken V4 X",
        "tipo_carga": "General",
        "bodega_id": "BOD-CENTRAL-01",
        "precio_costo": 45000.0,
        "precio_venta": 79990.0,
        "descripcion": "Audífonos gaming con sonido envolvente 7.1 y micrófono retráctil",
        "stock_inicial": 15,
        "umbral_critico": 3,
        "umbral_bajo": 8
    },
    {
        "sku": "MON-165HZ-27",
        "nombre": "Monitor Gamer 27' 165Hz",
        "tipo_carga": "Frágil",
        "bodega_id": "BOD-SUR-02",
        "precio_costo": 120000.0,
        "precio_venta": 199990.0,
        "descripcion": "Monitor panel IPS de alta tasa de refresco para eSports",
        "stock_inicial": 8,
        "umbral_critico": 2,
        "umbral_bajo": 5
    },
    {
        "sku": "VAP-UWL-CGBM",
        "nombre": "Uwell Caliburn G4 Mini Pod",
        "tipo_carga": "Peligrosa", # Por las baterías de litio integradas
        "bodega_id": "BOD-NORTE-01",
        "precio_costo": 12000.0,
        "precio_venta": 24990.0,
        "descripcion": "Pod compacto, incluye cartuchos de repuesto",
        "stock_inicial": 42,
        "umbral_critico": 10,
        "umbral_bajo": 20
    },
    {
        "sku": "MEM-RAM-32GB",
        "nombre": "Memoria RAM 32GB (2x16GB) DDR5",
        "tipo_carga": "General",
        "bodega_id": "BOD-CENTRAL-01",
        "precio_costo": 65000.0,
        "precio_venta": 105000.0,
        "descripcion": "Kit de memorias RAM de alto rendimiento",
        "stock_inicial": 2, # Simulando un stock bajo para ver cómo reacciona el sistema
        "umbral_critico": 5,
        "umbral_bajo": 10
    }
]
async def obtener_todos_los_productos(request=None):
    url = f"{settings.MS_INVENTARIO_URL}/api/inventario/productos/"
    headers = make_tenant_headers(request) if request else {}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            
            # Si el servidor responde 404, esto lanzará la excepción HTTPStatusError
            response.raise_for_status() 
            
            return response.json()
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"Error al conectar con Inventario: {e}")
            
            return []