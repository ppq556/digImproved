FROM python:alpine

RUN pip install httplib2

WORKDIR /app
COPY . .

ENTRYPOINT ["python", "digImproved.py"]
