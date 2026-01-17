from pydantic import BaseModel
from typing import Optional
from datetime import date

class ProductoCreate(BaseModel):
    nombre: str
    descripcion: str
    precio: float
    id_categoria: int
    categoria: str
    imagen: Optional[str] = None  # ruta (ej: "uploads/DOLCEGABANNA1.webp")

class InventarioEntradaCreate(BaseModel):
    id_producto: int
    nombre_producto: str                
    precio_adquirido: float
    cantidad: int
    fecha_ingreso: date
    id_proveedor: int                   
    observacion: Optional[str] = None

class InventarioSalidaCreate(BaseModel):
    id_producto: int
    cantidad: int
    fecha_salida: date
    observacion: Optional[str] = None
    id_usuario: int

class EntradaStock(BaseModel):
    id_producto: int
    precio_adquirido:float
    cantidad: int
    fecha_ingreso: date
    id_proveedor: int
    observacion: Optional[str] = None
    

class ProductoUpdate(BaseModel):
    id_producto: int
    nombre: str
    precio: float
    disponible: bool = True
    stock_actual:int