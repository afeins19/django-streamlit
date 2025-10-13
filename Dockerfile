FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/ /app/
COPY app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt gunicorn whitenoise dj-database-url

ENV PYTHONUNBUFFERED=1 \
    STATIC_ROOT=/staticfiles

CMD sh -c "python manage.py migrate --noinput && \
           python manage.py collectstatic --noinput && \
           gunicorn demo.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120"

