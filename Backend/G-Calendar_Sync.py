import json
import logging
import os
import pytz
import requests

from datetime import datetime
from dotenv import load_dotenv
from googleapiclient import discovery
from google.oauth2.service_account import Credentials

from Components.Create import Calendar_Regist

if __name__ == '__main__':
	load_dotenv()
	logging.basicConfig(
		level = logging.INFO,
		format = '[{levelname}]: {message}',
		style = '{'
	)

	time_zone = pytz.timezone(zone = 'Asia/Tokyo')
	current_datetime: datetime = datetime.now().astimezone(tz = time_zone).replace(microsecond = 0)

	notion_request_header: dict[str, str] = {
		'content-type': 'application/json',
		'accept': 'application/json',
		'Authorization': f"Bearer {os.getenv(key = 'NOTION_SECRET_KEY')}",
		'Notion-Version': '2022-06-28'
	}

	with open(
		file = '/usr/local/src/Google-Cloud_Secrets.json',
		mode = 'r',
		encoding = 'utf_8',
		newline = '\n',
		buffering = 1,
		closefd = True
	) as secrets:
		google_client = discovery.build(
			serviceName = 'calendar',
			version = 'v3',
			credentials = Credentials.from_service_account_info(
				info = json.load(fp = secrets),
				scopes = ['https://www.googleapis.com/auth/calendar.events'],
			),

			cache_discovery = False,
			num_retries = 3
		)

	regist_count = Calendar_Regist(google_client, current_datetime)
	requests.post(
		url = 'https://api.line.me/v2/bot/message/push',
		headers = {
			'content-type': 'application/json',
			'Authorization': f"Bearer {os.getenv(key = 'LINE_CHANNEL_ACCESS_TOKEN')}",
		},
		json = {
			'to': os.getenv(key = 'LINE_USER_ID'),
			'notificationDisabled': True,
			'messages': [{
				'type': 'text',
				'text': f"■ Google カレンダーに同期完了\n　──────────\n　■ 実行日: {current_datetime.replace(microsecond = 0)}\n　■ 新規登録: {regist_count}件"
			}]
		}
	)

	logging.info(msg = '処理が正常に終了しました。')
