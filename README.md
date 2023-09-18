# Salary analysis

Анализ зарплат программистов с HeadHunter и SuperJob.

## Как установить

Python3 должен быть уже установлен. Затем используйте pip 
(или pip3, если есть конфликт с Python2) для установки зависимостей:

```bash
pip install -r requirements.txt
``` 

### будет установлен:

requests~=2.31.0
python-dotenv~=1.0.0
terminaltables~=3.1.10

## Переменные окружения

Необходимо создать файл **.env**, в нём должен содержаться API ключ полученный 
Вами на сайте **https://api.superjob.ru/**. Переменная должна иметь имя **API_KEY_SJ**

```bash
API_KEY_SJ='API ключ'
```

## Запуск

Запустите программу командой 
```bash
python main.py
```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).

 
