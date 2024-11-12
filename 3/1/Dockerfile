FROM python:3.10.14-slim

LABEL maintainer="Dmitriy-U"
LABEL "org.label-schema.vendor"="dmitriyushkalov@gmail.com"
LABEL "org.label-schema.version"="1.0.0"
LABEL "org.label-schema.schema-version"="1.0"
LABEL "org.label-schema.name"="Laboratory 1. Main"
LABEL "org.label-schema.description"="The main module. It contains web interface for distribute data base nodes"
LABEL "org.label-schema.docker.cmd"="docker run -d -p 9090:9090 laboratory-1-main"

WORKDIR /laboratory-1
ADD . /laboratory-1
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "app:app", "--workers", "1", "--host", "0.0.0.0", "--port", "9090", "--use-colors", "--log-level", "debug"]
