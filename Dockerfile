# The base image is python 3.12 slim
FROM python:3.12-slim

# Create the working directory
WORKDIR /app

# Copy all the code to the Docker image
COPY . /app

# Expose the application port
EXPOSE 3306

# Run the python server, which will return 
# Toronto current time as JSON for GET request
CMD [ "python", "server.py" ]