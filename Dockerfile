FROM python:latest

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY gather_data.py gather_data.p

CMD [ "python", "gather_data.py"]