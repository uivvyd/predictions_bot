FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3.11 python3.11-distutils && apt-get install -y python3-pip                                                                             >
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "/data/app.py"]
