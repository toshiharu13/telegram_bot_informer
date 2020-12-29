import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s; %(levelname)s; %(name)s; %(message)s',
                   )

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    try:
        if homework.get('status') == 'rejected':
            verdict = 'К сожалению в работе нашлись ошибки.'
        elif homework.get('status') == 'approved':
            verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
        else:
            verdict = 'неизвестный статус работы'
            unknown_status = homework.get('status')
            logging.error(f'неизвестный статус {unknown_status}')
            return verdict
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except Exception as error:
        return logging.error(error, exc_info=True)


def get_homework_statuses(current_timestamp):
    headers = {
        'Authorization': f'OAuth {PRAKTIKUM_TOKEN}',
    }
    if current_timestamp is None:
        current_timestamp = int(time.time())
    params = {
        'from_date': current_timestamp,
    }
    try:
        homework_statuses = requests.get(url, headers=headers, params=params)
        return homework_statuses.json()
    except requests.RequestException as error:
        return logging.error(error, exc_info=True)


def send_message(message, bot_client):
    return bot_client.send_message(CHAT_ID, message)


def main():
    logging.debug('Бот запущен')
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            new_homework_request = new_homework.get('homeworks')
            if new_homework_request:
                send_message(
                    parse_homework_status(
                        new_homework_request[0]), bot_client
                )
                logging.info('Сообщение отправлено')
            # обновить timestamp
            current_timestamp = new_homework.get(
                'current_date', current_timestamp
            )
            time.sleep(1200)  # опрашивать раз в 20 минут

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой: {e}')
            send_message(e, bot_client)
            time.sleep(5)


if __name__ == '__main__':
    main()
