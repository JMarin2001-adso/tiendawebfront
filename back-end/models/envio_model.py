from pydantic import BaseModel
from typing import Optional


class EnvioEstadoUpdate(BaseModel):
    estado: str
