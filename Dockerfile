FROM python:3.11-slim

# Install system packages required by WeasyPrint
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libxml2 \
    libxslt1.1 \
    libssl-dev \
    fonts-liberation \
    fonts-dejavu-core \
    fontconfig \
    shared-mime-info && \
    apt-get clean

# Set working directory
WORKDIR /app

# Copy only requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a non-root user (Render runs as root by default, this is optional security)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Use uvicorn directly with dynamic port support
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
