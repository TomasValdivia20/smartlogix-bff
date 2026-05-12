from ninja import NinjaAPI
from .clients.inventario_client import obtener_todos_los_productos

# Instanciamos la API con los datos de tu plataforma
api = NinjaAPI(
    title="SmartLogix BFF API",
    description="API Gateway que orquesta la comunicación entre React, Inventario y Pedidos.",
    version="1.0.0"
)

# Un endpoint de prueba súper rápido
@api.get("/health")
def health_check(request):
    return {
        "status": "ok", 
        "message": "¡El BFF de SmartLogix está vivo, respirando y listo para orquestar!"
    }
# --- NUEVO ENDPOINT ASÍNCRONO ---
@api.get("/productos")
async def listar_productos_bff(request):
    # El BFF llama a su "mensajero" y espera la lista de productos
    datos = await obtener_todos_los_productos()
    return datos