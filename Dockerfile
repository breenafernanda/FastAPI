# Use an official Hypercorn base image
FROM tiangolo/hypercorn:python3.8

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Hypercorn will run on
EXPOSE 8000

# Command to run the application using Hypercorn
CMD ["hypercorn", "main:app", "--bind", "0.0.0.0:8000", "--workers", "4"]
