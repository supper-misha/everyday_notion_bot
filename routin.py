from datetime import datetime
from config import notion

ROUTIN_DB_ID = "38d0351c-9661-8098-8c0e-000b88dd4316"

ROUTIN_TYPES = {
    'morning': "Утро",
    'evening': "Вечер",
    '75_soft': "75 soft"
}
TASK_FILTERS = {
    'morning': [
        'Заправить кровать',
        'Почистить зубы, умыться',
        'Использовать Авамис',
        'Сделать 15 отжиманий',
        'Позавтракать'
    ],
    'evening': [
        'Поужинать',
        'Принять душ, почистить зубы, умыться',
        'Использовать Авамис'
    ],
    '75_soft': [
        '2л воды',
        '40 минут прогулки',
        '15 минут изучения языков',
        '20 минут медитация',
        'закалка'
    ]
}


def create_notion_record(data_source_id, name, tag, date=None):
    """
    Создает новую запись в Notion через Data Source

    Args:
        data_source_id (str): ID источника данных
        name (str): Название записи (поле "Name")
        tag (str): Тэг/тип записи (поле "Select")
        date (str, optional): Дата в формате YYYY-MM-DD или YYYY-MM-DDTHH:MM:SS
                               Если не указана, используется текущая дата

    Returns:
        dict: Данные созданной страницы

    Raises:
        Exception: При ошибке создания записи
    """
    # Если дата не указана, используем сегодняшнюю
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    try:
        new_page = notion.pages.create(
            parent={
                "type": "data_source_id",
                "data_source_id": data_source_id
            },
            properties={
                "Name": {
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": name}
                        }
                    ]
                },
                "Select": {
                    "select": {"name": tag}
                },
                "Date": {
                    "date": {"start": date}
                }
            }
        )

        return new_page

    except Exception as e:
        print(f"❌ Ошибка при создании записи: {e}")
        raise


def create_routin_record(routin_name):
    try:
        if routin_name not in ROUTIN_TYPES:
            raise ValueError(f"Неизвестный тип: {routin_name}")

        tag = ROUTIN_TYPES[routin_name]
        current_date = datetime.now().strftime("%Y-%m-%d")
        heading = datetime.now().strftime("%d.%m.%y")

        return create_notion_record(
            data_source_id=ROUTIN_DB_ID,
            name=heading,
            tag=tag,
            date=current_date
        )

    except Exception as e:
        print(f"❌ Ошибка при создании '{routin_name}': {e}")
        return None


def get_unchecked_tasks(routin_name):
    """
    Проверяет сегодняшнюю запись рутины и возвращает список неотмеченных чекбоксов

    Args:
        routin_name (str): Ключ рутины ('morning', 'evening', '75_soft')

    Returns:
        list: Список названий неотмеченных задач (чекбоксов)
              Возвращает пустой список, если все задачи выполнены или запись не найдена
    """

    # Проверка существования типа рутины
    if routin_name not in ROUTIN_TYPES:
        print(f"❌ Ошибка: Неизвестный тип рутины '{routin_name}'")
        print(f"   Доступные типы: {', '.join(ROUTIN_TYPES.keys())}")
        return []

    tag = ROUTIN_TYPES[routin_name]
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        # Поиск сегодняшней записи с нужным тегом
        response = notion.data_sources.query(
            data_source_id=ROUTIN_DB_ID,
            filter={
                "and": [
                    {
                        "property": "Select",
                        "select": {"equals": tag}
                    },
                    {
                        "property": "Date",
                        "date": {"equals": today}
                    }
                ]
            }
        )

        # Если запись не найдена
        if not response["results"]:
            print(f"⚠️ Запись для '{routin_name}' на сегодня ({today}) не найдена")
            return []

        # Берем первую найденную запись
        page = response["results"][0]
        properties = page["properties"]

        # Получаем список задач для данного типа рутины
        allowed_tasks = TASK_FILTERS.get(routin_name, [])

        # Собираем все неотмеченные чекбоксы
        unchecked_tasks = []

        for prop_name, prop_value in properties.items():
            # Проверяем, что это чекбокс и он не отмечен
            if prop_value.get("type") == "checkbox" and prop_value.get("checkbox") is False:
                # Если есть фильтр задач, проверяем, входит ли задача в список
                if allowed_tasks:
                    if prop_name in allowed_tasks:
                        unchecked_tasks.append(prop_name)
                else:
                    # Если фильтр не задан, учитываем все чекбоксы
                    unchecked_tasks.append(prop_name)

        return unchecked_tasks

    except Exception as e:
        print(f"❌ Ошибка при проверке задач: {e}")
        return []


if __name__ == "__main__":
    print(get_unchecked_tasks("75_soft"))
