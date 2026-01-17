import pymysql
import pymysql.cursors
from db.db_mysql import get_db_connection
from fastapi.responses import JSONResponse
from models.factura_model import FacturaElectronicaCreate,ClienteManual,FacturaManualCreate
class FacturaService:
    def __init__(self):
        self.con = get_db_connection()
        if self.con is None:
            raise Exception("No se pudo establecer conexión")

    def close_connection(self):
        if self.con:
            self.con.close()

    def crear_factura_online(self, data: FacturaElectronicaCreate):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_pedido = """
                SELECT id_usuario, total
                FROM pedido_cliente
                WHERE id_pedido = %s
                """
                
                cursor.execute(sql_pedido, (data.id_pedido,))
                pedido = cursor.fetchone()
                if not pedido:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "success": False,
                            "message": "Pedido no encontrado"
                            }
                            )
                id_usuario = pedido["id_usuario"]
                total = pedido["total"]
                
                cursor.execute("SELECT COUNT(*) + 1 AS siguiente FROM factura")
                conteo = cursor.fetchone()
                num_factura = f"FE-{conteo['siguiente']:05d}"
                
                sql_factura = """
                INSERT INTO factura (
                    id_pedido,
                    numero_factura,
                    id_usuario,
                    total,
                    estado,
                    origen
                ) VALUES (%s, %s, %s, %s, 'emitida', 'online')
                """
                
                cursor.execute(sql_factura, (
                    data.id_pedido,
                    num_factura,
                    id_usuario,
                    total
                    ))
                
                id_factura = cursor.lastrowid
                
                sql_detalle = """
                INSERT INTO detalle_venta_backup
                (id_factura, id_producto, cantidad, precio_unitario)
                SELECT
                    %s,
                    dp.id_producto,
                    dp.cantidad,
                    dp.precio_unitario
                FROM detalle_pedido_cliente dp
                WHERE dp.id_pedido = %s
                """
                
                cursor.execute(sql_detalle, (id_factura, data.id_pedido))
                self.con.commit()
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "Factura electrónica registrada exitosamente",
                        "numero_factura": num_factura,
                        "id_factura": id_factura
                        }
                        )
        except Exception as e:
            self.con.rollback()
            print("Error en crear_factura_online:", str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"Error al registrar: {str(e)}"
                    }
                    )
            
        finally:
            self.close_connection()



    def buscar_por_documento(self, documento: str):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                SELECT  nombre, documento, telefono, correo, direccion
                FROM usuario
                WHERE documento = %s
                """
                cursor.execute(sql, (documento,))
                usuario = cursor.fetchone()
                
                if not usuario:
                    return JSONResponse(
                        status_code=404,
                        content={"success": False, "message": "Usuario no encontrado"}
                        )
                return JSONResponse(
                    status_code=200,
                    content={"success": True, "data": usuario}
                    )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": str(e)}
                )
        finally:
            self.close_connection()



    def crear_cliente_manual(self, data: ClienteManual):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:

                # Verificar si ya existe usuario
                cursor.execute(
                    "SELECT id_usuario FROM usuario WHERE documento = %s",
                    (data.documento,)
                )
                if cursor.fetchone():
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "El cliente ya existe"
                        }
                    )

                # Insertar cliente
                sql = """
                INSERT INTO usuario (documento, nombre, correo, direccion, telefono, rol)
                VALUES (%s, %s, %s, %s, %s, 'cliente')
                """
                cursor.execute(sql, (
                    data.documento,
                    data.nombre,
                    data.correo,
                    data.direccion,
                    data.telefono
                ))

                self.con.commit()

                return {
                    "success": True,
                    "data": {
                        "documento": data.documento,
                        "nombre": data.nombre,
                        "correo": data.correo,
                        "direccion": data.direccion,
                        "telefono": data.telefono
                    }
                }

        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": str(e)
                }
            )
        finally:
            self.close_connection()
        

    def crear_factura_manual(self, data: FacturaManualCreate):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                # obtiene al cliente registrado 
                cursor.execute("SELECT id_usuario FROM usuario WHERE documento = %s", (data.cliente.documento,))
                usuario = cursor.fetchone()
                
                if not usuario:
                    return JSONResponse(status_code=404, content={"success": False, "message": "Cliente no encontrado"})
                
                id_usuario = usuario['id_usuario']

                # Genera número de factura
                cursor.execute("SELECT COUNT(*) + 1 as siguiente FROM factura")
                conteo = cursor.fetchone()
                num_factura = f"FM-{conteo['siguiente']:05d}"

                #Calcular total de productos
                total_factura = sum(p.cantidad * p.precio_unitario for p in data.productos)

                # Insertar cabecera de factura
               
                sql_factura = """
                    INSERT INTO factura (id_usuario, numero_factura, total, estado, origen)
                    VALUES (%s, %s, %s, 'emitida', 'manual')
                """
                cursor.execute(sql_factura, (id_usuario, num_factura, total_factura))
                id_factura = cursor.lastrowid

                # detalle de factura y afectacion de stock
                for prod in data.productos:
                    sql_stock = """
                        UPDATE inventario 
                        SET stock_actual = stock_actual - %s 
                        WHERE id_producto = %s AND stock_actual >= %s
                    """
                    cursor.execute(sql_stock, (prod.cantidad, prod.id_producto, prod.cantidad))
                    
                    if cursor.rowcount == 0:
                        self.con.rollback()
                        return JSONResponse(status_code=400, content={"success": False, "message": f"Stock insuficiente: {prod.id_producto}"})

                    #mandar datos detelle_fcatura
                    sql_detalle = """
                        INSERT INTO detalle_venta_backup (id_factura, id_producto, cantidad, precio_unitario)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql_detalle, (id_factura, prod.id_producto, prod.cantidad, prod.precio_unitario))

               
                self.con.commit()

            return JSONResponse(status_code=200, content={
                "success": True,
                "message": "Factura generada exitosamente",
                "numero_factura": num_factura
            })

        except Exception as e:
            if self.con: self.con.rollback()
            print(f"ERROR CRÍTICO: {str(e)}")
            return JSONResponse(status_code=500, content={"success": False, "message": f"Error interno: {str(e)}"})
        
        finally:
            self.close_connection()

    def obtener_historial_facturas(self, documento: str):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:

                #Valida que exista el usuario
                cursor.execute(
                    "SELECT id_usuario FROM usuario WHERE documento = %s",
                    (documento,)
                )
                usuario = cursor.fetchone()

                if not usuario:
                    return {
                        "success": False,
                        "message": "Usuario no encontrado"
                    }

                sql = """
                SELECT 
                    f.id_factura,
                    f.numero_factura,
                    u.documento AS documento_cliente,
                    u.nombre AS nombre_cliente,
                    f.total,
                    f.estado,
                    f.fecha
                FROM factura f
                INNER JOIN usuario u ON u.id_usuario = f.id_usuario
                WHERE u.documento = %s
                ORDER BY f.fecha DESC
                """

                cursor.execute(sql, (documento,))
                facturas = cursor.fetchall()

                if not facturas:
                    return {
                        "success": False,
                        "message": "El cliente no tiene facturas"
                    }

                return {
                    "success": True,
                    "data": facturas
                }

        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": str(e)
                }
            )

        finally:
            self.close_connection()

    def buscar_por_factura(self, numero_factura: str):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:

                sql = """
                SELECT 
                    f.id_factura,
                    f.numero_factura,
                    u.documento AS documento_cliente,
                    u.nombre AS nombre_cliente,
                    f.total,
                    f.estado,
                    f.fecha
                FROM factura f
                INNER JOIN usuario u ON u.id_usuario = f.id_usuario
                WHERE f.numero_factura = %s
                """

                cursor.execute(sql, (numero_factura,))
                factura = cursor.fetchall()

                if not factura:
                    return {
                        "success": False,
                        "message": "Factura no encontrada"
                    }

                return {
                    "success": True,
                    "data": factura
                }

        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": str(e)
                }
            )
        finally:
            self.close_connection()

    def obtener_detalle_factura(self, id_factura: int):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                               SELECT
                               f.id_factura,
                               f.numero_factura,
                               u.nombre AS cliente,
                               u.documento,
                               f.estado,
                               f.total
                               FROM factura f
                               LEFT JOIN usuario u ON u.id_usuario = f.id_usuario
                               WHERE f.id_factura = %s
                               """, (id_factura,))
                factura = cursor.fetchone()
                
                if not factura:
                    return {"success": False, "message": "Factura no encontrada"}
                
                cursor.execute("""
                               SELECT
                               p.nombre,
                               d.cantidad,
                               d.precio_unitario,
                               (d.cantidad * d.precio_unitario) AS subtotal
                               FROM detalle_venta_backup d
                               INNER JOIN producto p ON p.id_producto = d.id_producto
                               WHERE d.id_factura = %s
                               """, (id_factura,))
                
                productos = cursor.fetchall()
                
                factura["productos"] = productos
                
                return {
                    "success": True,
                    "factura": factura
                    }
                
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            self.close_connection()





   
