# Use Python image as base image
FROM python:3.11.6

# Set working directory in the container
WORKDIR /app

# Copy the contents of the scraper directory to the container's /app directory
COPY . /app

# Install project dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI application
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
