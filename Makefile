all:
	pip install poetry invoke colorlog toml --user
	inv app.dependencies.install
