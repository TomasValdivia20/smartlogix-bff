import os
from ninja import NinjaAPI, Schema, Router
from typing import Optional
from .clients.inventario_client import obtener_todos_los_productos
from .clients.pedidos_client import (
    obtener_pedido_por_id,
    enviar_crear_pedido,
    aprobar_pedido,
    enviar_pedido,
    entregar_pedido,
    obtener_guia,
    generar_guia,
    listar_bodegas,
)
from .clients import usuario_client
from .clients import login_client
from .clients import pedidos_client  # <-- Añade esta línea arriba
from .clients import envios_client
import httpx
import json
from .schemas import CrearPedidoBffIn
from app_web_api.auth import make_tenant_headers, extract_tenant_rut
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
    datos = await obtener_todos_los_productos(request=request)
    return datos
@api.post("/productos")
async def bff_crear_producto(request):
    # 1. Tomamos el JSON puro que envía el Front, sin que Ninja lo bloquee
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return api.create_response(request, {"error": "Formato JSON inválido"}, status=400)

    url_ms_inventario = "http://127.0.0.1:8002/api/inventario/productos/"

    headers = {}
    if "Authorization" in request.headers:
        headers["Authorization"] = request.headers["Authorization"]
    headers.update(make_tenant_headers(request))

    async with httpx.AsyncClient() as client:
        response = await client.post(url_ms_inventario, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            return api.create_response(
                request,
                response.json(),
                status=response.status_code
            )
        
#ENDPOINTS 
@api.post("/usuarios")
async def bff_crear_usuario(request, data: UsuarioPymeIn):
    respuesta, status_code = await usuario_client.registrar_usuario_pyme(data.model_dump())
    if status_code in [200, 201]:
        return respuesta
    return api.create_response(request, respuesta, status=status_code)

@api.get("/usuarios")
async def bff_listar_usuarios(request):
    return await usuario_client.listar_usuarios_pyme()

@api.get("/usuarios/{rut}")
async def bff_detalle_usuario(request, rut: str):
    return await usuario_client.obtener_usuario_por_rut(rut)

@api.patch("/usuarios/{rut}")
async def bff_actualizar_usuario(request, rut: str, data: UsuarioPymeUpdateIn):
    datos_actualizar = {k: v for k, v in data.model_dump().items() if v is not None}
    respuesta, status_code = await usuario_client.actualizar_usuario_pyme(rut, datos_actualizar)
    if status_code == 200:
        return respuesta
    return api.create_response(request, respuesta, status=status_code)

@api.post("/login")
async def bff_login(request, data: LoginIn):
    respuesta, status_code = await login_client.procesar_login(data.model_dump())
    if status_code == 200:
        return respuesta
    return api.create_response(request, respuesta, status=status_code)

# --- ROUTER ENVIOS (ms-envios) ---
router_envios = Router(tags=["Envíos y Rutas"])

@router_envios.get("/vehiculos/")
async def listar_vehiculos(request):
    data, status = await envios_client.proxy(request, "vehiculos", "GET")
    if status == 200:
        return data
    return api.create_response(request, data, status=status)

@router_envios.get("/vehiculos/{id}/")
async def detalle_vehiculo(request, id: str):
    data, status = await envios_client.proxy(request, f"vehiculos/{id}", "GET")
    if status == 200:
        return data
    return api.create_response(request, data, status=status)

@router_envios.get("/repartidores/")
async def listar_repartidores(request):
    data, status = await envios_client.proxy(request, "repartidores", "GET")
    if status == 200:
        return data
    return api.create_response(request, data, status=status)

@router_envios.get("/envios/")
async def listar_envios(request):
    data, status = await envios_client.proxy(request, "envios", "GET")
    if status == 200:
        return data
    return api.create_response(request, data, status=status)

@router_envios.post("/envios/")
async def crear_envio(request):
    data, status = await envios_client.proxy(request, "envios", "POST")
    if status in (200, 201):
        return data
    return api.create_response(request, data, status=status)

@router_envios.get("/envios/{id}/")
async def detalle_envio(request, id: str):
    data, status = await envios_client.proxy(request, f"envios/{id}", "GET")
    if status == 200:
        return data
    return api.create_response(request, data, status=status)

@router_envios.put("/envios/{id}/")
async def actualizar_envio(request, id: str):
    data, status = await envios_client.proxy(request, f"envios/{id}", "PUT")
    if status == 200:
        return data
    return api.create_response(request, data, status=status)

@router_envios.delete("/envios/{id}/")
async def eliminar_envio(request, id: str):
    data, status = await envios_client.proxy(request, f"envios/{id}", "DELETE")
    if status == 204:
        return data
    return api.create_response(request, data, status=status)

@router_envios.get("/rutas/")
async def listar_rutas(request):
    data, status = await envios_client.proxy(request, "rutas", "GET")
    if status == 200:
        return data
    return api.create_response(request, data, status=status)

@router_envios.post("/rutas/")
async def crear_ruta(request):
    data, status = await envios_client.proxy(request, "rutas", "POST")
    if status in (200, 201):
        return data
    return api.create_response(request, data, status=status)

@router_envios.get("/rutas/{id}/")
async def detalle_ruta(request, id: str):
    data, status = await envios_client.proxy(request, f"rutas/{id}", "GET")
    if status == 200:
        return data
    return api.create_response(request, data, status=status)

@router_envios.put("/rutas/{id}/")
async def actualizar_ruta(request, id: str):
    data, status = await envios_client.proxy(request, f"rutas/{id}", "PUT")
    if status == 200:
        return data
    return api.create_response(request, data, status=status)

@router_envios.delete("/rutas/{id}/")
async def eliminar_ruta(request, id: str):
    data, status = await envios_client.proxy(request, f"rutas/{id}", "DELETE")
    if status == 204:
        return data
    return api.create_response(request, data, status=status)

@router_envios.post("/rutas/{id}/calcular/")
async def calcular_ruta(request, id: str):
    data, status = await envios_client.proxy(request, f"rutas/{id}/calcular", "POST")
    if status == 200:
        return data
    return api.create_response(request, data, status=status)

@router_envios.post("/rutas/{id}/completar/")
async def completar_ruta(request, id: str):
    data, status = await envios_client.proxy(request, f"rutas/{id}/completar", "POST")
    if status == 200:
        return data
    return api.create_response(request, data, status=status)

@router_envios.post("/calcular-costos/")
async def calcular_costos(request):
    data, status = await envios_client.proxy(request, "calcular-costos", "POST")
    if status == 200:
        return data
    return api.create_response(request, data, status=status)

@router_envios.post("/geocodificar/")
async def geocodificar(request):
    data, status = await envios_client.proxy(request, "geocodificar", "POST")
    if status == 200:
        return data
    return api.create_response(request, data, status=status)

@router_envios.get("/productos/")
async def listar_productos(request):
    url_ms_inventario = "http://127.0.0.1:8002/api/inventario/productos/"
    headers = make_tenant_headers(request)
    print(f"[DEBUG BFF GET] X-Tenant-RUT presente: {'X-Tenant-RUT' in headers}, headers={headers}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url_ms_inventario, headers=headers, timeout=5.0)
            return response.json()
        except httpx.RequestError as exc:
            return api.create_response(
                request, {"error": f"Error de conexión con MS-Inventario: {str(exc)}"}, status=503
            )

@router_envios.post("/productos/")
async def crear_producto(request):
    url_ms_inventario = "http://127.0.0.1:8002/api/inventario/productos/"
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return api.create_response(request, {"error": "Formato JSON inválido"}, status=400)
    headers = {}
    if "Authorization" in request.headers:
        headers["Authorization"] = request.headers["Authorization"]
    headers.update(make_tenant_headers(request))
    async with httpx.AsyncClient() as client:
        response = await client.post(url_ms_inventario, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            return response.json()
        return api.create_response(
            request, response.json(), status=response.status_code
        )

# ==========================================
# 1. ENDPOINT PARA CREAR UN PEDIDO (NUEVO)
# ==========================================
# Deja esta ruta fija: "/crear-pedido"

# --- ENDPOINTS DE PEDIDOS (CONFIGURADOS EN EL PUERTO 8007) ---

@api.get("/pedidos")
async def listar_pedidos_bff(request):
    url_ms_pedidos = "http://127.0.0.1:8007/pedidos/"
    headers = make_tenant_headers(request)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url_ms_pedidos, headers=headers, timeout=5.0)
            if response.status_code == 200:
                return response.json()
            return api.create_response(request, response.json(), status=response.status_code)
        except httpx.RequestError as exc:
            return api.create_response(
                request, 
                {"error": f"No se pudo conectar con el microservicio de pedidos en el puerto 8007: {str(exc)}"}, 
                status=503
            )
        
@api.post("/crear-pedido")  
async def crear_pedido_bff(request, payload: CrearPedidoBffIn):
    datos_pedido = payload.model_dump()
    resultado, estado_http = await enviar_crear_pedido(datos_pedido, request=request)
    if estado_http in [200, 201]:
        return resultado
    return api.create_response(request, resultado, status=estado_http)


# ==========================================
# 2. ENDPOINT PARA VER EL PEDIDO CON DETALLES
# ==========================================
@api.get("/pedido-completo/{pedido_id}")
async def obtener_pedido_con_detalles_producto(request, pedido_id: str):
    # 1. Traer el pedido base desde MS-Pedidos
    pedido = await obtener_pedido_por_id(pedido_id, request=request)
    if not pedido:
        return {"error": "El pedido no existe en MS-Pedidos"}

    # 2. Traer la lista directa desde MS-Inventario (Puerto 8002)
    lista_productos = await obtener_todos_los_productos(request=request)
    
    # Armamos el diccionario rápido relacionando SKU con el objeto completo del producto
    productos_dict = {p['sku']: p for p in lista_productos if isinstance(p, dict) and 'sku' in p}

    # 3. Mapear los ítems del pedido
    # DRF puede devolver los productos del pedido como 'items' o 'detalles'
    detalles_del_pedido = pedido.get('items', pedido.get('detalles', []))

    for item in detalles_del_pedido:
        sku_pedido = item.get('sku')
        
        # Si el SKU coincide con lo que tienes en la base de datos de inventario...
        if sku_pedido in productos_dict:
            item['datos_inventario'] = productos_dict[sku_pedido]
        else:
            item['datos_inventario'] = {
                "mensaje": f"El SKU '{sku_pedido}' no existe en el catálogo de Inventario."
            }

    return pedido


# ==========================================
# 3. PROXY ENDPOINTS ADICIONALES PARA MS-PEDIDOS
# ==========================================

@api.get("/pedidos/{pedido_id}")
async def detalle_pedido_bff(request, pedido_id: str):
    url = f"http://127.0.0.1:8007/pedidos/{pedido_id}/"
    headers = make_tenant_headers(request)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=5.0)
            if response.status_code == 200:
                return response.json()
            return api.create_response(request, response.json(), status=response.status_code)
        except httpx.RequestError as exc:
            return api.create_response(
                request,
                {"error": f"No se pudo conectar con ms-pedidos: {str(exc)}"},
                status=503
            )


@api.patch("/pedidos/{pedido_id}/aprobar")
async def aprobar_pedido_bff(request, pedido_id: str):
    resultado, status_code = await aprobar_pedido(pedido_id, request=request)
    if status_code == 200:
        return resultado
    return api.create_response(request, resultado, status=status_code)


@api.patch("/pedidos/{pedido_id}/enviar")
async def enviar_pedido_bff(request, pedido_id: str):
    resultado, status_code = await enviar_pedido(pedido_id, request=request)
    if status_code == 200:
        return resultado
    return api.create_response(request, resultado, status=status_code)


@api.patch("/pedidos/{pedido_id}/entregar")
async def entregar_pedido_bff(request, pedido_id: str):
    resultado, status_code = await entregar_pedido(pedido_id, request=request)
    if status_code == 200:
        return resultado
    return api.create_response(request, resultado, status=status_code)


@api.get("/pedidos/{pedido_id}/guia")
async def obtener_guia_bff(request, pedido_id: str):
    resultado, status_code = await obtener_guia(pedido_id, request=request)
    if status_code == 200:
        return resultado
    return api.create_response(request, resultado, status=status_code)


@api.post("/pedidos/{pedido_id}/guia")
async def generar_guia_bff(request, pedido_id: str):
    resultado, status_code = await generar_guia(pedido_id, request=request)
    if status_code == 201:
        return api.create_response(request, resultado, status=201)
    return api.create_response(request, resultado, status=status_code)


@api.get("/bodegas")
async def listar_bodegas_bff(request):
    resultado, status_code = await listar_bodegas(request=request)
    if status_code == 200:
        return resultado
    return api.create_response(request, resultado, status=status_code)


# ==========================================
# DASHBOARD — Resumen por empresa
# ==========================================

@api.get("/dashboard/resumen")
async def dashboard_resumen(request):
    rut_empresa = extract_tenant_rut(request)
    if not rut_empresa:
        return api.create_response(request, {"error": "No autenticado"}, status=401)

    headers = make_tenant_headers(request)

    async with httpx.AsyncClient() as client:
        try:
            resp_productos = await client.get(
                "http://127.0.0.1:8002/api/inventario/productos/",
                headers=headers, timeout=5.0
            )
            total_productos = len(resp_productos.json()) if resp_productos.status_code == 200 else 0
        except Exception:
            total_productos = 0

        try:
            resp_pedidos = await client.get(
                "http://127.0.0.1:8007/pedidos/",
                headers=headers, timeout=5.0
            )
            pedidos_data = resp_pedidos.json() if resp_pedidos.status_code == 200 else []
            total_pedidos = len(pedidos_data)
            pedidos_entregados = sum(1 for p in pedidos_data if p.get('estado') == 'Entregado')
        except Exception:
            total_pedidos = 0
            pedidos_entregados = 0

        try:
            resp_envios = await client.get(
                "http://127.0.0.1:8006/api/envios/envios/",
                headers=headers, timeout=5.0
            )
            envios_data = resp_envios.json() if resp_envios.status_code == 200 else []
            if isinstance(envios_data, list):
                total_envios = len(envios_data)
                envios_entregados = sum(1 for e in envios_data if e.get('estado') == 'Entregado')
            else:
                total_envios = 0
                envios_entregados = 0
        except Exception:
            total_envios = 0
            envios_entregados = 0

    return {
        "total_productos": total_productos,
        "total_pedidos": total_pedidos,
        "pedidos_entregados": pedidos_entregados,
        "total_envios": total_envios,
        "envios_entregados": envios_entregados,
    }


# ¡LA MAGIA OCURRE AQUÍ! Acoplamos el router a la API principal
api.add_router("/envios", router_envios)
