from config import bot, ID
from routin import create_routin_record, get_unchecked_tasks
from datetime import datetime

ROUTIN_NAMES = {
    'morning': 'УТРО 🌅',
    'evening': 'ВЕЧЕР 🌃',
    '75_soft': '75 СОФТ ⛩'
}


@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(ID, "Бот работает")


@bot.message_handler(commands=["test"])
def test(message):
    check_and_notify_unchecked_tasks("morning")


def create_routin(routin_name):
    """
    Создает запись ежедневной рутины и отправляет уведомление в Telegram
    """
    try:
        # Создаем запись в Notion
        result = create_routin_record(routin_name)

        # Отправляем сообщение в Telegram
        if result:
            name = ROUTIN_NAMES[routin_name]
            bot.send_message(
                ID,
                f"Создана рутина <b>{name}</b>",
                parse_mode="HTML"
            )
        else:
            bot.send_message(
                ID,
                "❌ Все сломалось"
            )

    except Exception as e:
        bot.send_message(
            ID,
            f"❌ Ошибка: {str(e)}"
        )


def check_and_notify_unchecked_tasks(routin_name):
    """
    Проверяет невыполненные задачи и отправляет уведомление, если они есть

    Args:
        routin_name (str): Ключ рутины ('morning', 'evening', '75_soft')
        display_name (str): Название для отображения в сообщении
    """
    try:
        display_name = ROUTIN_NAMES[routin_name]
        # Получаем список невыполненных задач
        unchecked_tasks = get_unchecked_tasks(routin_name)

        # Если есть невыполненные задачи
        if unchecked_tasks:
            current_time = datetime.now().strftime("%H:%M")

            # Формируем сообщение
            message = f"⚠️ Уже <b>{current_time}</b>, а в <b>{display_name}</b> не выполнены задачи:\n"

            # Добавляем список задач с маркерами
            for task in unchecked_tasks:
                message += f"✖️ {task}\n"

            # Отправляем сообщение
            bot.send_message(
                ID,
                message,
                parse_mode='HTML'
            )

    except Exception as e:
        print(f"❌ Ошибка при проверке задач {display_name}: {e}")
        # Можно отправить сообщение об ошибке в Telegram
        bot.send_message(
            ID,
            f"❌ Ошибка при проверке {display_name} рутины: {str(e)}"
        )
