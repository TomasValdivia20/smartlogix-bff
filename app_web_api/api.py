import os
from ninja import NinjaAPI, Schema, Router
from typing import List, Optional
from .clients.inventario_client import obtener_todos_los_productos
from .clients import usuario_client
from .clients import login_client
from .clients import pedidos_client  # <-- Añade esta línea arriba
from ninja import Router
import httpx
import json
# Instanciamos la API con los datos de tu plataforma
api = NinjaAPI(
    title="SmartLogix BFF API",
    description="API Gateway que orquesta la comunicación entre React, Inventario, usuarios y login.",
    version="1.0.0"
)
#ayuda a swagger a entender la estructura de los datos que se esperan en el endpoint de creación de usuario
class UsuarioPymeIn(Schema):
    rut_empresa: str
    razon_social: str
    nombre_empresa: str
    email: str
    telefono: str
    direccion: str
    codigo_sii: str
    password: str
class UsuarioPymeUpdateIn(Schema): # Todo opcional para el PATCH
    razon_social: Optional[str] = None
    nombre_empresa: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    codigo_sii: Optional[str] = None

class UsuarioPymeOut(Schema): # Lo que devolvemos al frontend
    rut_empresa: str
    razon_social: str
    nombre_empresa: str
    email: str
    rol: str
    activo: bool

class LoginIn(Schema):
    email: str
    password: str

class UsuarioLoginOut(Schema):
    rut_empresa: str
    email: str
    rol: str
    nombre: str

class LoginOut(Schema):
    access_token: str
    token_type: str
    usuario: UsuarioLoginOut


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
@api.post("/productos")
async def bff_crear_producto(request):
    # 1. Tomamos el JSON puro que envía el Front, sin que Ninja lo bloquee
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return api.create_response(request, {"error": "Formato JSON inválido"}, status=400)

    url_ms_inventario = "http://127.0.0.1:8002/api/inventario/productos/"
    
    # 2. Pasamos el Token de seguridad
    headers = {}
    if "Authorization" in request.headers:
        headers["Authorization"] = request.headers["Authorization"]

    # 3. Viaje al MS-Inventario
    async with httpx.AsyncClient() as client:
        response = await client.post(url_ms_inventario, json=payload, headers=headers)
        
        # Si el ms-inventario lo guarda exitosamente (200 o 201 Created)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            # Si el ms-inventario se enoja (ej. "SKU repetido"), le pasamos el error exacto al Front
            return api.create_response(
                request, 
                response.json(), 
                status=response.status_code
            )
        
# --- ENDPOINTS DE PEDIDOS (CONFIGURADOS EN EL PUERTO 8007) ---

@api.get("/pedidos")
async def listar_pedidos_bff(request):
    """El BFF llama de forma asíncrona al MS-Pedidos en el puerto 8007"""
    # Usamos el puerto 8007 y apuntamos directo a /pedidos/ según el urls.py del MS
    url_ms_pedidos = "http://127.0.0.1:8007/pedidos/"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url_ms_pedidos, timeout=5.0)
            if response.status_code == 200:
                return response.json()
            return api.create_response(request, response.json(), status=response.status_code)
        except httpx.RequestError as exc:
            # Si el microservicio en el 8007 está apagado, avisamos con un 503 limpio
            return api.create_response(
                request, 
                {"error": f"No se pudo conectar con el microservicio de pedidos en el puerto 8007: {str(exc)}"}, 
                status=503
            )


@api.post("/pedidos")
async def bff_crear_pedido(request):
    """El BFF toma el JSON del Front y lo envía al puerto 8007"""
    # 1. Tomamos el JSON puro que envía el Front
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return api.create_response(request, {"error": "Formato JSON inválido"}, status=400)

    # Ajustamos la URL exacta hacia el puerto 8007
    url_ms_pedidos = "http://127.0.0.1:8007/pedidos/"
    
    # 2. Pasamos el Token de seguridad si viene desde React
    headers = {}
    if "Authorization" in request.headers:
        headers["Authorization"] = request.headers["Authorization"]

    # 3. Viaje al MS-Pedidos en el puerto 8007
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url_ms_pedidos, json=payload, headers=headers, timeout=5.0)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return api.create_response(request, response.json(), status=response.status_code)
        except httpx.RequestError as exc:
            return api.create_response(
                request, 
                {"error": f"Error de comunicación con el MS-Pedidos (Puerto 8007): {str(exc)}"}, 
                status=503
            )

#ENDPOINTS 
# Agregamos 500: dict aquí
@api.post("/usuarios", response={201: UsuarioPymeOut, 400: dict, 500: dict})
async def bff_crear_usuario(request, data: UsuarioPymeIn):
    respuesta, status_code = await usuario_client.registrar_usuario_pyme(data.dict())
    return status_code, respuesta

# Actualizamos los demás por si acaso para que sean a prueba de balas
@api.get("/usuarios", response=List[UsuarioPymeOut])
async def bff_listar_usuarios(request):
    return await usuario_client.listar_usuarios_pyme()

@api.get("/usuarios/{rut}", response={200: UsuarioPymeOut, 404: dict, 500: dict})
async def bff_detalle_usuario(request, rut: str):
    return await usuario_client.obtener_usuario_por_rut(rut)

@api.patch("/usuarios/{rut}", response={200: UsuarioPymeOut, 400: dict, 500: dict})
async def bff_actualizar_usuario(request, rut: str, data: UsuarioPymeUpdateIn):
    datos_actualizar = {k: v for k, v in data.dict().items() if v is not None}
    respuesta, status_code = await usuario_client.actualizar_usuario_pyme(rut, datos_actualizar)
    return status_code, respuesta

# ¡Agregamos el 404: dict a la lista!
@api.post("/login", response={200: LoginOut, 400: dict, 401: dict, 404: dict, 500: dict})
async def bff_login(request, data: LoginIn):
    respuesta, status_code = await login_client.procesar_login(data.dict())
    return status_code, respuesta

# --- NUEVO ROUTER: ENVIOS Y RUTAS (ms-envios) ---
router_envios = Router(tags=["Envíos y Rutas"])
# Usamos un valor por defecto seguro por si se te olvida ponerlo en el .env
URL_MS_ENVIOS = os.environ.get('URL_MS_ENVIOS', 'http://127.0.0.1:8006/api/envios')

@router_envios.get("/rutas")
async def obtener_rutas(request):
    """
    El BFF va a buscar las rutas al ms-envios de forma asíncrona.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{URL_MS_ENVIOS}/rutas/")
        return response.json()

# ¡LA MAGIA OCURRE AQUÍ! Acoplamos el router a la API principal
api.add_router("/logistica", router_envios)