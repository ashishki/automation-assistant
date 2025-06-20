FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install Poetry for Python dependency management
RUN pip install poetry

# Copy project metadata and README so Poetry can read them
COPY pyproject.toml poetry.lock* README.md ./

# Copy application source code and tests before installing
COPY automation_assistant ./automation_assistant
COPY tests ./tests

# Configure Poetry to install into the system environment and install dependencies + project
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Default command to run the assistant
CMD ["python", "-m", "automation_assistant.main"]
