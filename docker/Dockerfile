FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-deps -r requirements.txt

COPY . .

CMD ["python", "-m", "src/main.py"]