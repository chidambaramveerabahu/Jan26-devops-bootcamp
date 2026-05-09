FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update and install dependencies
RUN apt-get update && apt-get install -y \
    clamav \
    clamav-daemon \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Update ClamAV virus database
RUN freshclam

# Set working directory
WORKDIR /app

# Copy requirements file
COPY scanner/requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the application
COPY scanner .

# Run the script
CMD ["python3", "main.py"]