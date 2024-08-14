
# Тестовое задание Python Developer

## Описание задания

Ваша задача заключается в написании алгоритма агрегации статистических данных о зарплатах сотрудников компании по временным промежуткам. Для выполнения задания необходимо использовать стек Python3, Asyncio, MongoDB, и любую асинхронную библиотеку для Telegram бота.
Входные данные:

1. Дата и время старта агрегации в ISO формате (dt_from)
2. Дата и время окончания агрегации в ISO формате (dt_upto)
3. Тип агрегации (group_type). Возможные значения: hour, day, month


Пример входных данных

    `{
    "dt_from": "2022-09-01T00:00:00",
    "dt_upto": "2022-12-31T23:59:00",
    "group_type": "month"
    }`

Пример выходных данных

    `{
    "dataset": [5906586, 5515874, 5889803, 6092634],
    "labels": ["2022-09-01T00:00:00", "2022-10-01T00:00:00", "2022-11-01T00:00:00", "2022-12-01T00:00:00"]
    }`

Cсылка на данные:
    https://drive.google.com/file/d/1pcNm2TAtXHO4JIad9dkzpbNc4q7NoYkx/view?usp=sharing

Установка и запуск:

1. Скачать файл с данными со статистическими зарплатными данными с GitHub.
2. Установить необходимые зависимости, используя команду `pip install -r requirements.txt`
3. Настроить виртуальное окружение (optional).
4. Убедиться, что на вашем устройстве установлена MongoDB.
5. Скачайте файл data.bson с данными со статистическими зарплатными данными.
6. Создайте базу данных в MongoDB и импортируйте данные из файла data.bson:

        mongorestore --drop --uri "mongodb://localhost:27017/companyDB" --collection statistics 

7. Скачайте репозиторий скрипта с помощью Git:

        git clone https://github.com/username/repository_name.git
        cd repository_name

8. Установите свой теллеграм токен в удобном для вас формате
        TELEGRAM_TOKEN = 'TELEGRAM_TOKEN' #os.environ.get('TELEGRAM_TOKEN')
    
Несколько примеров создания виртуального окружения:
Linux и macOS:

        python3 -m venv env
        source env/bin/activate

Windows:

        py -m venv env
        .\env\Scripts\activate
