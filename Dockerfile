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

# Copy everything from local to the container
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000
# Start the FastAPI app with Uvicorn
# Use 'bash -c' so the ${PORT} environment variable is properly expanded by the shell
# Bind to 0.0.0.0 so the container exposes the port to Render
CMD bash -c 'exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info'
