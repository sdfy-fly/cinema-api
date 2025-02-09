## Запуск тестов
### Локальный запуск в docker-compose
```shell
cd tests/functional
docker-compose up --build
```

## Запуск приложения
### Локальный запуск for macos
```shell
brew install poetry
poetry install
poetry shell
export PYTHONPATH=/PATH_TO_PROJECT_DIR/:$PYTHONPATH
python3 etl/pipeline.py
uvicorn src.main:app --reload
```
### Локальный запуск в docker-compose
В корне проекта выполнить команду
```shell
docker-compose up 
```

документация API доступна по следующему адресу - http://127.0.0.1:8000/api/openapi 


### GitFlow
#### main
Ветка для деплоя в производственную среду. Содержит реализованный и протестированный функционал. В эту ветку Team Lead производит слияние нового функционала из dev в соответствии с релизным циклом.
#### dev 
Ветка для разработки и деплоя в тестовую среду. Тестирование реализованного функционала ведётся в этой ветке. В эту ветку разработчики производят слияние функционала, разработанного в локальных ветках разработки.
#### bugfix-<name-of-the-bug>
Ветка разработки некритичного багфикса, который вливается в dev-ветку.
#### feature-<name-of-the-feature>
Ветка разработки нового функционала.
#### <arbitrary-name-of-the-branch>
Ветка разработки нового/модификации старого функционала. Название ветки произвольное, однако оно должно отражать задачу, которая решается в данной ветке.
