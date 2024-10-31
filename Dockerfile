# Start with an official Python image as the base
FROM python:3.10.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.5.1 \
    # Ensures Poetry creates a virtual environment inside the container
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # Avoids sending telemetry data in Docker builds
    POETRY_NO_INTERACTION=1

# Install system dependencies required for Poetry and building Python packages
RUN apt-get update && apt-get install -y curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory inside the container
WORKDIR /app

# Copy Poetry files first to leverage Docker layer caching
COPY pyproject.toml poetry.lock ./

# Install dependencies (without installing the project itself)
RUN poetry install --no-root --no-dev

# Copy the rest of the application code
COPY . .

# If your main application file is called main.py, this is how you run it
# Otherwise, adjust the entry point or command accordingly
CMD ["poetry", "run", "python", "main.py"]

# docker build -t my-python-app . # builds the docker image 
# docker images # lists the image 
# docker run -it --rm --network="host" my-python-app # runs the image  (according to CMD)
# With the setup above, the "--network" flag forces the app to use the host network. 
# Consequently, the app finds the postgresql database on "localhost". Thus, it requires the postgres
# application to be installed and configured beforehand. 
# However, postgres itself can run in a separate docker image. This image can be used in parallel to the
# python docker image while both connect via a docker network.

# CHATGPT suggestion below

# A more isolated and reproducible approach is to run PostgreSQL in its own Docker container and connect it to your application’s container via a Docker network. Here’s how to set it up:

# Create a Docker network:

# bash

# docker network create my_network

# Run a PostgreSQL container attached to this network:

# bash

# docker run -d --name postgres-container --network my_network \
#     -e POSTGRES_USER=your_user \
#     -e POSTGRES_PASSWORD=your_password \
#     -e POSTGRES_DB=your_db_name \
#     postgres:13

# Modify your application container to use this network and connect to the PostgreSQL container by its container name:

# bash

# docker run -it --rm --network my_network my-python-app

# Update your app’s connection settings to point to postgres-container instead of localhost:

# python

# conn = psycopg2.connect(
# host="postgres-container",
# port="5432",
# database="your_db_name",
# user="your_user",
# password="your_password"
# )

# This method makes the setup portable and containerized entirely within Docker, and it works across all systems.
