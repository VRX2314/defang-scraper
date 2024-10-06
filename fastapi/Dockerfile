# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Install required C++11 libraries and ca-certificates, xvfb for x-server
RUN apt-get update -qq \
      && apt-get install -y \
      build-essential \
      python3-dev \
      ca-certificates \
      xvfb \
      && apt-get clean \
      && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install && playwright install-deps

# Set the display environment variable
ENV DISPLAY=:99

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run main when the container launches, using xvfb-run
CMD ["sh", "-c", "Xvfb :99 -screen 0 1920x1080x24 & DISPLAY=:99 uvicorn main:app --host 0.0.0.0 --port 8000"]