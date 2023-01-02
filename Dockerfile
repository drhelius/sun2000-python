FROM python:latest

WORKDIR /app

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY gather_data.py gather_data.py

CMD [ "python", "gather_data.py"]