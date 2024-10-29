# Use an official Python image from the Docker Hub
FROM python:3.9-slim

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