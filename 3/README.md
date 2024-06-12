# Лабораторная работа 3

Централизованное хранение данных

## Запуск хранения данных в *docker* контейнере

### Создание образа

Запустите: `docker buildx build --tag <image_name> .`, где:

- *image_name* - наименование образа

#### Windows

```ps
docker buildx build --tag laboratory-3 .
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
docker run --name laboratory-3-9000 -p 9000:9000 -d laboratory-3
```

## Команды

### Получение файла

```ps
python.exe .\app.py -C read -F .\demo.txt
```

или

```ps
python.exe .\app.py -C read -F .\demo.txt -O .\demo1.txt
```

### Запись файла

```ps
python.exe .\app.py -C write -F .\demo.txt -I .\demo.txt
```

### Удаление файла

```ps
python.exe .\app.py -C delete -F .\demo.txt
```

### Изменение блока файла

```ps
python.exe .\app.py -C changeblock -F .\demo.txt -B 64:23 -BD 01234567890123456789012345678901
```
