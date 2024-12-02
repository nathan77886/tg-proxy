FROM python:3.12

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./app /app/app
 
COPY main.py /app/main.py
WORKDIR /app

CMD ["python", "/app/main.py"]