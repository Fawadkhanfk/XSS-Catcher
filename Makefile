SHELL := /usr/bin/env bash
POSTGRES_PASSWORD := $(shell cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)\n
CLIENT_DIR=client

install:
	@python3 -m pip install pipenv -U
	@pipenv install --dev
	@pipenv run pre-commit install
	@npm install --prefix $(CLIENT_DIR)

lint:
	@pipenv run black --line-length=160 server
	@pipenv run isort --profile black server
	@npm run --prefix $(CLIENT_DIR) lint

test:
	@pipenv run pytest server/tests

test-coverage-report:
	@pipenv run pytest -v --cov=endpoints --cov-report html:cov_html server/tests

run-web-app:
	@npm --prefix client run serve

run-backend-server: lint
	@cd server/api && pipenv run uvicorn main:app --reload

generate-secrets:
ifeq ($(wildcard ./.db_password),)
	@echo $(POSTGRES_PASSWORD) > .db_password
else
	@echo "[-] Database password are already set"
endif

deploy: generate-secrets
	@docker-compose build
	@docker-compose up -d

update:
	@docker-compose build
	@docker-compose up -d

start:
	@docker-compose up -d

stop:
	@docker-compose down
