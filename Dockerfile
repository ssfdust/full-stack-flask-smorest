FROM python:latest

ENV FLASK_ENV=production

RUN pip install poetry invoke

RUN mkdir Application

# set working directory to /app/
WORKDIR /Application/

# add requirements.txt to the image
ADD pyproject.toml /Application/

RUN poetry config settings.virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

CMD ["sh" "scripts/initapp.sh"]
