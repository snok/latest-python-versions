FROM python:3.10.0rc1-alpine

RUN pip install requests packaging

COPY main.py /main.py

ENTRYPOINT ["python", "/main.py"]
