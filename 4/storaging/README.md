# Лабораторная работа 4. Хранение данных

Децентрализованное хранение данных

---

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
docker build --tag laboratory-4 .
```

### Создание и запуск контейнера

Запустите: `docker run --name <container_name> -p <port>:9000 -d <image_name>`, где:

- *container_name* - наименование контейнера,
- *port* - номер порта на котором будет работать хранилище
- *image_name* - наименование образа

```shell
docker run --name laboratory-4-9000 -p 9000:9000 -d laboratory-4
```

---

## Протокол синхронизации нод

При появлении в сети новой ноды, она отправляет широковещательный пакет данных для синхронизации

| Наименование     | Значение          |
|------------------|-------------------|
| Сетевой протокол | `UDP`             |
| Адрес            | `255.255.255.255` |
| Порт             | `9000`            |

**Полезная нагрузка**

```json
{
  "key": "LABORATORY_4",
  "ip": "192.168.0.0"
}
```

---

## Протокол хранения данных

| Наименование     | Значение          |
|------------------|-------------------|
| Сетевой протокол | `TCP`             |
| Порт             | `9001`            |

### Обновление списка нод

| Наименование                  | Значение           |
|-------------------------------|--------------------|
| Путь                          | `/nodes`           |
| Метод                         | `PUT`              |
| Тип контента (*contentType*)  | `application/json` |

**Полезная нагрузка**

```json
{
  "ipList": [
    "192.168.0.0",
    "192.168.0.1",
    "192.168.0.2"
  ]
}
```

### Получение данных

| Наименование                  | Значение                   |
|-------------------------------|----------------------------|
| Путь                          | `/keys/<hash>`             |
| Метод                         | `GET`                      |
| Тип контента (*contentType*)  | `application/octet-stream` |

**Ответ**

- 200 Получено. Данные: *bytes*
- 404 Данных нет

### Сохранение данных

| Наименование                 | Значение                   |
|------------------------------|----------------------------|
| Путь                         | `/keys/<hash>`             |
| Метод                        | `POST`                     |
| Тип контента (*contentType*) | `application/octet-stream` |
| Полезная нагрузка            | *bytes*                    |

**Ответ**

- 201 Сохранено

### Удаление данных

| Наименование                 | Значение                   |
|------------------------------|----------------------------|
| Путь                         | `/keys/<hash>`             |
| Метод                        | `DELETE`                   |
| Тип контента (*contentType*) | `application/octet-stream` |

**Ответ**

- 200 Удалено