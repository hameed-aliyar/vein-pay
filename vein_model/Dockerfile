FROM python:3.13.3-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir torch==2.6.0+cpu torchvision==0.21.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD gunicorn vein_service:app --bind 0.0.0.0:$PORT