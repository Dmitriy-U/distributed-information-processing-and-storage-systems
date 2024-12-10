# Laboratory 2

## Note

Credential for airflow webserver:

- login: `airflow`
- password: `airflow`

## Commands

### Init airflow

```sh
docker compose up airflow-init -d
```

### Run airflow

```sh
docker compose up -d
```

### Clear project

```sh
docker compose down --volumes --remove-orphans
```
