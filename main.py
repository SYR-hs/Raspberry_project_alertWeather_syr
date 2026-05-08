import urllib.request                      # 웹 페이지나 API에 HTTP 요청을 보내기 위한 모듈.
import json                                # 서버로부터 받은 JSON 형식의 데이터를 파이썬 딕셔너리 형태로 파싱하기 위한 모듈.
import datetime                            # 시스템의 현재 날짜와 시간 정보를 처리하기 위한 모듈.
import asyncio                             # 코드의 동시성(비동기) 처리를 지원하여, 무한 루프 중에도 다른 작업이 멈추지 않게 하는 모듈.
from telegram import Bot                   # 텔레그램 봇 API를 제어하기 위해 telegram 패키지에서 Bot 클래스.

telegram_id = 'Enter your chat ID here'    # 메시지를 수신할 사용자의 텔레그램 채팅 ID(chat_id)를 저장하는 변수.
my_token = 'Enter your bot token here'     # BotFather로부터 발급받은 봇의 고유 인증 토큰을 저장하는 변수.
api_key = 'Enter your API key here'        # 날씨 정보를 가져오기 위해 OpenWeatherMap에서 발급받은 API 키를 저장하는 변수.

bot = Bot(token=my_token) # 발급받은 토큰을 사용하여 텔레그램 Bot 객체를 생성하고 초기화.

ALERT_HOURS = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22] # 정각 알림을 보낼 시간대(07:00 ~ 22:00)를 리스트로 지정.
ALERT_TIMES = ["08:30", "12:35"] # 정각 외에 사용자 지정 시간(시:분)에 알림을 보내기 위한 목록을 리스트로 지정. 실험에서 사용된 시간은 오후 12시 35분.

def getWeather(): # OpenWeatherMap API를 호출하여 날씨 데이터를 수집하고 문자열로 가공하는 함수를 정의.
    url = f"https://api.openweathermap.org/data/2.5/forecast?q=Seoul&appid={api_key}&units=metric&lang=en&cnt=8" # 서울의 24시간(3시간 간격 8개) 날씨 예보를 요청하는 URL을 포맷팅하여 생성.

    with urllib.request.urlopen(url) as r: # 생성된 URL로 API 서버에 HTTP GET 요청을 보내고 응답을 r 변수로 받음.
        data = json.loads(r.read()) # 응답으로 받은 JSON 데이터를 읽어서 파이썬 딕셔너리 구조로 변환하여 data에 저장.

    text = "" # 가공된 날씨 텍스트를 누적해서 담을 빈 문자열을 생성.
    for i in range(8): # 3시간 간격의 예보 데이터 8개를 순차적으로 처리하기 위해 반복문을 실행.
        item = data['list'][i] # 전체 데이터 리스트에서 i번째 시간대의 날씨 데이터 묶음을 추출.
        hour = str((int(item['dt_txt'][11:13]) + 9) % 24).zfill(2) # UTC 기준의 예보 시간 텍스트를 추출하여 9를 더해 한국 시간(KST)으로 변환하고 2자리 문자열로 만듦.
        temp = item['main']['temp'] # 해당 시간대의 기온(temperature) 수치를 추출.
        humi = item['main']['humidity'] # 해당 시간대의 습도(humidity) 수치를 추출.
        desc = item['weather'][0]['description'] # 해당 시간대의 날씨 상태에 대한 상세 설명 텍스트를 추출.
        text += f"({hour}h {temp}C {humi}% {desc})\n" # 추출한 시간, 기온, 습도, 날씨 설명을 읽기 편한 형태의 한 줄 문자열로 만들어 text 변수에 누적 추가.

    return text # 완성된 날씨 예보 문자열을 호출한 곳으로 반환.

async def main(): # 메인 로직을 수행할 비동기(async) 함수를 정의.
    try: # 예기치 못한 에러나 강제 종료에 대비하여 예외 처리를 시작.
        while True: # 프로그램이 종료될 때까지 무한히 반복하는 루프.
            now = datetime.datetime.now() # 현재 시스템의 날짜 및 시간 정보.
            hm = now.strftime('%H:%M') # 현재 시간에서 '시:분' 형식의 문자열(예: "08:30")만 추출하여 저장.

            is_alert_hour = now.hour in ALERT_HOURS and now.minute == 0 and now.second == 0 # 현재 시간이 정각 알림 리스트에 있고, 정각(0분 0초)인지 확인하여 참/거짓 값을 저장.
            is_alert_time = hm in ALERT_TIMES and now.second == 0 # 현재 시/분이 사용자 지정 알림 시간에 일치하고 0초인지 확인하여 참/거짓 값을 저장.

            if is_alert_hour or is_alert_time: # 두 가지 알림 조건 중 하나라도 만족하는지 확인.
                msg = getWeather() # 조건이 만족되면 getWeather 함수를 호출하여 가공된 날씨 텍스트 확인.
                print(msg) # 가져온 날씨 텍스트를 터미널 창에 출력하여 정상 동작을 확인.
                await bot.send_message(chat_id=telegram_id, text=msg) # 텔레그램 서버로 날씨 메시지를 전송. API 호출이 완료될 때까지 비동기 대기(await).

            await asyncio.sleep(1) # 무한 루프가 과부하를 일으키지 않도록 1초 동안 비동기적으로 대기한 뒤 다음 루프를 실행.

    except KeyboardInterrupt: # 사용자가 터미널에서 Ctrl+C를 눌러 인터럽트를 발생시켰을 때의 예외를 처리.
        pass # 에러를 발생시키지 않고 조용히 예외를 넘기며 루프를 빠져나옵니다.

asyncio.run(main()) # 작성된 비동기 main 함수를 이벤트 루프에 등록하고 프로그램을 본격적으로 실행.
