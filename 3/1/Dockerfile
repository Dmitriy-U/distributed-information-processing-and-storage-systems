FROM python:3.10.14-slim
LABEL maintainer="Dmitriy-U"
WORKDIR /laboratory-1
ADD . /laboratory-1
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9090", "--use-colors", "--log-level", "debug"]
