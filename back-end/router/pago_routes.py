from fastapi import APIRouter
from services.pago_service import PagoService
from models.pago_model import PagoClienteCreate

router = APIRouter(prefix="/pagos", tags=["pagos"])


@router.post("/registrar")
def registrar_pago(data: PagoClienteCreate):
    service = PagoService()
    return service.registrar_pago_sync(data)


@router.get("/notificaciones")
def notificaciones_pagos():
    service = PagoService()
    return service.listar_notificaciones_sync()
