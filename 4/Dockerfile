FROM python:3.10.14-slim
LABEL maintainer="Dmitriy-U"
WORKDIR /laboratory-4
ADD . /laboratory-4
RUN pip install -r requirements.txt
CMD uvicorn app:app --host 0.0.0.0 --port 9090 --use-colors --log-level debug
