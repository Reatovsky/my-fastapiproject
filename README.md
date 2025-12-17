# Добрый день!

В данном файле изложена пошаговая инструкция по развёртыванию данного проекта.
Также вашему вниманию предлагаются примеры запросов с тестированием основного функционала, а именно:
+ ### Запись
+ ### Чтение
+ ### Сохранение

Ознакомиться с образами вы можете в docker hub: https://hub.docker.com/repositories/reat18

## Этап 1. Развёртывание
Пропустим шаг с загрузкой проекта на вашу машину и перейдём сразу к процессу.
Все нижеперечисленные операции рекомендую производить под root, посколько именно под ним я и работал. :grin:
### Шаг 1 - Сборка образов
Необходимо перейти в папки сервисов (cd <папка_сервива>/), после чего прописать команды:
+ docker build -t todo-service .
+ docker build -t shorturl-service .
Для каждого сервиса начнётся процесс сборки. Выглядить он будет примерно так:
<img width="890" height="400" alt="image" src="https://github.com/user-attachments/assets/32d150e1-faba-4e9b-97aa-8ede6b4e23f6" />

Удостовериться в корректной сборке можно посредству команды:
+ docker images | grep todo-service && docker images | grep shorturl-service

В ответы вы должны увидеть следующее:

<img width="890" height="70" alt="image" src="https://github.com/user-attachments/assets/204c405b-374a-4b86-af90-534224ac7137" />

### Шаг 2 - Создание томов
Для корректной работы механизма сохранения данных, необходимо создать тома todo_data и shorturl_data:
+ docker volume create todo_data
+ docker volume create shorturl_data
<img width="890" height="93" alt="image" src="https://github.com/user-attachments/assets/aa27cb07-6acc-4372-9187-11425f3cc44b" />

Далее, чтобы удостовериться в корректном создании томов, можно воспользоваться командой:
+ docker volume ls | grep todo_data && docker volume ls | grep shorturl_data
<img width="890" height="72" alt="image" src="https://github.com/user-attachments/assets/5883d08f-7473-4c68-93e0-5011d4759c68" />

Если вывод показал два тома, значит, всё корректно и можно приступать к следующему шагу.
## Шаг 3 - Запуск контейнеров
Для запуска контейнеров потребуются команды:
+ docker run -d --name todo_container -p 8000:80 -v todo_data:/app/data todo-service
+ docker run -d --name shorturl_container -p 8001:80 -v shorturl_data:/app/data shorturl-service

Корректная отработка команды выведит хэш-значение контейнера:

<img width="890" height="134" alt="image" src="https://github.com/user-attachments/assets/7dc79eb6-e2de-4cc6-aa39-4a91a7c115ad" />

Удостовериться в запуске контейнеров можно через **docker ps**. Если увидете 2 контейнера, значит, сервисы запущены и можно приступать к тестированию! :trophy::trophy::trophy:

<img width="890" height="94" alt="image" src="https://github.com/user-attachments/assets/7d5535cc-4242-4e64-be62-f5794a26d152" />

## Этап 2. Тестирование
### Шаг 1 - Создание/чтение задач в todo-service
Заведём задачи через команды:
+ curl -X POST "http://localhost:8000/items" -H "Content-Type: application/json" -d '{"title": "Купить продукты", "description": "Молоко, хлеб, яйца, сыр", "completed": false}'
+ curl -X POST "http://localhost:8000/items" -H "Content-Type: application/json" -d '{"title": "Записаться к врачу", "completed": false}'
<img width="890" height="182" alt="image" src="https://github.com/user-attachments/assets/a0679e77-e2a4-4fd6-aa0b-6711e9f5dd6c" />
<img width="890" height="132" alt="image" src="https://github.com/user-attachments/assets/3478d288-66cf-483e-8203-836174bac3eb" />

Ознакомиться с задачами можно через (Настоятельно рекомендую установить jq (apt-get install jq), чтобы вывести всё в читаемом формате):
+ curl "http://localhost:8000/items" | jq .
<img width="890" height="535" alt="image" src="https://github.com/user-attachments/assets/2456536f-1d7c-4d69-bdea-60ebad1315f1" />

Задачи можно посмотреть по их id:
+ curl "http://localhost:8000/items/<id_задачи>" | jq .
<img width="890" height="220" alt="image" src="https://github.com/user-attachments/assets/0c965f8b-6673-47a7-8016-3640e6b44e93" />

Обновление статуса происходит через:
+ curl -X PUT "http://localhost:8000/items/<id_задачи>" -H "Content-Type: application/json" -d '{"completed": true}'
<img width="890" height="286" alt="image" src="https://github.com/user-attachments/assets/4dc11741-ed90-400b-af05-89c7f6d27a97" />

Удалим задачу через команду:
+ curl "http://localhost:8001/" | jq .
<img width="890" height="402" alt="image" src="https://github.com/user-attachments/assets/85020b4e-820e-4245-974e-2afd51443ad1" />

### Шаг 2 - Создание/чтение задач в searchurl-service
Создадим несколько новых сокращённых ссылок:
+ curl -X POST "http://localhost:8001/shorten" -H "Content-Type: application/json" -d '{"url": "https://yandex.ru"}' | jq .
+ curl -X POST "http://localhost:8001/shorten" -H "Content-Type: application/json" -d '{"url": "https://gmail.com"}' | jq .
<img width="890" height="398" alt="image" src="https://github.com/user-attachments/assets/04aa7fcf-a677-44d2-af39-880440179ccf" />

Выведим список всех ссылок:
+ curl "http://localhost:8001/" | jq .
<img width="890" height="642" alt="image" src="https://github.com/user-attachments/assets/2dda1245-f689-4eae-bf7d-d793055c28c0" />

Работоспособность ссылок можно проверить в браузере.

Проверим переадресацию на полную ссылку:
+ curl -X GET -v "http://localhost:8001/Dgmhmd" 2>&1
<img width="890" height="422" alt="image" src="https://github.com/user-attachments/assets/3225cfab-302a-4485-aa86-bb0c89c8b73b" />

Возвратим json информацию с полным URL:
+ curl "http://localhost:8001/stats/Dgmhmd" | jq .
<img width="890" height="179" alt="image" src="https://github.com/user-attachments/assets/b98d1a78-db11-4118-b1fc-74449393079b" />


### Шаг 3 - Сохранение данных в сервисах
Для проверки нужно перезагрузить контейнеры. Для этого остановим их:
+ docker stop todo_container shorturl_container
<img width="890" height="73" alt="image" src="https://github.com/user-attachments/assets/1b5e8452-cabc-4af3-bc08-f430659f89ed" />

Проверим состояние контейнеров:
+ docker ps
<img width="890" height="47" alt="image" src="https://github.com/user-attachments/assets/28936a81-caa0-4787-8580-0689fed7f267" />

Теперь запустим контейнеры:
+ docker start todo_container shorturl_container
<img width="890" height="76" alt="image" src="https://github.com/user-attachments/assets/7242911c-5c96-44ba-8208-d48efbeb738b" />

И вновь проверим их состояние:
+ docker ps
<img width="890" height="115" alt="image" src="https://github.com/user-attachments/assets/4fe79844-f1d5-48be-ba22-cff55094e1a0" />

Соответственно, проверим список задач:
+ curl "http://localhost:8000/items" | jq .
<img width="890" height="402" alt="image" src="https://github.com/user-attachments/assets/f0cbe17c-12a7-4002-b3c5-472ddb730c1c" />

А также проверим список коротких ссылок:
+ curl "http://localhost:8001/" | jq .
<img width="890" height="641" alt="image" src="https://github.com/user-attachments/assets/c117ba5b-3d3c-4106-aaf6-4f29fdadae23" />

Всё сохранилось, а значит функционал работает корректно.
