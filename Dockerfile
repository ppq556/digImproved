FROM python:alpine

RUN pip install httplib2 future certifi

WORKDIR /app
COPY . .

ENTRYPOINT ["python", "digImproved.py"]
