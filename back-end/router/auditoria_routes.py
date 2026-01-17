
from fastapi import APIRouter
from models.auditoria_model import AuditoriaCreate, PedidoPagado
from services.auditoria_service import AuditoriaService

router = APIRouter(prefix="/auditoria")

@router.post("/registrar")
def registrar(data: AuditoriaCreate):
    service = AuditoriaService()
    return service.registrar_evento(data)

@router.get("/notificaciones")
def listar_revision():
    service = AuditoriaService()
    return service.listar_por_accion("UPDATE")

@router.post("/notificaciones/pedido-pagado")
def notificar_pago(data: PedidoPagado):
    return {
        "mensaje": "Notificación registrada",
        "pedido_pagado": data.id_pedido,
        "monto": data.valor_pagado
    }
