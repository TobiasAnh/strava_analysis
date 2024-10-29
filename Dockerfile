# Use an official Python image from the Docker Hub
FROM python:3.10.12-slim

# Set a working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Specify the command to run your app (replace `app.py` with your entrypoint script)
CMD ["python", "main.py"]


# docker build -t my-python-app . # builds the docker image 
# docker images # lists the image 
# docker run -it --rm my-python-app # runs the image (according to CMD)
# docker run -it --rm --network="host" my-python-app 



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
