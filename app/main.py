from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import psycopg2
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de base de datos dinámica para Render o Local
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    if DATABASE_URL:
        # En producción (Render) se conecta usando la URL interna generada por la plataforma
        return psycopg2.connect(DATABASE_URL)
    else:
        # En desarrollo local (Docker local) usa la configuración clásica previa
        return psycopg2.connect(
            host="geo_db",
            database="geopoints",
            user="postgres",
            password="postgres",
            port=5432
        )

# Configurar la ruta absoluta de la carpeta frontend subiendo un nivel desde 'app/'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Si el contenedor aplana las carpetas en la raíz, usamos la ruta alternativa por seguridad
if not os.path.exists(FRONTEND_DIR):
    FRONTEND_DIR = "./frontend"

# Servir archivos estáticos si la carpeta existe
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# 🌐 MOSTRAR EL MAPA EN LA RAÍZ
@app.get("/", response_class=HTMLResponse)
def root():
    # Intento 1: Buscar index.html usando la ruta calculada dinámicamente
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as file:
            return file.read()
            
    # Intento 2: Buscar index.html en la raíz directa del contenedor
    fallback_path = "./frontend/index.html"
    if os.path.exists(fallback_path):
        with open(fallback_path, "r", encoding="utf-8") as file:
            return file.read()
            
    # Intento 3: Buscar index.html un nivel arriba de forma literal
    literal_path = "../frontend/index.html"
    if os.path.exists(literal_path):
        with open(literal_path, "r", encoding="utf-8") as file:
            return file.read()
            
    return "<h1>Error: No se encontró el archivo index.html en la carpeta frontend</h1>"


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
