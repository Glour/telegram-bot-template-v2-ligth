from datetime import datetime, timedelta
from typing import Callable, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


async def set_scheduled_jobs(
        scheduler: AsyncIOScheduler,
        funk: Callable[..., Any],
        trigger: str = "date",
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        timezone: str = 'Europe/Moscow',
        *args: Any,
        **kwargs: Any
) -> None:
    """
    Schedules jobs to be run on the APScheduler based on specified parameters.

    :param scheduler: The scheduler instance to which the jobs will be added.
    :param funk: The function to be scheduled.
    :param trigger: Type of trigger for the job ('cron', 'interval', etc.). Defaults to 'cron'.
    :param days: Number of days before the job should be run. Defaults to 0.
    :param hours: Number of hours before the job should be run. Defaults to 0.
    :param minutes: Number of minutes before the job should be run. Defaults to 0.
    :param seconds: Number of seconds before the job should be run. Defaults to 0.
    :param timezone: Timezone in which the job should be run. Defaults to 'Europe/Moscow'.
    :param args: Additional positional arguments to pass to the function.
    :param kwargs: Additional keyword arguments to pass to the function.
    :return: None
    """
    if trigger == "date":
        # Schedule a one-time job
        run_date = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        scheduler.add_job(
            func=funk,
            trigger=trigger,
            run_date=run_date,
            timezone=timezone,
            args=args,
            kwargs=kwargs,
        )
    elif trigger == "cron":
        # Schedule a cron-based job
        cron_trigger = CronTrigger(
            hour=hours,
            minute=minutes,
            second=seconds,
            timezone=timezone,
        )
        scheduler.add_job(
            func=funk,
            trigger=cron_trigger,
            args=args,
            kwargs=kwargs,
        )
    else:
        # For other triggers, you may need to adjust the arguments accordingly
        scheduler.add_job(
            func=funk,
            trigger=trigger,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            timezone=timezone,
            args=args,
            kwargs=kwargs,
        )


def get_scheduler():
    return AsyncIOScheduler()
