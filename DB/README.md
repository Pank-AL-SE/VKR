Инструкция по запуску:

    Создайте папку для проекта и перейдите в неё:
    bash

mkdir docker-postgres && cd docker-postgres

Создайте файл docker-compose.yml и (опционально) init.sql

Запустите контейнер:
bash

docker-compose up -d

Проверьте работу:
bash

docker ps  # должен показать работающий контейнер

Подключитесь к БД:
bash

docker exec -it my_postgres psql -U myuser -d mydatabase