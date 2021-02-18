FROM python:3.8-slim

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY db db
COPY routers routers
COPY app.py app.py
COPY schemas.py schemas.py

EXPOSE 8000

CMD ["uvicorn", "app:app"]
