import logging
import httpx
from django.http import HttpResponse, JsonResponse

logger = logging.getLogger(__name__)


def descargar_guia_pdf(request, pedido_id):
    url = f"http://127.0.0.1:8007/pedidos/{pedido_id}/guia/pdf/"
    try:
        response = httpx.get(url, timeout=10.0)
        if response.status_code == 200:
            return HttpResponse(response.content, content_type="application/pdf")

        detail = ""
        try:
            detail = response.json().get("error", response.text)
        except Exception:
            detail = response.text[:500]

        logger.error(
            "[descargar_guia_pdf] ms-pedidos responded %s: %s",
            response.status_code, detail,
        )
        return JsonResponse(
            {"error": f"ms-pedidos error ({response.status_code}): {detail}"},
            status=response.status_code,
        )
    except httpx.RequestError as exc:
        logger.error("[descargar_guia_pdf] connection error: %s", exc)
        return JsonResponse(
            {"error": f"No se pudo conectar con ms-pedidos: {exc}"},
            status=503,
        )
    except Exception as exc:
        logger.error("[descargar_guia_pdf] unexpected error: %s", exc, exc_info=True)
        return JsonResponse(
            {"error": f"Error interno del BFF: {exc}"},
            status=500,
        )
