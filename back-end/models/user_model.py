from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    nombre:str
    correo:str
    telefono:str
    direccion:str
    usuario:str
    contrasena:str
    rol:str
    estado:Optional[int] = 1  

class LoginRequest(BaseModel):
    correo: str
    contrasena: str

class LoginEmpleado(BaseModel):
    usuario: str
    contrasena: str


class DireccionUpdate(BaseModel):
    direccion: str
    ciudad: str
    postal: str



