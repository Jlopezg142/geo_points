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
        return psycopg2.connect(DATABASE_URL)
    else:
        return psycopg2.connect(
            host="geo_db",
            database="geopoints",
            user="postgres",
            password="postgres",
            port=5432
        )

# --- CONFIGURACIÓN AUTOMÁTICA DE LA BASE DE DATOS AL INICIAR ---
@app.on_event("startup")
def setup_database():
    print("🔄 Verificando y configurando base de datos en la nube...")
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # 1. Activar PostGIS
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        
        # 2. Crear la tabla si no existe
        cur.execute("""
            CREATE TABLE IF NOT EXISTS puntos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100),
                descripcion TEXT,
                categoria VARCHAR(50),
                geom GEOGRAPHY(Point,4326)
            );
        """)
        
        # 3. Si la tabla está vacía, insertar los puntos por defecto
        cur.execute("SELECT COUNT(*) FROM puntos;")
        count = cur.fetchone()[0]
        
        if count == 0:
            print("📌 La tabla está vacía. Insertando puntos iniciales...")
            cur.execute("""
                INSERT INTO puntos (nombre, descripcion, categoria, geom) VALUES
                ('Agencia Zona 12', 'Ferreteria', 'Punto de Venta', ST_SetSRID(ST_MakePoint(-90.5459,14.5847),4326)),
                ('Agencia Retalhuleu', 'Ferreteria', 'Punto de Venta', ST_SetSRID(ST_MakePoint(-91.6714,14.5412),4326)),
                ('Agencia San Juan', 'Materiales de Construccion', 'Punto de Venta', ST_SetSRID(ST_MakePoint(-90.6435,14.7298),4326)), 
                ('Agencia Villa Hermosa', 'Materiales de Construccion', 'Punto de Venta', ST_SetSRID(ST_MakePoint(-90.5531,14.5274),4326)), 
                ('Cementos Progreso', 'Ferreteria', 'Proveedor', ST_SetSRID(ST_MakePoint(-90.5224,14.5769),4326)), 
                ('Aceros de Guatemala', 'Materiales de Construccion', 'Proveedor', ST_SetSRID(ST_MakePoint(-90.1753,14.8198),4326)), 
                ('Oficinas Administrativas', 'RRHH', 'Servicio', ST_SetSRID(ST_MakePoint(-90.4848,14.4685),4326));
            """)
            conn.commit()
            print("✅ ¡Puntos iniciales guardados con éxito!")
        else:
            print(f"📊 La base de datos ya contiene {count} puntos. No se requiere inserción.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(catch_error := f"❌ Error configurando la base de datos: {e}")


# Configurar la ruta absoluta de la carpeta frontend subiendo un nivel desde 'app/'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

if not os.path.exists(FRONTEND_DIR):
    FRONTEND_DIR = "/workspace/frontend"

# Servir archivos estáticos si la carpeta existe
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# 🌐 MOSTRAR EL MAPA EN LA RAÍZ
@app.get("/", response_class=HTMLResponse)
def root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as file:
            return file.read()
    return f"<h1>Error: No se encontró el archivo index.html en la ruta: {FRONTEND_DIR}</h1>"


# 🔍 OBTENER PUNTOS (CON FILTRO /API)
@app.get("/api/puntos")
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


# ➕ CREAR PUNTO (/API)
@app.post("/api/puntos")
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


# ✏️ ACTUALIZAR (/API)
@app.put("/api/puntos/{id}")
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


# ❌ ELIMINAR (/API)
@app.delete("/api/puntos/{id}")
def eliminar_punto(id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM puntos WHERE id=%s", (id,))
    conn.commit()

    cur.close()
    conn.close()

    return {"mensaje": "Eliminado"}
