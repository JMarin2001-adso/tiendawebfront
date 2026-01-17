from dotenv import load_dotenv
import uvicorn #import sirve para importar librerias
from fastapi import FastAPI, status #from sirve para importar recuersos de las librerias
from  fastapi.responses import HTMLResponse #para generara respuestas
from fastapi.middleware.cors import CORSMiddleware #quienes van a tener acceso al servidor
from fastapi.staticfiles import StaticFiles


from router.usuario_routes import routes as usuario_routes
from router.producto_routes import router as producto_routes
from router.envio_routes import router as envio_routes
from router.pedido_routes import router as pedido_rorutes
from router.auditoria_routes import router as auditoria_routes
from router.pago_routes import router as pago_routes
from router.factura_routes import router as factura_routes
#crear aplicacion en FasApi

app= FastAPI()#se creo una aplicacion en fastapi

app.title = "tienda web" #propiedad de titulo de la pagina

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

load_dotenv() #configuracion para variable de entorno, luego de haber creado la carpeta .env con las variables de entorno

app.include_router(usuario_routes)
app.include_router(producto_routes)
app.include_router(envio_routes)
app.include_router(pedido_rorutes)
app.include_router(auditoria_routes)
app.include_router(pago_routes)
app.include_router(factura_routes)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],# allow=permitir origin=origen, el * se tendra que convertir en IP, se permitira el acceso a cualquier, sin embargo esta configuracion se tiene que cambiar mas adelante
    allow_credentials= True,#se usa para pedir contraseñas para el acceso a la api
    allow_methods=["GET","POST","PUT","DELETE", "PATCH"],#metodos http asociados a la crud
    allow_headers=["*"]# permite cabeceras
)#configuracion de la parte de seguridad

#punto inicial del proyecto
@app.get(
    path="/",#la raiz punto de inicio de la aplicacion
    status_code= status.HTTP_200_OK,# siempre se debe configurar, asumimos que el punto inicial todo funciona perfecto
    summary="Default api",
    tags=["APP"]#NOMBRE QUE SE LE DA A LA RUTA
) #ruta principal

def message():#def se utiliza para definir una funcion
    """Inicio de la api

    returns:
         message
    """ #return es un valor de retorno es una respuestaa devolver
    return HTMLResponse("<h1>creacion de pagina</h1>")# HTMLRESPONSES va a llevar un mandar un mensaje en codg html

#CONFIGURACION DEL SERVIDOR
if __name__ == "__main__" : #lo que hace el __name__ es verificar si hay un archivo que se llama main
#lo que hara es lanzar la aplicacion por un puerto
    uvicorn.run(app, host="0.0.0.0", port= 8000, reload=True)







