FROM python:3

RUN mkdir /app

RUN python -m venv /app/venv \
    && /app/venv/bin/pip install -U pip
COPY requirements.txt deploy/requirements-deploy.txt /tmp/
RUN /app/venv/bin/pip install -r /tmp/requirements.txt \
    && /app/venv/bin/pip install -r /tmp/requirements-deploy.txt

COPY recipes /app/recipes_website/recipes
COPY users /app/recipes_website/users
COPY baking_softwaredev /app/recipes_website/baking_softwaredev
COPY deploy/wsgi.py deploy/settings_prod.py /app/recipes_website/

ENV DJANGO_SETTINGS_MODULE=settings_prod

CMD [ \
    "/app/venv/bin/gunicorn", \
    "--log-level", "info",\
    "--chdir", "/app/recipes_website", \
    "--bind", "0.0.0.0:8000", \
    "wsgi:application" \
    ]