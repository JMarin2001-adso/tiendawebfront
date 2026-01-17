from pydantic import BaseModel, Field

class PagoClienteCreate(BaseModel):
    id_pedido: int
    metodo_pago: str = Field(..., example="tarjeta")
    estado_pago: str = Field(..., example="pagado")   # "pagado" | "fallido"
    monto: float
    descripcion: str | None = None  
