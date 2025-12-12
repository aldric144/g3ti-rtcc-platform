FROM python:3.11-slim

LABEL maintainer="G3TI RTCC-UIP Team"
LABEL description="AI Sentinel Supervisor - System-Wide Oversight & Ethical Governance"
LABEL version="33.0"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY config.py .

ENV PYTHONUNBUFFERED=1
ENV SENTINEL_MODE=production
ENV AUTO_CORRECTION_ENABLED=true
ENV ETHICS_GUARD_ENABLED=true
ENV MAX_AUTONOMY_LEVEL=2
ENV ALERT_THRESHOLD=medium
ENV LOG_LEVEL=INFO

EXPOSE 8033

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8033/health || exit 1

CMD ["python", "main.py"]
