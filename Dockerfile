# Usar una imagen base ligera de Python 3.10
FROM python:3.10-slim

# Evitar que Python escriba archivos .pyc en el disco
ENV PYTHONDONTWRITEBYTECODE=1
# Evitar que Python almacene en búfer stdout y stderr
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema operativo (opcional, por si hiciera falta para compilar)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requisitos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del repositorio
COPY . .

# Comando de entrada
CMD ["python", "-X", "utf8", "main.py"]
