release: python manage.py migrate
web: gunicorn --log-level info --bind 0.0.0.0:8000 --log-file - baking_softwaredev.wsgi:application
