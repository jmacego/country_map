# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Expose port 8000 to the outside world
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run Gunicorn when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
