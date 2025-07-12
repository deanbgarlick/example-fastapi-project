This project was created with Python 3.11.5

Run unit tests with `uv run pytest tests/`

Run tests in the docker compose dev environment for a fresh build with... `docker-compose -f docker-compose-dev.yaml run --build --rm api sh -c ". ~/.bashrc && uv run pytest tests"`
