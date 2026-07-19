FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy and install dependencies
COPY pyproject.toml .
COPY uv.lock* .
RUN uv sync --no-dev

# Copy application
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]