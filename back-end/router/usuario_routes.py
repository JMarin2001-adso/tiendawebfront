from fastapi import APIRouter,HTTPException
from services.user_service import UserService
from models.user_model import LoginRequest, User,LoginEmpleado,DireccionUpdate
from fastapi import Request
from models.cliente_model import UserClienteCreate

routes = APIRouter(prefix="/user", tags=["users"])


user_service = UserService()

user_model = User

@routes.get("/get-users/")
async def get_all_users():
    result = await user_service.get_users()
    return result

@routes.get("/users/{user_id}")
async def get_user(user_id: int):
    return await user_service.get_user_by_id(user_id)

@routes.post("/clientes/registrar/")
async def registrar_cliente(cliente: UserClienteCreate):
    return await user_service.crear_usuario_cliente(cliente)


@routes.post("/nombre-metodo/")
async def nombre_metodo():
    return "Nombre método"

@routes.post("/crear/")
async def crear_usuario(user: User):
    return await user_service.crear_usuario(user)

@routes.patch("/change-password/")
async def change_password(user_id: int, new_Password):
    return await user_service.change_password(user_id, new_Password)

@routes.patch("/inactivate/{user_id}")
async def inactivate_user(user_id: int):
    return await user_service.inactivate_user(user_id)

@routes.patch("/change-status/{user_id}")
async def change_user_status(user_id: int):
    return await user_service.toggle_user_status(user_id)


@routes.post("/login/")
async def login(data: LoginRequest):
    user = await user_service.login(data)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"mensaje": "Login exitoso", "usuario": user}

@routes.post("/login-empleado/")
async def login_empleado(data: LoginEmpleado):
    user = await user_service.login_empleado(data)
    if not user or user.get("rol") not in ("empleado", "superadmin"):
        raise HTTPException(status_code=401, detail="Solo empleados autorizados")
    return {"mensaje": "Login empleado exitoso", "usuario": user}

@routes.put("/usuario/{id_usuario}/direccion")
def actualizar_direccion(id_usuario: int, data: DireccionUpdate):
    return user_service.actualizar_direccion(id_usuario, data)