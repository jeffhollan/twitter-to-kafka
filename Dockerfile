FROM python:3.6

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
CMD ["python", "twitter-to-kafka.py"]