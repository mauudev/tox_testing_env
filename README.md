# FastAPI + SQLAlchemy + Asyncio + Tox

A basic API rest built on FastAPI and SQLAlchemy + asyncio extension to check compatibilities by switching beetween Python versions.
Uses `tox` and `tox-docker` to create environments with different Python versions and run the unit tests.

## Installation

Install dependencies using `poetry`

```bash
poetry shell
poetry install
```

## Usage

You can start the application manually.
Deploy Postgres by using the packed `docker-compose.yaml` file inside `infra` folder.
Export the `ENV` environment variable with `local` value.

Then start the server by:

```bash
poetry run python src/api/main.py
```

Then go to http://localhost:8000/docs

## Running unit tests

Export `ENV` env var with `test` value and run the unit tests by:

```bash
poetry run pytest -vv
```

### Usin tox

Export `ENV` env var with `test` value and run:

```bash
tox
# or
tox run -e test -- -v
```
