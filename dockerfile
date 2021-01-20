from python:3

WORKDIR /home/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./cmd_mqtt.py"]