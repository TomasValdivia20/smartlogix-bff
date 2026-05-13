from ninja import NinjaAPI, Schema
from typing import List, Optional
from .clients.inventario_client import obtener_todos_los_productos
from .clients import usuario_client
from .clients import login_client
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

# --- ENDPOINTS Usuarios ---


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
