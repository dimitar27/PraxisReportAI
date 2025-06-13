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

# Copy everything into the container
COPY . /app

# Make sure script is executable AFTER it's copied
RUN chmod +x /app/start.sh

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

# Start the app
CMD ["/app/start.sh"]
