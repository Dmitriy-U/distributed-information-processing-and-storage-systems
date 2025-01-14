# Laboratory 2

## Note

Credential for airflow webserver:

- login: `airflow`
- password: `airflow`

## Commands

### Run airflow

```sh
docker compose up -d --build
```

### Clear project

```sh
docker compose down --volumes --remove-orphans
```

## Connection

Airflow console > Admin > Connections > Add a new record

### Default config

- Connection Id: cassandra_default
- Connection Type: Cassandra
- Host: host.docker.internal
- Port: 9042
- Login: cassandra
- Password: password
