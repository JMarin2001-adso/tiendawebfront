from pydantic import BaseModel
from typing import Optional

class UserClienteCreate(BaseModel):
    nombre: str
    correo: str
    telefono:str
    contrasena: str
    usuario: Optional[str] = None