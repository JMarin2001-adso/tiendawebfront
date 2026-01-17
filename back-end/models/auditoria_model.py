
from pydantic import BaseModel
from typing import Optional

class AuditoriaCreate(BaseModel):
    tabla_afectada: str
    id_registro: int
    accion: str
    descripcion: str
    estado_anterior: Optional[str] = None
    estado_nuevo: Optional[str] = None
    detalle: Optional[str] = None

class PedidoPagado(BaseModel):
    id_pedido: int
    metodo_pago: str
    referencia: str
    valor_pagado: float