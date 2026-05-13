Backend For Frontend (BFF) - Web App
Este microservicio, desarrollado en Django, actúa como la capa de agregación y orquestación diseñada específicamente para servir al Frontend (React).

Propósito:

Su función principal es simplificar la comunicación para el cliente:

Agregación: Combina datos de múltiples microservicios (Inventario + Pedidos + Envíos) en una sola respuesta.

Formateo: Entrega los datos exactamente como React los necesita, reduciendo el procesamiento en el navegador.

Seguridad: Valida sesiones y tokens antes de redirigir las peticiones al ApiGateway.

Instalación y Configuración:

Entorno Virtual y Dependencias:

Bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
Variables de Entorno (.env):
Es crucial configurar las URLs de los servicios que consume:

Fragmento de código
API_GATEWAY_URL=http://api-gateway-service:8000
DEBUG=True


Ejecución:

python manage.py runserver
