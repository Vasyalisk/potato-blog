VENV_ROOT=./.venv
VENV=${VENV_ROOT}/bin/activate
APP_DIR=./blog

.PHONY: help
help:
	@echo "To activate virtual env run: source ${VENV}"
	@echo ""
	@echo "pip-compile  Pin package versions from requirements.in"
	@echo "lint         Format python files and sort imports"
	@echo ""
	@echo "To deactivate virtual env run: deactivate"

.PHONY: lint
lint:
	@echo "Sorting imports..."
	@source ${VENV};isort ${APP_DIR} --profile black --skip migrations --line-length 120
	@echo "Formatting code..."
	@source ${VENV};black ${APP_DIR} --line-length 120 --extend-exclude "/(|migrations)/"

.PHONY: create-venv
create-venv:
	@python3 -m venv ${VENV_ROOT}
	@source ${VENV};pip install -r ./requirements/requirements.txt

.PHONY: pip-compile
pip-compile:
	@docker-compose exec app pip-compile --allow-unsafe --generate-hashes --output-file=./requirements/requirements.txt ./requirements/requirements.in