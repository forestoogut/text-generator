FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask openai

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
