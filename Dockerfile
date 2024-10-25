# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application into the container
COPY . .

# Expose the application port (e.g., 5000)
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]  # Change 'app.py' to your main application file if different
