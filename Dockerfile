#FROM ubuntu:22.04
FROM python:3.12

# Установка необходимых Python-зависимостей
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

COPY . /radicale-endpoints
#COPY backend/ /backend
WORKDIR /radicale-endpoints

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3005"]