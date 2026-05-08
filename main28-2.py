import urllib.request
import json
import datetime
import asyncio
from telegram import Bot

telegram_id = 'Enter your chat ID here'
my_token = 'Enter your bot token here'
api_key = 'Enter your API key here'

bot = Bot(token=my_token)

ALERT_HOURS = [7, 10, 13, 16, 19, 22]                                     # Hourly alerts every 3 hours
ALERT_TIMES = ["08:30", "15:20"]                                          # Custom time alerts (add your times here)

def getWeather():
    url = f"https://api.openweathermap.org/data/2.5/forecast?q=Seoul&appid={api_key}&units=metric&lang=en&cnt=8"

    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read())

    text = ""
    for i in range(8):
        item = data['list'][i]
        hour = str((int(item['dt_txt'][11:13]) + 9) % 24).zfill(2)
        temp = item['main']['temp']
        humi = item['main']['humidity']
        desc = item['weather'][0]['description']
        text += f"({hour}h {temp}C {humi}% {desc})\n"

    return text

async def main():
    try:
        while True:
            now = datetime.datetime.now()
            hm = now.strftime('%H:%M')                                     # Current time as HH:MM (e.g. "08:30")

            is_alert_hour = now.hour in ALERT_HOURS and now.minute == 0 and now.second == 0   # Check scheduled hour alert
            is_alert_time = hm in ALERT_TIMES and now.second == 0                             # Check custom time alert

            if is_alert_hour or is_alert_time:
                msg = getWeather()
                print(msg)
                await bot.send_message(chat_id=telegram_id, text=msg)

            await asyncio.sleep(1)

    except KeyboardInterrupt:
        pass

asyncio.run(main())