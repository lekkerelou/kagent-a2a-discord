FROM python:3.12-slim
LABEL authors="LekkereLou"

WORKDIR /app
COPY . .

RUN pip install --upgrade pip
RUN pip install .

CMD ["python", "main.py"]
