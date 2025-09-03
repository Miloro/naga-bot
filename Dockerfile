FROM python:3.11-slim

WORKDIR /app

COPY requirements .
RUN pip install --no-cache-dir -r requirements

CMD ["python", "bot/bot.py"]
