# Лабораторная работа 4. Хранение данных

Децентрализованное хранение данных

## Запуск в *docker* контейнере

### Создание образа

Запустите: `docker buildx build --tag <image_name> .`, где:

- *image_name* - наименование образа

#### Windows

```ps
docker buildx build --tag laboratory-4 .
```

#### linux

```shell
docker build --tag laboratory-3 .
```

### Создание и запуск контейнера

Запустите: `docker run --name <container_name> -p <port>:9000 -d <image_name>`, где:

- *container_name* - наименование контейнера,
- *port* - номер порта на котором будет работать хранилище
- *image_name* - наименование образа

```shell
docker run --name laboratory-4-9000 -p 9000:9000 -d laboratory-4
```
