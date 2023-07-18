VENV=.venv/bin/activate
APP_DIR=./blog

.PHONY: help
help:
	@echo "To activate virtual env run: source ${VENV}"
	@echo ""
	@echo "pip-compile  Pin package versions from requirements.in"
	@echo "pip-install  Install requirements from requirements.txt"
	@echo "lint         Format python files and sort imports"
	@echo "run-server   Run dev server"
	@echo ""
	@echo "To deactivate virtual env run: deactivate"

.PHONY: lint
lint:
	@echo "Sorting imports..."
	@source ${VENV};isort ${APP_DIR} --profile black --skip migrations --line-length 120
	@echo "Formatting code..."
	@source ${VENV};black ${APP_DIR} --line-length 120 --extend-exclude "/(|migrations)/"

.PHONY: pip-compile
pip-compile:
	@source ${VENV};pip-compile --allow-unsafe --generate-hashes --output-file=./requirements/requirements.txt ./requirements/requirements.in

.PHONY: pip-install
pip-install:
	@source ${VENV};pip install -r ./requirements/requirements.txt

.PHONY: run-server
run-server:
	@source ${VENV};docker-compose up -d;python ./manage.py run_local_server