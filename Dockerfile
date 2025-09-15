# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY app.py .
COPY templates/ /app/templates/
COPY static/ /app/static/

# Expose the port Flask runs on
EXPOSE 5000

CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--debug"]

# Command to run the application
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--worker-class", "gunicorn.workers.gthread.ThreadWorker", "app:app"]