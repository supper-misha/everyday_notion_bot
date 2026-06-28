from datetime import datetime, timedelta
from config import notion, bot, ID
import pytz

# ID источника данных для календаря
CALENDAR_DATA_SOURCE_ID = "38d0351c-9661-805b-bbc0-000b728efd23"
TZ = pytz.timezone('Europe/Moscow')


def get_events_for_date(target_date):
    """
    Получает все события из календаря на указанную дату

    Args:
        target_date (str): Дата в формате YYYY-MM-DD

    Returns:
        list: Список событий на указанную дату. Каждое событие содержит:
              - id: ID записи в Notion
              - name: Название события
              - date: Дата события (в том виде, в котором она хранится в Notion)
              Если событий нет, возвращает пустой список
    """
    try:
        # Запрашиваем события из Notion
        response = notion.data_sources.query(
            data_source_id=CALENDAR_DATA_SOURCE_ID,
            filter={
                "property": "Date",
                "date": {"equals": target_date}
            }
        )

        # Если записей нет, возвращаем пустой список
        if not response["results"]:
            return []

        # Извлекаем данные из каждой записи
        events = []
        for item in response["results"]:
            # Извлекаем название
            name_prop = item["properties"].get("Name", {})
            name = ""
            if name_prop.get("type") == "title" and name_prop.get("title"):
                name = "".join([p["plain_text"] for p in name_prop["title"]])

            # Извлекаем дату в том виде, в котором она хранится
            date_prop = item["properties"].get("Date", {})
            date = None
            if date_prop.get("type") == "date" and date_prop.get("date"):
                date = date_prop["date"].get("start")

            events.append({
                "id": item["id"],
                "name": name,
                "date": date  # Сохраняем как есть (может быть "2026-06-29" или "2026-06-29T15:30:00")
            })

        return events

    except Exception as e:
        print(f"❌ Ошибка при получении событий на {target_date}: {e}")
        return []


def send_tomorrow_reminders():
    """
    Получает события на завтра и отправляет напоминания в Telegram

    Returns:
        bool: True если отправлены напоминания, False если событий нет или ошибка
    """
    try:
        # Вычисляем завтрашнюю дату
        tomorrow = (datetime.now(TZ) + timedelta(days=1)).strftime("%Y-%m-%d")

        # Получаем события на завтра
        events = get_events_for_date(tomorrow)

        # Если событий нет, выходим
        if not events:
            return False

        # Форматируем дату для отображения
        tomorrow_display = datetime.strptime(tomorrow, "%Y-%m-%d").strftime("%d.%m.%Y")

        # Формируем сообщение
        message = (
            f"⏰ Завтра запланировано <b>{len(events)}</b> событий\n\n"
        )

        for event in events:
            # Извлекаем время из даты, если оно есть
            event_time = ""
            if event['date'] and "T" in event['date']:
                # Парсим время из формата "2026-06-29T15:30:00"
                time_part = event['date'].split("T")[1]
                # Берем только часы и минуты
                event_time = time_part[:5]  # "15:30"
                event_time = f"<b>{event_time}</b> "

            message += f"{event_time}{event['name']}\n"

        message += f"\nДата: <b>{tomorrow_display}</b>\n"

        # Отправляем сообщение
        bot.send_message(
            ID,
            message,
            parse_mode='HTML'  # Изменено с 'Markdown' на 'HTML'
        )

        return True

    except Exception as e:
        print(f"❌ Ошибка при отправке напоминаний: {e}")
        return False


@bot.message_handler(commands=['tomorrow'])
def handle_tomorrow(message):
    """Отправляет напоминания о событиях на завтра"""
    if str(message.chat.id) == ID:
        send_tomorrow_reminders()
