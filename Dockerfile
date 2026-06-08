# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Pin the requirements directly in the build sequence
RUN echo "fastapi==0.110.0\nuvicorn==0.28.0\npydantic==2.6.4\ntrafilatura==1.8.0" > requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY main.py .

# Expose the API port
EXPOSE 8000

# Run the Uvicorn deployment engine
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]