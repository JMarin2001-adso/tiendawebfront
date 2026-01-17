import pymysql
from db.db_mysql import get_db_connection

class EnvioService:
    def __init__(self):
        self.con = get_db_connection()

    def close(self):
        if self.con:
            self.con.close()

    def listar_envios_sync(self):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                    SELECT e.id_envio, e.tracking, e.estado, e.fecha_creacion,
                           p.id_pedido, u.nombre AS cliente
                    FROM envio e
                    INNER JOIN pedido_cliente p ON p.id_pedido = e.id_pedido
                    INNER JOIN usuario u ON u.id_usuario = p.id_usuario
                    ORDER BY e.id_envio DESC
                """)
                return cursor.fetchall()
        finally:
            self.close()

    #Listar por estado
    def listar_envios_estado_sync(self, estado: str):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM envio
                    WHERE estado = %s
                    ORDER BY id_envio DESC
                """, (estado,))
                return cursor.fetchall()
        finally:
            self.close()

    def obtener_envio_por_pedido(self, id_pedido: int):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                    SELECT *
                    FROM envio
                    WHERE id_pedido = %s
                """, (id_pedido,))
                envio = cursor.fetchone()

                if not envio:
                    return {"status": "error", "detalle": "Este pedido no tiene envío"}

                return envio
        finally:
            self.close()



    def actualizar_estado_envio_sync(self, id_envio: int, nuevo_estado: str):
        cursor = None
        try:
            estados_validos = ["Pendiente", "En tránsito", "Entregado"]

            if nuevo_estado not in estados_validos:
                return {
                    "status": "error",
                    "detalle": "Estado de envío no permitido"
                }

            self.con.ping(reconnect=True)
            cursor = self.con.cursor(pymysql.cursors.DictCursor)

            # Obtiene envío y pedido 
            cursor.execute("""
                SELECT id_pedido, estado
                FROM envio
                WHERE id_envio = %s
            """, (id_envio,))
            envio = cursor.fetchone()

            if not envio:
                return {"status": "error", "detalle": "Envío no encontrado"}

            cursor.execute("""
                UPDATE envio
                SET estado = %s
                WHERE id_envio = %s
            """, (nuevo_estado, id_envio))

            if nuevo_estado == "Entregado":
                cursor.execute("""
                    UPDATE pedido_cliente
                    SET estado = 'entregado'
                    WHERE id_pedido = %s
                """, (envio["id_pedido"],))

            self.con.commit()

            return {
                "status": "ok",
                "mensaje": f"Estado del envío actualizado a {nuevo_estado}"
            }

        except Exception as e:
            self.con.rollback()
            print("ERROR ACTUALIZAR ENVÍO:", e)
            return {"status": "error", "detalle": str(e)}

        finally:
           self.close

    def marcar_en_transito_sync(self, id_envio: int):
        cursor = None
        try:
            self.con.ping(reconnect=True)
            cursor = self.con.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                           SELECT e.id_pedido, p.id_usuario, e.estado
                           FROM envio e
                           JOIN pedido_cliente p ON p.id_pedido = e.id_pedido
                           WHERE e.id_envio = %s
                           """, (id_envio,))
            envio = cursor.fetchone()
            if not envio:
                return {"status": "error", "detalle": "Envío no encontrado"}
            if envio["estado"] != "Pendiente":
                return {
                    "status": "error",
                    "detalle": f"No se puede pasar a tránsito desde {envio['estado']}"
                    }
            cursor.execute("""
                           UPDATE envio
                           SET estado = 'En tránsito'
                           WHERE id_envio = %s
                           """, (id_envio,))
            cursor.execute("""
                           UPDATE pedido_cliente
                           SET estado = 'en_camino'
                           WHERE id_pedido = %s
                           """, (envio["id_pedido"],))
            cursor.execute("""
                           INSERT INTO notificacion_cliente (id_usuario, titulo, mensaje, tipo)
                           VALUES (%s, %s, %s, %s)
                           """, (
                               envio["id_usuario"],
                               "Pedido en camino",
                               f"Tu pedido #{envio['id_pedido']} ya fue despachado y va en camino ",
                               "envio"
                               ))
            self.con.commit()
            return {
                "status": "ok",
                "mensaje": "Envío marcado en tránsito y notificación creada"
                }
        except Exception as e:
            if self.con:
                self.con.rollback()
                return {"status": "error", "detalle": str(e)}
        finally:
            if cursor:
                cursor.close()


    def confirmar_entrega_sync(self, id_envio: int):
        cursor = None
        try:
            self.con.ping(reconnect=True)
            cursor = self.con.cursor(pymysql.cursors.DictCursor)
            
            cursor.execute("""
                           SELECT id_pedido, estado
                           FROM envio
                           WHERE id_envio = %s
                           """, (id_envio,))
            envio = cursor.fetchone()
            
            if not envio:
                return {"status": "error", "detalle": "Envío no encontrado"}
            
            if envio["estado"] != "En tránsito":
                return {
                    "status": "error",
                    "detalle": f"No se puede entregar desde estado {envio['estado']}"
                    }
            cursor.execute("""
                           UPDATE envio
                           SET estado = 'Entregado'
                           WHERE id_envio = %s
                           """, (id_envio,))
            cursor.execute("""
                           UPDATE pedido_cliente
                           SET estado = 'entregado'
                           WHERE id_pedido = %s
                           """, (envio["id_pedido"],))
            
            self.con.commit()
            
            return {"status": "ok", "mensaje": "Pedido entregado correctamente"}
        except Exception as e:
            self.con.rollback()
            return {"status": "error", "detalle": str(e)}
        
        finally:
            if cursor:
                cursor.close()
    def obtener_notificaciones_usuario(self, id_usuario: int):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                               SELECT id_notificacion, titulo, mensaje, leida, fecha
                               FROM notificacion_cliente
                               WHERE id_usuario = %s
                               ORDER BY fecha DESC
                               """, (id_usuario,))
                return cursor.fetchall()
        finally:
            self.close()

