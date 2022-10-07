# otus-server

#### Приложение написано в качестве учебного проекта.
Веб-сервер на сокетах частично реализующий протокол HTTP.
Реализован кастомный событийный цикл для асинхронной обработки запросов. Готовность сокетов проверяется стандартной библиотекой select.

### Стек
Для запуска не требуется устанавливать никакие сторонние библиотеки.
- python 3.10


### Запуск
``` python httpd.py ```
После чего можно делать запросы к серверу 
``` http://localhost:port/ ```

### Конфигурация
Приложению можно передать аргументы первоначальной конфигурации. 
```
-r  - корневая директория веб сервера
-p  - порт на котором будет поднят сервер
-w  - число воркеров

python httpd.py -r templates -p 5000 -w 2
```

### Разработка
Для разработки и тестирования потребуется установить зависимости в ваше окружение.
``` 
pip install poetry 
poetry install
```

### Запуск тестов, линтеров
``` 
python httptest.py
flake8
mypy .
```

### Результаты нагрузочного тестирования
Locust

![alt text](https://i.ibb.co/sQVTfrT/2022-10-07-21-15-33.png)

``` 
Server Software:        otus-server
Server Hostname:        127.0.0.1
Server Port:            6002

Document Path:          /
Document Length:        104 bytes

Concurrency Level:      100
Time taken for tests:   34.327 seconds
Complete requests:      20000
Failed requests:        0
Total transferred:      5020000 bytes
HTML transferred:       2080000 bytes
Requests per second:    582.64 [#/sec] (mean)
Time per request:       171.633 [ms] (mean)
Time per request:       1.716 [ms] (mean, across all concurrent requests)
Transfer rate:          142.81 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        1   27 369.4      3    6777
Processing:     0   46  24.2     51     267
Waiting:        0   45  24.3     51     267
Total:          1   73 367.9     59    6781

Percentage of the requests served within a certain time (ms)
  50%     59
  66%     61
  75%     65
  80%     66
  90%     73
  95%     77
  98%     83
  99%     99
 100%   6781 (longest request)

```