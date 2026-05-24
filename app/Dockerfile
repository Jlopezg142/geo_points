FROM python:3.11

WORKDIR /workspace

# 1. Copiar e instalar las dependencias de Python
COPY app/requirements.txt .
RUN pip install -r requirements.txt

# 2. Copiar tanto la carpeta app como frontend al contenedor
COPY app/ ./app
COPY frontend/ ./frontend

EXPOSE 8000

# 3. Ejecutar el servidor apuntando correctamente a la carpeta app
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
