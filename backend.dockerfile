# Use the official Python image from the Docker Hub with Python 3.12
FROM python:3.12-slim
# Install Poetry
RUN pip install poetry

# Set the working directory in the container
WORKDIR /app


# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*


RUN pip install poetry && poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

# Install dependencies (without creating a virtual environment)
RUN poetry install --no-root --no-interaction --no-ansi

# Copy the FastAPI application code to the working directory
COPY . .

# Install the Python dependencies
RUN pip install ua-parser


ENV PYTHONPATH=/app

#RUN cd app && python backend_pre_start.py

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the port the app runs on
EXPOSE 8002

# Command to run the FastAPI app using uvicorn,
#CMD ["poetry", "run", "uvicorn", "app.main:app","--reload", "--host", "0.0.0.0", "--port", "8002"]

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]


