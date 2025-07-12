########################################################
# Build stage
########################################################
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    echo 'export PATH="/root/.cargo/bin:$PATH"' >> ~/.bashrc && \
    . ~/.bashrc

# Copy project files
COPY pyproject.toml README.md ./
COPY src ./src/
COPY tests ./tests/
COPY secrets ./secrets/

# Install all dependencies including dev dependencies
RUN . ~/.bashrc && uv pip install --system ".[dev]"

# Run tests
RUN . ~/.bashrc && PYTHONPATH=/app uv run pytest tests/

########################################################
# Production stage
########################################################
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    echo 'export PATH="/root/.cargo/bin:$PATH"' >> ~/.bashrc && \
    . ~/.bashrc

# Copy files from builder stage (this ensures builder stage runs first)
COPY --from=builder /app/pyproject.toml /app/README.md ./
COPY --from=builder /app/src ./src/

# Install only production dependencies
RUN . ~/.bashrc && uv pip install --system .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"] 