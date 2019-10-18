all:
	pip install poetry invoke colorlog --user
	inv app.dependencies.install
