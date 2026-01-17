from fastapi import APIRouter
from models.factura_model import FacturaElectronicaCreate, FacturaManualCreate,BuscarUsuarioDocumento,ClienteManual
from services.factura_service import FacturaService

router = APIRouter(
    prefix="/factura",
    tags=["Factura"]
)

@router.get("/busqueda-documento/{documento}")
def buscar_usuario(documento: str):
    service = FacturaService()
    return service.buscar_por_documento(documento)


@router.post("/online")
def crear_factura_online(data: FacturaElectronicaCreate):
    service = FacturaService()
    return service.crear_factura_online(data)

@router.post("/cliente/manual")
def crear_cliente_manual(data: ClienteManual):
    service = FacturaService()
    return service.crear_cliente_manual(data)

@router.post("/manual")
def crear_factura_manual(data: FacturaManualCreate):
    service = FacturaService()
    return service.crear_factura_manual(data)


@router.get("/buscar-por-documento/{documento}")
def buscar_facturas_documento(documento: str):
    service = FacturaService()
    return service.obtener_historial_facturas(documento)

@router.get("/buscar-por-factura/{numero_factura}")
def buscar_factura(numero_factura: str):
    service = FacturaService()
    return service.buscar_por_factura(numero_factura)

@router.get("/detalle/{id_factura}")
def detalle_factura(id_factura: int):
    service = FacturaService()
    return service.obtener_detalle_factura(id_factura)
