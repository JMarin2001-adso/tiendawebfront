import pymysql
from db.db_mysql import get_db_connection
from models.pago_model import PagoClienteCreate


class PagoService:

    def __init__(self):
        self.con = get_db_connection()

  
    def registrar_pago_sync(self, data: PagoClienteCreate):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:

                # Verificar si el pedido existe
                cursor.execute("""
                    SELECT estado 
                    FROM pedido_cliente 
                    WHERE id_pedido = %s
                """, (data.id_pedido,))
                pedido = cursor.fetchone()

                if not pedido:
                    return {"status": "error", "mensaje": "El pedido no existe"}

                # Registrar el pago
                cursor.execute("""
                    INSERT INTO pago_cliente (id_pedido, metodo_pago, estado_pago, monto, fecha)
                    VALUES (%s, %s, %s, %s, NOW())
                """, (data.id_pedido, data.metodo_pago, data.estado_pago, data.monto))

                # cambio de estado-al realiar pago
                if data.estado_pago == "pagado":
                    cursor.execute("""
                        UPDATE pedido_cliente
                        SET estado = 'aprobado'
                        WHERE id_pedido = %s
                    """, (data.id_pedido,))
                    
                    #pago exitoso
                    cursor.execute("""
                        INSERT INTO auditoria (id_pedido, accion, descripcion, fecha)
                        VALUES (%s, 'pago_aprobado', %s, NOW())
                    """, (data.id_pedido,
                          data.descripcion or "Pago aprobado y pedido actualizado")
                    )

                #fallo al realizar pago
                else:
                    cursor.execute("""
                        INSERT INTO auditoria (id_pedido, accion, descripcion, fecha)
                        VALUES (%s, 'pago_fallido', %s, NOW())
                    """, (data.id_pedido,
                          data.descripcion or "Intento de pago fallido")
                    )

                self.con.commit()

                return {
                    "status": "ok",
                    "mensaje": "Pago procesado correctamente"
                }

        except Exception as e:
            return {"status": "error", "detalle": str(e)}


 
    def listar_notificaciones_sync(self):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:

                cursor.execute("""
                    SELECT 
                        p.id_pago,
                        p.id_pedido,
                        p.estado_pago,
                        p.metodo_pago,
                        p.fecha
                    FROM pago_cliente p
                    ORDER BY p.fecha DESC
                    LIMIT 20
                """)

                return cursor.fetchall()

        except Exception as e:
            return {"status": "error", "detalle": str(e)}
