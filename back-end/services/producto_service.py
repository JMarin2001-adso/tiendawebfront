
from fastapi.responses import JSONResponse
from db.db_mysql import get_db_connection
from models.producto_model import ProductoCreate,InventarioSalidaCreate,InventarioEntradaCreate,EntradaStock,ProductoUpdate
import pymysql
import pymysql.cursors
from decimal import Decimal
from datetime import date, datetime


def serializar(valor):
    """Convierte objetos no serializables (Decimal, date/datetime, dicts, lists) a tipos JSON-friendly."""
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    if isinstance(valor, dict):
        return {k: serializar(v) for k, v in valor.items()}
    if isinstance(valor, list):
        return [serializar(v) for v in valor]
    return valor



class ProductoService:
    def __init__(self, con=None):
        self.con = con or get_db_connection()
        if self.con is None:
            raise Exception("No se pudo establecer conexión con la base de datos")

    def close_connection(self):
        if self.con:
            try:
                self.con.close()
            except:
                pass


    def crear_producto(self, producto: ProductoCreate):
        cursor = None  # evitar error 
        try:
            cursor = self.con.cursor()
            sql = """
                INSERT INTO producto 
                (nombre, descripcion, precio, id_categoria, categoria, imagen, estado)
                VALUES (%s, %s, %s, %s, %s, %s,%s)
            """
            valores = (
                producto.nombre,
                producto.descripcion,
                producto.precio,
                producto.id_categoria,
                producto.categoria,
                producto.imagen,
                1
            )
            cursor.execute(sql, valores)
            self.con.commit()
            return {"mensaje": "Producto creado exitosamente"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            if cursor:
                cursor.close()
            self.close_connection()

   
    def listar_productos_sync(self):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = sql = """
                SELECT 
                p.id_producto, p.nombre, p.precio, p.imagen, p.disponible,
                COALESCE(i.stock_actual, 0) AS stock_actual
                FROM producto p
                LEFT JOIN inventario i ON p.id_producto = i.id_producto
                WHERE p.estado = 1
                """
                cursor.execute(sql)
                productos = cursor.fetchall()
                
                print("Productos encontrados:", len(productos))
                
                for p in productos:
                    if p.get("imagen"):
                        if "uploads/" in p["imagen"]:
                            p["imagen"] = f"http://127.0.0.1:8000/{p['imagen']}"
                        else:
                            p["imagen"] = f"http://127.0.0.1:8000/uploads/{p['imagen']}"
                    else:
                            p["imagen"] = "http://127.0.0.1:8000/uploads/default.jpg"

        #Convertir Decimal a float para evitar errores.
            for p in productos:
                if isinstance(p.get("precio"), Decimal):
                   p["precio"] = float(p["precio"])

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Productos obtenidos exitosamente",
                    "data": productos if productos else []
                }
            )
        except Exception as e:
            print("Error en listar_productos_sync:", str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"Error al obtener los productos: {str(e)}",
                    "data": None
                }
            )
        finally:
           self.close_connection()

    
    def listar_entradas_sync(self):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                SELECT 
                    e.id_entrada,
                    e.id_producto,
                    e.nombre_producto,
                    e.precio_adquirido,
                    e.cantidad,
                    e.fecha_ingreso,
                    pr.nombre_proveedor AS proveedor,
                    e.observacion
                FROM inventario_entrada e
                LEFT JOIN proveedor pr ON e.id_proveedor = pr.id_proveedor
                ORDER BY e.fecha_ingreso DESC
            """
                cursor.execute(sql)
                entradas = cursor.fetchall()
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "Entradas obtenidas exitosamente",
                        "data": serializar(entradas) if entradas else []
                        }
                        )
        except Exception as e:
            print("Error en listar_entradas_sync:", str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"Error al obtener las entradas: {str(e)}",
                    "data": None
                    }
                    )
        finally:
            self.close_connection()

    def agregar_entrada_sync(self, data: InventarioEntradaCreate):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                
                cursor.execute(
                    "SELECT id_producto FROM producto WHERE id_producto = %s",
                    (data.id_producto,)
                    )
                producto = cursor.fetchone()
                
                if not producto:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "success": False,
                            "message": f"El producto con ID {data.id_producto} no existe.",
                            "data": None
                            }
                            )
                sql_entrada = """
                INSERT INTO inventario_entrada
                (id_producto, nombre_producto, precio_adquirido, cantidad, fecha_ingreso, id_proveedor, observacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(sql_entrada, (
                    data.id_producto,
                    data.nombre_producto,
                    data.precio_adquirido,
                    data.cantidad,
                    data.fecha_ingreso,
                    data.id_proveedor,
                    data.observacion
                    ))
                
                cursor.execute(
                    "SELECT stock_actual FROM inventario WHERE id_producto = %s",
                    (data.id_producto,)
                    )
                
                inventario = cursor.fetchone()
                
                if inventario:
                    
                    cursor.execute("""
                                   UPDATE inventario
                                   SET stock_actual = stock_actual + %s
                                   WHERE id_producto = %s
                                   """, (data.cantidad, data.id_producto))
                else:
                    cursor.execute("""
                                   INSERT INTO inventario (id_producto, stock_actual, stock_minimo)
                                   VALUES (%s, %s, %s)
                                   """, (data.id_producto, data.cantidad, 5))
                    self.con.commit()
                    
                    return JSONResponse(
                        status_code=201,
                        content={
                            "success": True,
                            "message": "Entrada registrada y stock actualizado correctamente",
                            "data": {
                                "id_producto": data.id_producto,
                                "cantidad_ingresada": data.cantidad
                                }
                                }
                                )
        except Exception as e:
            print("Error en agregar_entrada_sync:", str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"Error al registrar entrada: {str(e)}",
                    "data": None
                    }
                    )
        finally:
            self.close_connection()


    def listar_salidas_sync(self):
        try:
            self.con.ping(reconnect=True)

            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                SELECT 
                    id_salida,
                    id_producto,
                    nombre_producto,
                    cantidad,
                    fecha_salida,
                    observacion,
                    id_usuario
                FROM inventario_salida
                ORDER BY fecha_salida DESC
                """
                cursor.execute(sql)
                salidas = cursor.fetchall()

            return JSONResponse(
                status_code=200,
                content={"success": True, "message": "Salidas obtenidas", "data": salidas}
            )

        except Exception as e:
            print("ERROR SALIDAS:", e)
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": str(e), "data": None}
            )

        finally:
            self.close_connection()

    def agregar_salida_sync(self, data: InventarioSalidaCreate):
        try:
            self.con.ping(reconnect=True)

            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:

                # Valida la cantidad mayor a 0
                if data.cantidad <= 0:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "La cantidad debe ser mayor que 0",
                            "data": None
                        }
                    )

                cursor.execute("SELECT nombre FROM producto WHERE id_producto = %s", (data.id_producto,))
                prod = cursor.fetchone()

                if not prod:
                    return JSONResponse(
                        status_code=404,
                        content={"success": False, "message": "El producto no existe", "data": None}
                    )

                nombre_producto = prod["nombre"]

                cursor.execute("SELECT stock_actual FROM inventario WHERE id_producto = %s", (data.id_producto,))
                inv = cursor.fetchone()

                if not inv:
                    return JSONResponse(
                        status_code=404,
                        content={"success": False, "message": "No existe inventario de este producto", "data": None}
                    )

                stock_actual = inv["stock_actual"]

                # ayuda a verificar que el stock se mayor al minimo (5)
                if stock_actual - data.cantidad < 0:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": f"Stock insuficiente. Disponible: {stock_actual}, solicitado: {data.cantidad}",
                            "data": None
                        }
                    )

                sql = """
                INSERT INTO inventario_salida 
                (id_producto, nombre_producto, cantidad, fecha_salida, observacion, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    data.id_producto,
                    nombre_producto,
                    data.cantidad,
                    data.fecha_salida,
                    data.observacion,
                    data.id_usuario
                ))

                nuevo_stock = stock_actual - data.cantidad

                cursor.execute("""
                    UPDATE inventario SET stock_actual = %s WHERE id_producto = %s
                """, (nuevo_stock, data.id_producto))

                self.con.commit()

                return JSONResponse(
                    status_code=201,
                    content={
                        "success": True,
                        "message": "Salida registrada y stock actualizado",
                        "data": {"stock_restante": nuevo_stock}
                    }
                )

        except Exception as e:
            print("ERROR EN SALIDA:", e)
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": str(e), "data": None}
            )

        finally:
            self.close_connection()
      
    def listar_inventario_sync(self):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                SELECT 
                    p.id_producto,
                    p.nombre,
                    COALESCE(i.stock_actual, 0) AS stock_actual,
                    (
                        SELECT precio_adquirido 
                        FROM inventario_entrada 
                        WHERE id_producto = p.id_producto
                        ORDER BY fecha_ingreso DESC
                        LIMIT 1
                    ) AS precio_adquirido,
                    (
                        SELECT fecha_ingreso 
                        FROM inventario_entrada 
                        WHERE id_producto = p.id_producto
                        ORDER BY fecha_ingreso DESC
                        LIMIT 1
                    ) AS fecha_ingreso,
                    (
                        SELECT pr.nombre_proveedor
                        FROM proveedor pr
                        JOIN inventario_entrada e ON pr.id_proveedor = e.id_proveedor
                        WHERE e.id_producto = p.id_producto
                        ORDER BY e.fecha_ingreso DESC
                        LIMIT 1
                    ) AS proveedor
                FROM producto p
                LEFT JOIN inventario i ON p.id_producto = i.id_producto
                WHERE p.estado = 1
                GROUP BY p.id_producto
                ORDER BY p.id_producto DESC
            """
                
                cursor.execute(sql)
                inventario = cursor.fetchall()
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "Inventario obtenido exitosamente",
                        "data": serializar(inventario)
                        }
                        )
        except Exception as e:
            print("Error en listar_inventario_sync:", str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"Error al obtener inventario: {str(e)}",
                    "data": None
                    }
                    )
        finally:
            self.close_connection()

    def entrada_stock_sync(self, data: EntradaStock):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                               UPDATE inventario
                               SET stock_actual = stock_actual + %s
                               WHERE id_producto = %s
                               """, (data.cantidad, data.id_producto))
                
                cursor.execute("""
                               INSERT INTO inventario_entrada
                               (id_producto, precio_adquirido, cantidad, fecha_ingreso, id_proveedor, observacion)
                               VALUES (%s, %s, %s, %s,%s,%s)
                               """, (
                                   data.id_producto,
                                   data.precio_adquirido,
                                   data.cantidad,
                                   data.fecha_ingreso,
                                   data.id_proveedor,
                                   data.observacion
                                   ))
                self.con.commit()
                return JSONResponse(
                    status_code=200,
                    content={"success": True, "message": "Stock actualizado correctamente"}
                    )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": f"Error al actualizar stock: {str(e)}"}
                )
        finally:
            self.close_connection()

    def sincronizar_inventario_sync(self):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT id_producto, nombre FROM producto")
                productos = cursor.fetchall()
                
                cursor.execute("SELECT id_producto FROM inventario")
                inventario_ids = {row["id_producto"] for row in cursor.fetchall()}
                
                agregados = 0
                
                for p in productos:
                    if p["id_producto"] not in inventario_ids:
                        cursor.execute("""
                                       INSERT INTO inventario (id_producto, stock_actual, stock_minimo)
                                       """, (p["id_producto"], 0, 5))
                        agregados += 1
                        
                        self.con.commit()
                        respuesta = {
                            "success": True,
                            "message": f"Sincronización completa. Productos agregados al inventario: {agregados}",
                            "data": None
                            }
                        print("\n==============================")
                        print("📌 DEBUG → Respuesta enviada:")
                        print(respuesta)
                        print("==============================\n")
                        
                        return respuesta
                    
        except Exception as e:
            error = {
                "success": False,
                "message": f"Error en inventario: {str(e)}",
                "data": None}
            
            print("\n Eror de inventario:")
            print(error)
            print("==============================\n")
            return error

        finally:
            self.close_connection()

    def actualizar_precio_sync(self, data: ProductoUpdate):
        print("DATA RECIBIDA:", data)
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                
                sql = "UPDATE producto SET nombre = %s, precio = %s WHERE id_producto = %s"
                cursor.execute(sql, (data.nombre, data.precio, data.id_producto))
                
                self.con.commit()
                
                if cursor.rowcount > 0:
                    return JSONResponse(
                        status_code=200,
                        content={"success": True, "message": "Producto actualizado en base de datos"}
                        )
                    
                else:
                    return JSONResponse(
                        status_code=404,
                        content={"success": False, "message": "No se encontró el producto"}
                        )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": f"Error en servidor: {str(e)}"}
                )
        finally:
            self.close_connection()


    def actualizar_integral_sync(self, data: ProductoUpdate):
        print("Sincronizando Producto e Inventario:", data)
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_producto = """
                    UPDATE producto 
                    SET nombre = %s, precio = %s, disponible = %s 
                    WHERE id_producto = %s
                """
                cursor.execute(sql_producto, (data.nombre, data.precio, data.disponible, data.id_producto))

                sql_inventario = """
                    UPDATE inventario 
                    SET stock_actual = %s 
                    WHERE id_producto = %s
                """
                cursor.execute(sql_inventario, (data.stock_actual, data.id_producto))

                self.con.commit()

                return JSONResponse(
                    status_code=200,
                    content={"success": True, "message": "Producto e inventario actualizados correctamente"}
                )

        except Exception as e:
            
            if self.con:
                self.con.rollback()
            print(" Error en actualización integral:", str(e))
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": f"Error en servidor: {str(e)}"}
            )
        finally:
            self.close_connection()

    def productos_mayor_rotacion_sync(self, fecha_inicio=None, fecha_fin=None):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                SELECT 
                p.id_producto,
                p.nombre,
                SUM(dv.cantidad) AS total_vendido
                FROM detalle_venta_backup dv
                JOIN producto p ON dv.id_producto = p.id_producto
                WHERE p.estado = 1
                """
                params = []
                
                if fecha_inicio and fecha_fin:
                    sql += " AND DATE(dv.fecha_venta) BETWEEN %s AND %s "
                    params.extend([fecha_inicio, fecha_fin])
                    
                    sql += """
                    GROUP BY p.id_producto
                    ORDER BY total_vendido DESC
                    LIMIT 10
                    """
                    
                cursor.execute(sql, params)
                data = cursor.fetchall()
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "Productos con mayor rotación",
                        "data": serializar(data)
                        }
                        )
                
        except Exception as e:
            print(" Error en listar producto:", e)
            return JSONResponse(
                status_code=500, 
                content={
                    "success": False,
                    "message": str(e),
                    "data": None
                    }
                    )
        finally:
            self.close_connection()


    def productos_bajo_stock_sync(self):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                
                sql = """
                SELECT
                p.id_producto,
                p.nombre,
                i.stock_actual,
                i.stock_minimo
                FROM inventario i
                JOIN producto p ON i.id_producto = p.id_producto
                WHERE p.estado = 1
                AND i.stock_actual <= i.stock_minimo
                ORDER BY i.stock_actual ASC
                """
                
                cursor.execute(sql)
                data = cursor.fetchall()
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "Productos con bajo stock",
                        "data": serializar(data)
                        }
                        )
        except Exception as e:
            print(" Error bajo stock:", e)
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": str(e), "data": None}
                )
        finally:
            self.close_connection()

