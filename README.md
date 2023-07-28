# Potato blog
###### (example of RESTful API server)

### 1. Setting up environment via docker-compose

- requirements: Docker is installed
- copy provided `.env.dist` file and fill in / change missing env params -> `cp .env.dist .env`
- build Docker images -> `docker-compose build`
- to start all services (server and database) run -> `docker-compose up`
- to access bash console withing running app container use -> `docker compose exec app bash` or shortcut -> `make bash`
- proceed to section 
> 3. Setting up server

### 2. Setting up environment via venv

- requirements: `
  - Python 3.9 or higher is installed
  - default-libmysqlclient-dev` or similar is installed (required by mysqlclient Python library, see https://pypi.org/project/mysqlclient/)
- copy provided `.env.dist` file and fill in / change missing env params -> `cp .env.dist .env`
- create venv -> `make create-venv`
- to activate venv -> `source .venv` (see `make help` as well)
- to run server (activated venv and working database is required) -> `python manage.py run_local_server`
- proceed to section
> 3. Setting up server

### 3. Setting up server
- run migrations to create required database tables -> `python manage.py migrate`
- copy static files for swagger documentation and admin panel -> `python manage.py collectstatic`
- create admin user to access admin pages -> `python manage.py create_default_admin` (use with  `--help` for details)
- start server (see section 1 and 2):
  - swaggers docs are served at http://localhost:8000/docs/ by default
  - admin panel is accessible via http://localhost:8000/admin/ (see `ADMIN_USERNAME` and `ADMIN_PASSWORD` variables in `.env`)
- in order to send real emails on password reset set up Email Credentials:
  - go to admin panel -> EMAILS -> Email Credentials -> Click "Add" or "ADD EMAIL CREDENTIALS" button
  - dy default those are preconfigured to use Gmail TSL connection (just add username, password and email)
  - in case of other providers make sure to change host / port / extra flags etc.
  - click "SAVE" button

### 4. Running tests
- to run tests via Docker -> `make test` (accepts pytest args via `CMD_ARGS` argument, e.g. `make test CMD_ARGS="posts/tests.py"` see https://docs.pytest.org/en/7.1.x/how-to/usage.html)
- to run tests via venv -> `cd blog && pytest -n auto`

### 5. Packages overview
- `black` - Python linter and code formatter
- `Django` - server framework
- `django-filter` - Django extension to serialize query parameters
- `django-environ` - Django parser for .env files
- `djangorestframework` - RESTful extension for Django
- `django-rest-passwordreset` - reset password APIs for Django-REST
- `djangorestframework-simplejwt` - JWT authentication and related authentication APIs for Django-REST
- `drf-spectacular` - Swagger documentation generator for Django-REST
- `drf-spectacular[sidecar]` - optional Spectacular extension to serve local Swagger static files instead of CDN
- `factory_boy` - factories to create / mock various Python objects during tests
- `gunicorn` - WSGI server for UNIX systems
- `isort` - utility to sort Python imports
- `mysqlclient` - MySQL database adapter
- `pytz` - Python timezone module
- `pip-tools` - PIP utilities
- `pytest-xdist` - allows running pytest on multiple cores
- `pytest-django` - pytest extension for Django-REST
- `python-dotenv` - .env parser
- `whitenoise` - wrapper to serve static files as part of WSGI application

