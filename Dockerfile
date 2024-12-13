# 1. Use an official Python runtime as a parent image
FROM python:3.10-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set work directory
WORKDIR /app

# 4. Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 6. Copy the models
COPY models/ ./models/

# 7. Copy the application code
COPY app/ ./app/

# 8. Expose the port Flask runs on
EXPOSE 5000

# 9. Set environment variables for Flask
ENV FLASK_APP=app.py

# 10. Define the entry point
CMD ["python", "app/app.py"]
