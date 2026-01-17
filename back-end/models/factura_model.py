from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class FacturaElectronicaCreate(BaseModel):
    id_pedido: int
    total: float

class ClienteManual(BaseModel):
    documento: str    
    nombre: str       
    correo: str  
    direccion: str   
    telefono: str     

class ProductoFactura(BaseModel):
    id_producto: int
    cantidad: int
    precio_unitario: float

class FacturaManualCreate(BaseModel):
    cliente: ClienteManual
    productos: List[ProductoFactura]


class BuscarUsuarioDocumento(BaseModel):
    documento: str


class FacturaOut(BaseModel):
    id_factura: int
    numero_factura: str
    documento_cliente: str
    nombre_cliente: str
    total: float
    estado: str
    fecha: datetime
