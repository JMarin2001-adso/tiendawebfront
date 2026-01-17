
import pymysql
from db.db_mysql import get_db_connection
from models.auditoria_model import AuditoriaCreate

class AuditoriaService:

    def __init__(self):
        self.con = get_db_connection()

    def registrar_evento(self, data: AuditoriaCreate):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO auditoria
                    (tabla_afectada, id_registro, accion, descripcion,
                     estado_anterior, estado_nuevo, detalle)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    data.tabla_afectada,
                    data.id_registro,
                    data.accion,
                    data.descripcion,
                    data.estado_anterior,
                    data.estado_nuevo,
                    data.detalle
                ))

            self.con.commit()
            return {"status": "ok", "mensaje": "Evento registrado"}

        except Exception as e:
            return {"status": "error", "detalle": str(e)}


    def listar_por_accion(self, accion):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM auditoria
                    WHERE accion = %s
                    ORDER BY fecha DESC
                """, (accion,))
                return cursor.fetchall()

        except Exception as e:
            return {"status": "error", "detalle": str(e)}
