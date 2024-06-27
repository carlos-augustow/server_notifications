FROM python:3.11.9-bookworm

WORKDIR /app

COPY . .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt --verbose

EXPOSE 4000