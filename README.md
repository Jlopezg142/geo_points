# 🌍 GeoPoints

Aplicación web geoespacial para la gestión de puntos de interés en un mapa interactivo.

---

## 📌 Descripción

GeoPoints permite visualizar, crear, editar y eliminar ubicaciones geográficas en tiempo real utilizando un mapa interactivo.

---

## 🎯 Objetivo

Desarrollar un sistema que permita gestionar datos geográficos de forma eficiente mediante tecnologías modernas.

---

## 🛠️ Tecnologías utilizadas

* 🐍 Python (FastAPI)
* 🐘 PostgreSQL + PostGIS
* 🌐 HTML, JavaScript
* 🗺️ Leaflet
* 🐳 Docker & Docker Compose
* ⚙️ Nginx

---

## 🏗️ Arquitectura

Usuario → Nginx → FastAPI → PostgreSQL/PostGIS

---

## 🚀 Instalación y ejecución

```bash
cd geo-points
docker compose up -d --build
```

---

## 🌐 Acceso

```
http://localhost:8080
```

---

## 🔌 API

| Método | Endpoint     | Descripción    |
| ------ | ------------ | -------------- |
| GET    | /puntos      | Obtener puntos |
| POST   | /puntos      | Crear punto    |
| PUT    | /puntos/{id} | Actualizar     |
| DELETE | /puntos/{id} | Eliminar       |

---

## 🗂️ Estructura del proyecto

```
geo-points/
├── app/
├── db/
├── frontend/
├── nginx/
├── docker-compose.yml
└── README.md
```

---

## 🗺️ Funcionalidades

* Visualización en mapa
* Creación de puntos
* Edición de puntos
* Eliminación de puntos
* Filtrado por categoría

---


## 👨‍💻 Autor

* Alex Flores
 

---

## 📄 Licencia

Este proyecto es de uso académico.
