# Use an official Python runtime as a parent image
FROM python:3.12-slim
# Set the working directory in the container
WORKDIR /app
# Install system dependencies and curl for Poetry installation
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
# Upgrade pip before installing Poetry
RUN pip install --upgrade pip
# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
# Disable Poetry's virtual environment to install dependencies globally
RUN poetry config virtualenvs.create false
# Copy the pyproject.toml and poetry.lock files first (for dependency caching)
COPY pyproject.toml poetry.lock* /app/
# Install dependencies using Poetry
RUN poetry install --no-root
# Copy the rest of the application code
COPY src/ /app/src/
# :small_blue_diamond: Copy the Streamlit config file from the repository to the container
COPY .streamlit/config.toml /root/.streamlit/config.toml
# Expose the necessary port (if using Streamlit)
EXPOSE 8501
# :small_blue_diamond: Set environment variable to ensure Streamlit loads the correct config
ENV STREAMLIT_CONFIG_FILE="/root/.streamlit/config.toml"
# Ensure correct execution inside the container
CMD ["poetry", "run", "streamlit", "run", "src/main.py", "--global.configFile=/root/.streamlit/config.toml"]