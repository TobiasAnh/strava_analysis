# Use an official Python base image
FROM python:3.10.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONPATH=/app

# Set working directory in the container
WORKDIR /app

# Install system dependencies and Poetry
RUN apt-get update && \
    apt-get install -y curl build-essential libpq-dev git && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy only Poetry files first to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Install Python dependencies
RUN poetry install --no-root

# Copy the rest of the application code
COPY . .

# Set the default command to run your application
CMD ["python", "app/main.py"]
