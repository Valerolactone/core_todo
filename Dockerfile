FROM python:3.11-slim

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN apt-get update && apt-get install -y curl && apt-get clean
RUN poetry install --without dev

COPY . /app/

ENTRYPOINT ["poetry", "run", "python", "-m", "manage.py"]