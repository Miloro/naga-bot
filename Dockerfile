FROM python:3.11-slim

WORKDIR /app

COPY requirements .
RUN pip install --no-cache-dir -r requirements

# Montaremos el código con volumes, no copiamos nada más
CMD ["python", "bot/bot.py"]
