# Dockerfile
FROM python:3.11-slim

# Set work directory inside the container
WORKDIR /SolveMath

# Copy all project files to container
COPY . /SolveMath

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Start the FastAPI app with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
