# Python image using Alpine as base
FROM python:3.11-alpine

# Install build dependencies and PostgreSQL client libraries
RUN apk add --no-cache build-base postgresql-dev

# Set working directory
WORKDIR /app

# Install Python dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Start the bot when the container launches
CMD ["python", "main.py"]
