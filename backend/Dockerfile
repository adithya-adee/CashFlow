FROM python:3.12

WORKDIR /fastapi-backend

COPY ./poetry.lock /fastapi-backend/poetry.lock
COPY ./pyproject.toml /fastapi-backend/pyproject.toml

# Install poetry and uvicorn before installing project dependencies
RUN pip install --no-cache-dir poetry uvicorn

# Install project dependencies
RUN poetry install --no-root 

COPY . /fastapi-backend/

# Expose the port the application will run on
EXPOSE 69

# Command to run the FastAPI application using uvicorn
# Assuming your FastAPI app instance is named 'app' in main.py
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "69"]

# Command to run the FastAPI application using fastapi
# CMD ["fastapi", "run", "main.py"]