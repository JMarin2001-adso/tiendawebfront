import pymysql
from db.db_mysql import get_db_connection
from models.pedido_model import PedidoClienteCreate
from models.auditoria_model import AuditoriaCreate
from services.auditoria_service import AuditoriaService

from services.envio_service import EnvioService




class PedidoService:


    def __init__(self):
        self.con = get_db_connection()

    def crear_pedido_sync(self, data: PedidoClienteCreate):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                
                total = 0
                for p in data.productos:
                    total += p.cantidad * p.precio_unitario
                    
                    print("TOTAL FINAL CALCULADO:", total)
                    
                    cursor.execute("""
                                   INSERT INTO pedido_cliente (id_usuario, total, estado)
                                   VALUES (%s, %s, 'pendiente')
                                   """, (data.id_usuario, total))
                    
                    id_pedido = cursor.lastrowid
                    
                    for p in data.productos:
                        cursor.execute("""
                                       INSERT INTO detalle_pedido_cliente
                                       (id_pedido, id_producto, cantidad, precio_unitario)
                                       VALUES (%s, %s, %s, %s)
                                       """, (id_pedido, p.id_producto, p.cantidad, p.precio_unitario))
                        cursor.execute("""
                                       UPDATE inventario
                                       SET stock_actual = stock_actual - %s
                                       WHERE id_producto = %s
                                       """, (p.cantidad, p.id_producto))
                        self.con.commit()
                        
                        return {
                            "status": "ok",
                            "mensaje": "Pedido creado correctamente",
                            "id_pedido": id_pedido,
                            "estado": "pendiente"
                            }
        except Exception as e:
            self.con.rollback()
            return {"status": "error", "detalle": str(e)}



    def listar_pendientes_sync(self):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                
                cursor.execute("""
                               SELECT *
                               FROM pedido_cliente
                               WHERE estado = 'pendiente'
                               ORDER BY fecha DESC
                               """)
                pedidos = cursor.fetchall()
                
                for p in pedidos:
                    cursor.execute("""
                                   SELECT id_producto, cantidad, precio_unitario
                                   FROM detalle_pedido_cliente
                                   WHERE id_pedido = %s
                                   """, (p["id_pedido"],))
                    p["items"] = cursor.fetchall()
                    
                    return pedidos
                
        except Exception as e:
            return {"status": "error", "detalle": str(e)}
        


    def actualizar_estado_sync(self, id_pedido, estado, motivo=None):
        try:
            
            estados_validos = [
                 "pendiente",
                 "pagado",
                 "en_camino",
                 "entregado",
                 "rechazado"
                 ]
            
            if estado not in estados_validos:
                return {"status": "error", "detalle": "Estado no permitido"}
            
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                
                cursor.execute("""
                               SELECT id_usuario
                               FROM pedido_cliente
                               WHERE id_pedido = %s
                               """, (id_pedido,))
                pedido = cursor.fetchone()
                
                if not pedido:
                    return {"status": "error", "detalle": "Pedido no encontrado"}
                
                id_usuario = pedido["id_usuario"]
                
                cursor.execute("""
                               UPDATE pedido_cliente
                               SET estado = %s
                               WHERE id_pedido = %s
                               """, (estado, id_pedido))
                
                descripcion = (
                    f"Pedido rechazado. Motivo: {motivo}"
                    if estado == "rechazado" and motivo
                    else f"Se cambió el estado del pedido a {estado}"
                    )
                
                cursor.execute("""
                               INSERT INTO auditoria (tabla_afectada, id_registro, accion, descripcion)
                               VALUES ('pedido_cliente', %s, 'UPDATE', %s)
                               """, (id_pedido, descripcion))
                
                cursor.execute("""
                               INSERT INTO notificacion
                               (id_usuario, tipo, mensaje, id_pedido, fecha)
                               VALUES (%s, %s, %s, %s, NOW())
                               """, (
                                   id_usuario,
                                   "pedido_estado",
                                   descripcion,
                                   id_pedido))
                
                self.con.commit()
                
                return {
                    "status": "ok",
                    "mensaje": "Estado actualizado correctamente"
                    }
        except Exception as e:
            self.con.rollback()
            return {
                "status": "error",
                "detalle": str(e)
                }


    def obtener_detalle_pedido(self, id_pedido: int):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                
                cursor.execute("""SELECT p.id_pedido, p.total, p.estado, p.fecha,
                               u.nombre AS nombre_cliente,
                               u.direccion,
                               u.telefono,u.correo
                               FROM pedido_cliente p
                               INNER JOIN usuario u ON u.id_usuario = p.id_usuario
                               WHERE p.id_pedido = %s
                               """, (id_pedido,))
                pedido = cursor.fetchone()
                
                if not pedido:
                    return {"status": "error", "msg": "Pedido no encontrado"}
                
                cursor.execute("""
                               SELECT 
                               dp.id_producto,
                               prod.nombre AS nombre_producto,
                               dp.cantidad,
                               dp.precio_unitario
                               FROM detalle_pedido_cliente dp
                               INNER JOIN producto prod ON prod.id_producto = dp.id_producto
                               WHERE dp.id_pedido = %s
                               """, (id_pedido,))

                productos = cursor.fetchall()
                
                return {
                    "id_pedido": pedido["id_pedido"],
                    "nombre_cliente": pedido["nombre_cliente"],
                    "estado": pedido["estado"],
                    "fecha": pedido["fecha"],
                    "total": pedido["total"],
                    "productos": productos,
                    "direccion": pedido["direccion"],
                    "telefono": pedido["telefono"],
                    "correo": pedido["correo"],
                    }
        except Exception as e:
            return {"status": "error", "detalle": str(e)}

    def despachar_pedido_sync(self, id_pedido: int):
        cursor = None
        try:
            self.con.ping(reconnect=True)
            cursor = self.con.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                           SELECT estado 
                           FROM pedido_cliente 
                           WHERE id_pedido = %s
                           """, (id_pedido,))
            pedido = cursor.fetchone()
            if not pedido:
                return {"status": "error", "detalle": "Pedido no encontrado"}
            if pedido["estado"] != "pagado":
                return {
                    "status": "error",
                    "detalle": f"No se puede despachar un pedido en estado: {pedido['estado']}"
                    }
            cursor.execute("""
                           SELECT id_envio 
                           FROM envio 
                           WHERE id_pedido = %s
                           """, (id_pedido,))
            if cursor.fetchone():
                return {
                    "status": "error",
                    "detalle": "Este pedido ya cuenta con un registro de envío"
                    }
            tracking = f"ENV-{id_pedido:06d}"
            
            cursor.execute("""
                           INSERT INTO envio (id_pedido, tracking, estado, fecha_creacion)
                           VALUES (%s, %s, 'Pendiente', NOW())
                           """, (id_pedido, tracking))
            self.con.commit()
            return {
                "status": "ok",
                "mensaje": "Pedido despachado. Envío creado en estado Pendiente.",
                "tracking": tracking
                }
        except Exception as e:
            if self.con:
                self.con.rollback()
                return {"status": "error", "detalle": str(e)}
        finally:
            if cursor:
                cursor.close()

        
