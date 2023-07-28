VENV_ROOT=./.venv
VENV=${VENV_ROOT}/bin/activate
APP_DIR=.

.PHONY: help
help:
	@echo "To activate virtual env run: source ${VENV}"
	@echo ""
	@echo "lint         Format python files and sort imports"
	@echo "create-venv  Create new virtual environment and install Python packages"
	@echo "pip-compile  Pin package versions from requirements.in"
	@echo "bash  		Start bash console inside Docker"
	@echo "test  		Run tests inside dedicated Docker container, accepts pytest args as CMD_ARGS"
	@echo ""
	@echo "To deactivate virtual env run: deactivate"

.PHONY: lint
lint:
	@echo "Sorting imports..."
	@docker-compose run --rm app isort ${APP_DIR} --profile black --skip migrations --line-length 120
	@echo "Sorting requirements.."
	@docker-compose run --rm app python /scripts/sort_requirements.py /requirements/requirements.in
	@echo "Formatting code..."
	@docker-compose run --rm app black ${APP_DIR} --line-length 120 --extend-exclude "/(|migrations)/"

.PHONY: create-venv
create-venv:
	@python3 -m venv ${VENV_ROOT}
	@source ${VENV};pip install -r ./requirements/requirements.txt

.PHONY: pip-compile
pip-compile:
	@docker-compose run --rm app pip-compile --allow-unsafe --generate-hashes --output-file=/requirements/requirements.txt /requirements/requirements.in

.PHONY: bash
bash:
	@docker-compose exec app bash

.PHONY: test
test:
	@docker-compose down
	@docker-compose -f docker-compose.yml -f docker-compose.test.override.yml run --rm app pytest ${CMD_ARGS} -n auto