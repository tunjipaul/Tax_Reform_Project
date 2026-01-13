# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements first to leverage Docker cache
# COPY requirements.txt .
COPY backend/requirements.txt backend_requirements.txt
COPY ai_engine/requirements.txt ai_engine_requirements.txt

# Install dependencies
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r backend_requirements.txt
RUN pip install --no-cache-dir -r ai_engine_requirements.txt

# Copy the entire project into the container
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Run the application
# We use the module syntax (-m) to ensure imports work correctly
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]