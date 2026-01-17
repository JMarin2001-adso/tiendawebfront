from fastapi import APIRouter
from services.pedido_service import PedidoService
from models.pedido_model import PedidoClienteCreate,PedidoActualizarEstado

router = APIRouter(prefix="/pedido", tags=["pedidos"])

@router.post("/nuevo")
def crear_pedido(data: PedidoClienteCreate):
    service = PedidoService()
    return service.crear_pedido_sync(data)


@router.get("/pendientes")
def listar_pendientes():
    service = PedidoService()
    return service.listar_pendientes_sync()


@router.put("/estado/{id_pedido}")
def actualizar_estado(id_pedido: int, data: PedidoActualizarEstado):
    service = PedidoService()
    return service.actualizar_estado_sync(id_pedido, data.estado)

@router.put("/aprobar/{id_pedido}")
def aprobar_pedido(id_pedido: int):
    service = PedidoService()
    return service.actualizar_estado_sync(id_pedido, "pagado")

@router.put("/rechazar/{id_pedido}")
def rechazar_pedido(id_pedido: int, data: dict):
    service = PedidoService()
    motivo = data.get("motivo")
    return service.actualizar_estado_sync(id_pedido, "rechazado", motivo)

@router.put("/despachar/{id_pedido}")
def despachar_pedido(id_pedido: int):
    service = PedidoService()
    return service.despachar_pedido_sync(id_pedido)


@router.get("/detalle/{id_pedido}")
def detalle_pedido(id_pedido: int):
    service = PedidoService()
    return service.obtener_detalle_pedido(id_pedido)


