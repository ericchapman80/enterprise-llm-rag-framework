# Use Python 3.10 as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY src/backend/requirements.txt .

# Copy the Zscaler certificate into the Docker image 
COPY zscaler.crt /usr/local/share/ca-certificates/zscaler.crt

# Establish trust between the container and the Zscaler CA
RUN apt-get update && apt-get install -y ca-certificates && \
    cat /usr/local/share/ca-certificates/zscaler.crt >> /etc/ssl/certs/ca-certificates.crt && \
    update-ca-certificates

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/backend /app/src/backend
COPY config /app/config

# Set environment variables
ENV PYTHONPATH=/app
ENV CONFIG_PATH=/app/config/config.yaml
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run the application with correct module path
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
