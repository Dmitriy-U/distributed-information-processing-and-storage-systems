# Лабораторная работа 3

Централизованное хранение данных

## Запуск хранения данных

```ps
fastapi run .\storage\main.py --host 127.0.0.1 --port 9000
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

### Запись фала

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
