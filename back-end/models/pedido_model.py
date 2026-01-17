from pydantic import BaseModel
from typing import List



class PedidoClienteItem(BaseModel):
    id_producto: int
    cantidad: int
    precio_unitario: float

class PedidoClienteCreate(BaseModel):
    id_usuario: int
    productos: List[PedidoClienteItem]
    
class PedidoActualizarEstado(BaseModel):
    estado: str  # 0 = revisión, 1 = aprobado, 2 = rechazado
