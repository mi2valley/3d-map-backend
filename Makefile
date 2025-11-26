.PHONY: run install update build test

PROGRAM_NAME := "py312"

prepare:
	cp .env.example .env

run:
	poetry run uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload

install:
	poetry install
	poetry run pre-commit install

update:
	poetry update
	poetry run pre-commit autoupdate

build:
	poetry build

test:
	poetry run pytest ./tests -p no:warnings

docker-build:
	docker build . -t ${PROGRAM_NAME}

docker-build-prod:
	docker build . -t ${PROGRAM_NAME}-prod --platform=linux/amd64

docker-run:
	docker run -it -p 8080:8080 ${PROGRAM_NAME}
