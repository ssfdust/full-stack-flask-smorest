FROM python:latest

ENV FLASK_ENV=production

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python - --preview

RUN export PATH=$PATH:$HOME/.poetry/bin

RUN mkdir Application

# set working directory to /app/
WORKDIR /Application/

# add requirements.txt to the image
ADD pyproject.toml poetry.lock /Application/

RUN poetry config settings.virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

CMD ["sh", "scripts/initapp.sh"]
