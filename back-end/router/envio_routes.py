from fastapi import APIRouter
from services.envio_service import EnvioService
from models.envio_model import EnvioEstadoUpdate

router = APIRouter(prefix="/envio", tags=["Envios"])

@router.get("/listar")
def listar_envios():
    service = EnvioService()
    return service.listar_envios_sync()


@router.get("/estado/{estado}")
def listar_por_estado(estado: str):
    service = EnvioService()
    return service.listar_envios_estado_sync(estado)


@router.get("/pedido/{id_pedido}")
def obtener_envio_pedido(id_pedido: int):
    service = EnvioService()
    return service.obtener_envio_por_pedido(id_pedido)



@router.put("/transito/{id_envio}")
def marcar_en_transito(id_envio: int):
    service = EnvioService()
    return service.marcar_en_transito_sync(id_envio)


@router.put("/entregar/{id_envio}")
def confirmar_entrega(id_envio: int):
    service = EnvioService()
    return service.confirmar_entrega_sync(id_envio)

@router.get("/notificaciones/{id_usuario}")
def listar_notificaciones(id_usuario: int):
    service = EnvioService()
    return service.obtener_notificaciones_usuario(id_usuario)

