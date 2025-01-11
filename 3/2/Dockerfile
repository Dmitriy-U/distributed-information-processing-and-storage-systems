FROM apache/airflow:2.10.4

LABEL maintainer="Dmitriy-U"
LABEL "org.label-schema.vendor"="dmitriyushkalov@gmail.com"
LABEL "org.label-schema.version"="1.0.0"
LABEL "org.label-schema.schema-version"="1.0"
LABEL "org.label-schema.name"="Laboratory 2. Airflow"

USER airflow
COPY requirements.txt /requirements.txt
USER airflow
RUN pip install --no-cache-dir -r /requirements.txt
