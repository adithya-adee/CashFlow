FROM python:3.12

WORKDIR /backend

# Set Poetry to create virtualenvs in the project directory
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# Add the virtual environment's bin directory to the PATH
ENV PATH="/backend/.venv/bin:$PATH"

# Copy only the necessary Poetry files
COPY ./pyproject.toml /backend/pyproject.toml
COPY ./poetry.lock /backend/poetry.lock

# Install poetry
RUN pip install --no-cache-dir poetry

# Debug: Show Poetry environment info before installing dependencies
RUN poetry env info

# Copy the rest of the application code first
COPY . /backend/

# Install project dependencies into the .venv (after copying all code)
RUN poetry install --no-root --no-interaction --no-ansi && \
    /backend/.venv/bin/python -c "import uvicorn; print('uvicorn imported successfully')"

# Debug: List contents of the WORKDIR to see if .venv was created
RUN ls -la /backend

# Create data directory
RUN mkdir -p /backend/data

# Expose the port the application will run on
EXPOSE 8000 

# Command to run the FastAPI application directly using the python interpreter from the venv
CMD ["/backend/.venv/bin/python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]