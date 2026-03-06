FROM python:3.11-slim

WORKDIR /app

# Install system essentials
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install the dependencies first (Caching layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire dev folder into the container
COPY . .
RUN chmod -R +r /app

# Expose the Hypervisor port
EXPOSE 8000

# Ignite the BoneAmanita engine
CMD ["uvicorn", "bone_server:app", "--host", "0.0.0.0", "--port", "8000"]