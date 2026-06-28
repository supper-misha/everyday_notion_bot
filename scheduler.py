from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from tg_routin import create_routin, check_and_notify_unchecked_tasks


def setup_scheduler():
    """
    Настраивает и возвращает планировщик с задачами
    """
    scheduler = BackgroundScheduler()

    # 75 софт в 6:00
    scheduler.add_job(
        create_routin,
        trigger=CronTrigger(hour=6, minute=0),
        args=['75_soft'],
        timezone="Europe/Moscow"
    )

    # Утренняя рутина в 6:05
    scheduler.add_job(
        create_routin,
        trigger=CronTrigger(hour=6, minute=5),
        args=['morning'],
        timezone="Europe/Moscow"
    )
    # Вечерняя рутина
    scheduler.add_job(
        create_routin,
        trigger=CronTrigger(hour=20, minute=5),
        args=['evening'],
        timezone="Europe/Moscow"
    )
    #
    scheduler.add_job(
        check_and_notify_unchecked_tasks,
        trigger=CronTrigger(hour=10, minute=5),
        args=['morning'],
        timezone="Europe/Moscow"
    )
    scheduler.add_job(
        check_and_notify_unchecked_tasks,
        trigger=CronTrigger(hour=18, minute=5),
        args=['75_soft'],
        timezone="Europe/Moscow"
    )
    scheduler.add_job(
        check_and_notify_unchecked_tasks,
        trigger=CronTrigger(hour=22, minute=5),
        args=['evening'],
        timezone="Europe/Moscow"
    )
    # Здесь можно добавить другие задачи вручную
    # scheduler.add_job(
    #     another_function,
    #     trigger=CronTrigger(hour=21, minute=0),
    #     id='another_task',
    #     name='Другая задача'
    # )

    return scheduler


def start_scheduler():
    """
    Запускает планировщик
    """
    scheduler = setup_scheduler()
    scheduler.start()
    return scheduler
