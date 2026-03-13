from datetime import time, datetime, timedelta
from zoneinfo import ZoneInfo
import os
import requests

from telegram.ext import ApplicationBuilder, ContextTypes

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Moscow")

CITY = "Moscow"
COUNTRY = "Russia"
METHOD = 2

async def send_morning_azkar(context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "🌿 Утренний азкар\n\n"
        "тест\n\n"
        "Не забудь прочитать утренние поминания."
    )

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=text
    )

async def send_evening_azkar(context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "🌙 Вечерний азкар\n\n"
        "тест\n\n"
        "Не забудь прочитать вечерние поминания."
    )

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=text
    )




def get_prayer_time() -> str:

    url = "https://api.aladhan.com/v1/timingsByCity"

    params = {
        "city": CITY,
        "country": COUNTRY,
        "method": METHOD
    }

    response = requests.get(url, params=params)
    data = response.json()
    
    return data["data"]["timings"]

def parse_time(time_str: str, tzinfo: ZoneInfo) -> time:
    clean_time_str = time_str.split(" ")[0]
    hour, minute = map(int, clean_time_str.split(":"))

    now = datetime.now(tz=tzinfo)    
    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

async def refresh_prayer_times(context: ContextTypes.DEFAULT_TYPE) -> None:
    tzinfo = ZoneInfo(TIMEZONE)

    timings = get_prayer_time()
    fajr_dt = parse_time(timings["Fajr"], tzinfo)
    asr_dt = parse_time(timings["Asr"], tzinfo)
    current_job = context.job_queue.jobs()
    
    for job in current_job:
        if job.name in ("daily_morning_azkar_post", "daily_evening_azkar_post"):
            job.schedule_removal()

    now = datetime.now(tz=tzinfo)
    
    if fajr_dt > now:
        context.job_queue.run_once(
            callback=send_morning_azkar,
            time=fajr_dt,
            name="today_morning_azkar_post"
        )

    if asr_dt > now:
        context.job_queue.run_once(
            callback=send_evening_azkar,
            time=asr_dt,
            name="today_evening_azkar_post"
        )

    print(f"Обновлены расписания на сегодня: Фаджр в {fajr_dt.time()}, Аср в {asr_dt.time()}", flush=True)





def main() -> None:
    if not TOKEN or not CHANNEL_ID:
        print("Ошибка: Необходимо установить переменные окружения TOKEN и CHANNEL_ID.")
        return
    
    tzinfo = ZoneInfo(TIMEZONE)

    application = (ApplicationBuilder()
    .token(TOKEN)
    .connect_timeout(30)
    .read_timeout(30)
    .write_timeout(30)
    .get_updates_connect_timeout(30)
    .get_updates_read_timeout(30)
    .build()
    )

    job_time = time(hour=0, minute=5, tzinfo=tzinfo)

    application.job_queue.run_daily(
        callback=refresh_prayer_times,
        time=job_time,
        name="daily_prayer_times_refresh"
    )

    application.job_queue.run_once(
        callback=refresh_prayer_times,
        when=5,
        name="initial_prayer_times_refresh"
    )

    timings = get_prayer_time()
    print(f"Бот запущен. Временная зона: {TIMEZONE}. Расписание будет обновляться ежедневно в {job_time}.\n"
          f"Сегодня: Фаджр в {timings['Fajr']}, Аср в {timings['Asr']}.", flush=True)
    
    application.run_polling()


if __name__ == "__main__":
    main()