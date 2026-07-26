release: python manage.py migrate --noinput
web: gunicorn admission_helper.wsgi --bind 0.0.0.0:$PORT --workers ${WEB_CONCURRENCY:-2} --timeout 30 --access-logfile - --error-logfile -
