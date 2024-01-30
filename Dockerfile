# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /mnt
WORKDIR /mnt

# Copy the current directory contents into the container at /mnt
COPY . .
ENV PYTHONPATH="/mnt"

RUN mkdir /mnt/download

# Set read, write, and execute permissions for the entire /mnt directory
RUN chmod -R 777 /mnt

# Install wget and other dependencies
RUN apt-get update && \
    apt-get install -y ca-certificates wget && \
    apt-get install -y libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Update pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run main.py when the container launches
CMD ["gunicorn", "-w", "1", "--threads", "5", "-b", "0.0.0.0:5000", "app:app"]
