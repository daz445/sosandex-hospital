.PHONY: install run test clean help

help: ## Показать все команды
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости в venv
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

run: ## Запустить сервер на http://localhost:8000
	.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Запустить тесты
	.venv/bin/python -m pytest tests/ -v

clean: ## Удалить venv, кэш, базу
	rm -rf .venv .pytest_cache __pycache__ app/__pycache__ \
		app/models/__pycache__ app/routers/__pycache__ \
		tests/__pycache__ hospital.db
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
