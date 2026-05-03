FROM python:3.13.3-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

# install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# now copy full project (IMPORTANT)
COPY . .

ENV PYTHONUNBUFFERED=1

RUN python manage.py collectstatic --noinput

CMD python manage.py migrate && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT