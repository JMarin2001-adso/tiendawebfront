import asyncio
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import pymysql
import pymysql.cursors
from db.db_mysql import get_db_connection
from models.cliente_model import UserClienteCreate
from models.user_model import LoginRequest, User, LoginEmpleado,DireccionUpdate



class UserService:
    def __init__(self):
        self.con = get_db_connection()
        if self.con is None:
            raise Exception("no se pudo establecer conexion")

    def close_connection(self):
        if self.con:
            self.con.close()

    def _get_users_sync(self):
        try:#ayuda a manejar la excepciones de manera controlada,presentando los errores
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM usuario")
                users = cursor.fetchall()
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "usuarios obtenidos exitosamente",
                    "data": users if users else []
                }
            )
        except Exception as e:
            print("error en get_users", str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"error al obtener los usuarios {str(e)}",
                    "data": None
                }
            )
        finally:
            self.close_connection()

    async def get_users(self):
        return await asyncio.to_thread(self._get_users_sync)

    def _get_user_by_id_sync(self, user_id: int):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT * FROM usuario WHERE id_usuario = %s"
                cursor.execute(sql, (user_id,))
                user = cursor.fetchone()
            if user:
                return JSONResponse(
                    status_code=200,
                    content={"success": True, "message": "usuario encontrado", "data": user}
                )
            else:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "message": "usuario no encontrado", "data": None}
                )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": f"error al consultar el usuario: {str(e)}", "data": None}
            )
        finally:
            self.close_connection()

    async def get_user_by_id(self, user_id: int):
        return await asyncio.to_thread(self._get_user_by_id_sync, user_id)
    
    def _crear_usuario_sync(self, data: User):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = """INSERT INTO usuario 
                         (nombre, correo, telefono, direccion, usuario, contrasena, rol, estado) 
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
                cursor.execute(sql, (
                    data.nombre, data.correo, data.telefono, data.direccion,
                    data.usuario, data.contrasena, data.rol, data.estado))
                self.con.commit()
            return {"mensaje": "Usuario creado correctamente"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            self.close_connection()

    async def crear_usuario(self, data: User):
        return await asyncio.to_thread(self._crear_usuario_sync, data)


    def _crear_usuario_cliente_sync(self, data: UserClienteCreate):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = """
                    INSERT INTO usuario 
                    (nombre, correo, telefono, contrasena, rol, estado) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    data.nombre,
                    data.correo,
                    data.telefono,
                    data.contrasena,
                    "cliente",  # rol
                    1           # estado activo
                ))
                self.con.commit()
            return {"mensaje": "Cliente registrado correctamente"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            self.close_connection()

    async def crear_usuario_cliente(self, data: UserClienteCreate):
        return await asyncio.to_thread(self._crear_usuario_cliente_sync, data)

    
    def _change_password_sync(self, user_id: int, new_password: str):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                check_sql = "SELECT COUNT(*) FROM usuario WHERE id_usuario = %s"
                cursor.execute(check_sql, (user_id,))
                result = cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "message": "usuario no existe", "data": None}
                    )

                sql = "UPDATE usuario SET contrasena=%s WHERE id_usuario=%s"
                cursor.execute(sql, (new_password, user_id))
                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(
                        content={"success": True, "message": "Contraseña actualizada exitosamente."}, status_code=200
                    )
                else:
                    return JSONResponse(
                        content={"success": False, "message": "No se realizaron cambios."}, status_code=409
                    )
        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                content={"success": False, "message": f"Error al actualizar la contraseña: {str(e)}"}, status_code=500
            )
        finally:
            self.close_connection()

    async def change_password(self, user_id: int, new_password: str):
        return await asyncio.to_thread(self._change_password_sync, user_id, new_password)

   
    def _inactivate_user_sync(self, user_id: int):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                check_sql = "SELECT COUNT(*) FROM usuario WHERE id_usuario=%s"
                cursor.execute(check_sql, (user_id,))
                result = cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(
                        content={"success": False, "message": "Usuario no encontrado."}, status_code=404
                    )

                sql = "UPDATE usuario SET estado=0 WHERE id_usuario=%s"
                cursor.execute(sql, (user_id,))
                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(
                        content={"success": True, "message": "Usuario inactivado exitosamente."}, status_code=200
                    )
                else:
                    return JSONResponse(
                        content={"success": False, "message": "No se realizaron cambios."}, status_code=400
                    )
        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                content={"success": False, "message": f"Error al inactivar usuario: {str(e)}"}, status_code=500
            )
        finally:
            self.close_connection()

    async def inactivate_user(self, user_id: int):
        return await asyncio.to_thread(self._inactivate_user_sync, user_id)

    def _toggle_user_status_sync(self, user_id: int):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                get_estado_sql = "SELECT estado FROM usuario WHERE id_usuario=%s"
                cursor.execute(get_estado_sql, (user_id,))
                result = cursor.fetchone()

                if not result:
                    return JSONResponse(
                        content={"success": False, "message": "Usuario no encontrado."}, status_code=404
                    )

                estado_actual = result[0]
                nuevo_estado = 0 if estado_actual == 1 else 1

                update_sql = "UPDATE usuario SET estado=%s WHERE id_usuario=%s"
                cursor.execute(update_sql, (nuevo_estado, user_id))
                self.con.commit()

                return JSONResponse(
                    content={"success": True, "message": "Estado actualizado correctamente."}, status_code=200
                )
        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                content={"success": False, "message": f"Error al cambiar estado: {str(e)}"}, status_code=500
            )
        finally:
            self.close_connection()

    async def toggle_user_status(self, user_id: int):
        return await asyncio.to_thread(self._toggle_user_status_sync, user_id)

    def _update_user_sync(self, user_id: int, user_data: User):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                check_sql = "SELECT COUNT(*) FROM usuario WHERE id_usuario=%s"
                cursor.execute(check_sql, (user_id,))
                result = cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(
                        content={"success": False, "message": "Usuario no encontrado."}, status_code=404
                    )

                update_sql = """
                    UPDATE usuario
                    SET nombre=%s, correo=%s, telefono=%s, direccion=%s, usuario=%s, contrasena=%s, rol=%s
                    WHERE id_usuario=%s
                """
                cursor.execute(update_sql, (
                    user_data.nombre,
                    user_data.correo,
                    user_data.telefono,
                    user_data.direccion,
                    user_data.usuario,
                    user_data.contrasena,
                    user_data.rol,
                    user_id
                ))
                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(
                        content={"success": True, "message": "Usuario actualizado correctamente."}, status_code=200
                    )
                else:
                    return JSONResponse(
                        content={"success": False, "message": "No se realizaron cambios."}, status_code=409
                    )
        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                content={"success": False, "message": f"Error al actualizar usuario: {str(e)}"}, status_code=500
            )
        finally:
            self.close_connection()

    async def update_user(self, user_id: int, user_data: User):
        return await asyncio.to_thread(self._update_user_sync, user_id, user_data)

    
    def _login_sync(self, data: LoginRequest):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT id_usuario, nombre, correo, telefono  FROM usuario WHERE correo=%s AND contrasena=%s"
                cursor.execute(sql, (data.correo, data.contrasena))
                user = cursor.fetchone()
                
                if user:
                    return {
                    "success": True,
                    "mensaje": "Login exitoso",
                    "id_usuario": user["id_usuario"],
                    "nombre": user["nombre"], 
                    "correo": user["correo"],
                    "telefono": user["telefono"]
                }
                else:
                    raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
        except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error en login: {str(e)}")
        finally:
            self.close_connection()

    async def login(self, data: LoginRequest):
        return await asyncio.to_thread(self._login_sync, data)

    def _login_empleado_sync(self, data: LoginEmpleado):
        """
        Valida que el usuario exista, la contraseña sea correcta
        y que el rol sea 'empleado' o 'superadmin'.
        """
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                    SELECT * FROM usuario
                    WHERE usuario=%s AND contrasena=%s
                      AND (rol='empleado' OR rol='superadmin')
                """
                cursor.execute(sql, (data.usuario, data.contrasena))
                user = cursor.fetchone()

                if user:
                    return user
                else:
                    raise HTTPException(status_code=401,
                        detail="Usuario o contraseña incorrectos o rol no autorizado")
        except Exception as e:
            raise HTTPException(status_code=500,
                detail=f"Error en login empleado: {str(e)}")
        finally:
            self.close_connection()

    async def login_empleado(self, data: LoginEmpleado):
        return await asyncio.to_thread(self._login_empleado_sync, data)
    
    def actualizar_direccion(self, id_usuario: int, data: DireccionUpdate):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = """
            UPDATE usuario 
            SET direccion=%s, ciudad=%s, postal=%s
            WHERE id_usuario=%s
            """
                cursor.execute(sql, (data.direccion, data.ciudad, data.postal, id_usuario))
                self.con.commit()
                return {"success": True, "message": "Dirección actualizada correctamente"}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            self.close_connection()




    def obtener_o_crear_usuario_fisico(self, cliente):
        with self.con.cursor() as cursor:
            cursor.execute("""
                SELECT id_usuario
                FROM usuario
                WHERE documento = %s
            """, (cliente["documento"],))

            usuario = cursor.fetchone()

            if usuario:
                return usuario["id_usuario"]

            cursor.execute("""
                INSERT INTO usuario
                (documento, nombre, telefono, correo, direccion, tipo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                cliente["documento"],
                cliente["nombre"],
                cliente.get("telefono"),
                cliente.get("correo"),
                cliente.get("direccion"),
                "fisico"
            ))

            self.con.commit()
            return cursor.lastrowid

