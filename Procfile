release: env PYTHONPATH=/mnt DJANGO_SETTINGS_MODULE=settings_prod python manage.py migrate 
web: env PYTHONPATH=/mnt DJANGO_SETTINGS_MODULE=settings_prod gunicorn --log-level info --log-file - baking_softwaredev.wsgi:application
