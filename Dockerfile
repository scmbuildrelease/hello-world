# Use Python base image
FROM python:3.10-slim

# Install gcc for compiling C program
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY hello.py hello.c ./

# Compile the C program
RUN gcc -o hello hello.c

# Make both executables accessible
ENV PATH="/app:${PATH}"

# Default command runs both hello world programs
CMD echo "=== Python Hello World ===" && \
    python hello.py && \
    echo "\n=== C Hello World ===" && \
    ./hello

