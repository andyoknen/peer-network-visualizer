FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./src/ .
ADD ./config ./config

CMD ["python", "main.py"]