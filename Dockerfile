FROM python:3.10-slim

LABEL authors="Felixhghg"

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10126

CMD ["python", "main.py"]