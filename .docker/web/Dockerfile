FROM python:3.11-slim-bullseye AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.11-slim-bullseye AS development

WORKDIR /app

COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV FLASK_RUN_PORT=5000
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000

CMD ["flask", "run"]


FROM python:3.11-slim-bullseye AS gunicorn
RUN pip install --no-cache-dir gunicorn


FROM python:3.11-slim-bullseye AS production

WORKDIR /app

COPY --from=builder /usr/local/bin /usr/local/bin

COPY --from=gunicorn /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

COPY . .

ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:5000 --workers=3"

EXPOSE 5000

CMD ["gunicorn", "app:app"]