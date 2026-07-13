FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src/ src/
COPY README.md ./

RUN pip install --no-cache-dir -e .

EXPOSE 8000

ENV IKUAI_URL=http://192.168.9.1
ENV IKUAI_USERNAME=admin
ENV IKUAI_PASSWORD=""

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "ikuai_mcp.server", "--transport", "http", "--port", "8000"]
