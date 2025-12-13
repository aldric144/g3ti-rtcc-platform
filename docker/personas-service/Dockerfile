FROM python:3.11-slim

LABEL maintainer="G3TI RTCC Platform"
LABEL description="AI Personas Service - Apex AI Officers"
LABEL version="1.0.0"
LABEL phase="34"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY docker/personas-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app/personas /app/backend/app/personas
COPY backend/app/api/personas /app/backend/app/api/personas
COPY backend/app/websockets/personas_ws.py /app/backend/app/websockets/personas_ws.py

COPY docker/personas-service/main.py /app/main.py
COPY docker/personas-service/config.py /app/config.py

RUN useradd -m -u 1000 personas && \
    chown -R personas:personas /app
USER personas

EXPOSE 8034

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8034/health || exit 1

CMD ["python", "main.py"]
