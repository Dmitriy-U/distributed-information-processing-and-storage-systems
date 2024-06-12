FROM python:3.10.14-slim
LABEL maintainer="Dmitriy-U"
WORKDIR /laboratory-3
ADD . /laboratory-3
RUN pip install -r requirements.txt
CMD uvicorn storage.main:app --host 0.0.0.0 --port 9000
