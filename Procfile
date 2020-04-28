release: python manage.py migrate
web: PYTHONPATH=/mnt DJANGO_SETTINGS_MODULE=settings_prod gunicorn --log-level info --bind 0.0.0.0:8000 --log-file - baking_softwaredev.wsgi:application
