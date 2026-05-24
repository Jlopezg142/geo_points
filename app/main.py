from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "host": "geo_db",
    "database": "geopoints",
    "user": "postgres",
    "password": "postgres",
    "port": 5432
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.get("/")
def root():
    return {"message": "API funcionando 🚀"}


# 🔍 OBTENER PUNTOS (CON FILTRO)
@app.get("/puntos")
def get_puntos(categoria: str = None):
    conn = get_connection()
    cur = conn.cursor()

    if categoria:
        cur.execute("""
            SELECT id, nombre, descripcion, categoria,
                   ST_Y(geom::geometry), ST_X(geom::geometry)
            FROM puntos
            WHERE categoria = %s
        """, (categoria,))
    else:
        cur.execute("""
            SELECT id, nombre, descripcion, categoria,
                   ST_Y(geom::geometry), ST_X(geom::geometry)
            FROM puntos
        """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "puntos": [
            {
                "id": r[0],
                "nombre": r[1],
                "descripcion": r[2],
                "categoria": r[3],
                "lat": r[4],
                "lng": r[5]
            } for r in rows
        ]
    }


# ➕ CREAR PUNTO
@app.post("/puntos")
def crear_punto(punto: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO puntos (nombre, descripcion, categoria, geom)
        VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s),4326))
    """, (
        punto["nombre"],
        punto["descripcion"],
        punto["categoria"],
        punto["lng"],
        punto["lat"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"mensaje": "Punto creado"}


# ✏️ ACTUALIZAR
@app.put("/puntos/{id}")
def actualizar_punto(id: int, punto: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE puntos
        SET nombre=%s, descripcion=%s, categoria=%s,
            geom = ST_SetSRID(ST_MakePoint(%s, %s),4326)
        WHERE id=%s
    """, (
        punto["nombre"],
        punto["descripcion"],
        punto["categoria"],
        punto["lng"],
        punto["lat"],
        id
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"mensaje": "Actualizado"}


# ❌ ELIMINAR
@app.delete("/puntos/{id}")
def eliminar_punto(id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM puntos WHERE id=%s", (id,))
    conn.commit()

    cur.close()
    conn.close()

    return {"mensaje": "Eliminado"}
