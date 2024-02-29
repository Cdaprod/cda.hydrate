# Use a slim version of Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application files to the container
COPY . .

# Install the dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Inform Docker that the container listens on port 8080 (if your application has a web interface)
EXPOSE 8080

# Define the command to run the application
CMD ["python", "main.py"]