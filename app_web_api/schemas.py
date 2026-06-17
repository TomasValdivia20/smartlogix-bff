# app_web_api/schemas.py
from typing import Optional
from ninja import Schema

# 👇 Revisa que esté escrito idéntico: C-rear-P-edido-B-ff-I-n
class CrearPedidoBffIn(Schema):
    cliente_id: str
    destinatario: dict
    items: list
    notas: Optional[str] = None
    tipo: str = "estandar"