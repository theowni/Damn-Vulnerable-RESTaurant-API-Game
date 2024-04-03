# Contributing

When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change. 

Please note we have a code of conduct, please follow it in all your interactions with the project.

# Development
This documentation is dedicated for contributors who would like to add new vulnerable features to the project.

## Configuring the project
The project is developed with the following frameworks and technologies:
* [Python 3.8](https://www.python.org/downloads/release/python-380/)
* [Docker](https://www.docker.com/) as a platform for containerisation 
* [FastAPI](https://github.com/tiangolo/fastapi) as easy to learn and fast to code web framework
* [PostgreSQL 15.4](https://www.postgresql.org/) as a database
* [Pytest](https://docs.pytest.org/) for code testing
* [pre-commit](https://pre-commit.com/) for maintaining hooks for code style and tests

Configuring a development environment is a straightforward process assuming that `Python>=3.8`, `pip` and `Docker` are already installed:

1. Install `psycopg2` prerequisites as described in the [official documentation](https://www.psycopg.org/install/). For "*nix" distributions, the following command can be used:
    ```sh
    sudo apt install python3-dev libpq-dev
    ```
    

2. Clone the repository and change directory to the project root:
    ```sh
    git clone https://github.com/theowni/Damn-Vulnerable-RESTaurant-API-Game.git
    cd Damn-Vulnerable-RESTaurant-API-Game
    ```

3. Install Poetry:
    ```sh
    pip3 install poetry
    ```

4. Install project dependencies and spawn shell within the created environment:
    ```sh
    poetry install
    poetry shell
    ```

5. Setup [pre-commit](https://pre-commit.com/):
    ```sh
    pre-commit install
    ```

6. Validate that tests are passing locally:
    ```sh
    pytest .
    ```
7. Develop vulnerable API endpoints by following already existing files structure.

## Running Tests
```sh
docker compose build
docker compose run web pytest .
```


## Generating Alembic Migrations
Changes in database models need to be reflected in migrations via Alembic. Migrations can be created via:
```sh
docker compose build
docker compose run web alembic revision --autogenerate -m 'changes description'
```