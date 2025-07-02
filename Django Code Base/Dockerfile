# Use an official Python runtime as a parent image
FROM --platform=linux/amd64 python:3.11-slim

# Set environment variables
# Prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures Python output is sent straight to the terminal without being buffered
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /when2meet-app

# Install system dependencies if any
# RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

CMD ["gunicorn", "Main.wsgi:application", "--bind", "0.0.0.0:8080"]