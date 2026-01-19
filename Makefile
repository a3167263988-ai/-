.PHONY: up down logs lint format test migrate

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

lint:
	ruff check .

format:
	black .

test:
	pytest -q

migrate:
	docker compose exec api alembic upgrade head
