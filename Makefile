.PHONY: dev build deploy clean-deploy lint format

dev:
	PYTHONPATH=src fastapi dev src/main.py --port 9001

build:
	uvx --from workers-py pywrangler build

deploy:
	uvx --from workers-py pywrangler deploy

clean-deploy:
	rm -rf dist .wrangler
	$(MAKE) build
	$(MAKE) deploy

lint:
	/home/meralialy/.local/bin/ruff check src/

format:
	/home/meralialy/.local/bin/ruff format src/
	/home/meralialy/.local/bin/ruff check --fix src/


