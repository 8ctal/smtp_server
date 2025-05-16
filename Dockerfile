FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create templates directory
RUN mkdir -p templates

# Copy application files
COPY . .

# Make sure the templates directory exists and has the right permissions
RUN chmod -R 755 templates

CMD ["python", "app.py"] 