import json
import logging
import os
import pytz

from datetime import datetime
from dotenv import load_dotenv
from requests import post, Response

from Components.Google import GET_Google_Credential
from Components.Notion import SET_Header as Notion_Request_Header
from Components.Notion import SET_Conditions

def Create_Events(current_datetime: datetime):
	notion_url: str = f"https://api.notion.com/v1/databases/{os.getenv(key = 'NOTION_DB_ID')}/query"

	loop_count: int = 0
	has_more: bool = True
	while has_more:
		if loop_count == 0:
			response: Response = post(
				url = notion_url,
				headers = json.loads(s = Notion_Request_Header()),
				json = json.loads(s = SET_Conditions(current_datetime)),
			)
		elif loop_count > 0:
			response: Response = post(
				url = notion_url,
				headers = json.loads(s = Notion_Request_Header()),
				json = json.loads(s = SET_Conditions(current_datetime, start_cursor)),
			)

		if response.status_code == 200:
			notion_records = json.loads(s = response.text)
			for record in notion_records['results']:
				logging.info(msg = record)
				break

			if notion_records['has_more']:
				start_cursor = notion_records['next_cursor']
				loop_count += 1
			else:
				has_more = notion_records['has_more']
		else:
			logging.info(msg = json.loads(s = response.text))
			has_more = False

	return None

def Update_Events():
	return None

if __name__ == '__main__':
	load_dotenv()
	logging.basicConfig(
		level = logging.INFO,
		format = '[{levelname}]: {message}',
		style = '{'
	)

	time_zone = pytz.timezone(zone = 'Asia/Tokyo')
	current_datetime: datetime = datetime.now().astimezone(tz = time_zone).replace(microsecond = 0)

	Create_Events(current_datetime)
	# regist_count = Calendar_Regist(google_client, current_datetime)
	# requests.post(
	# 	url = 'https://api.line.me/v2/bot/message/push',
	# 	headers = {
	# 		'content-type': 'application/json',
	# 		'Authorization': f"Bearer {os.getenv(key = 'LINE_CHANNEL_ACCESS_TOKEN')}",
	# 	},
	# 	json = {
	# 		'to': os.getenv(key = 'LINE_USER_ID'),
	# 		'notificationDisabled': True,
	# 		'messages': [{
	# 			'type': 'text',
	# 			'text': f"■ Google カレンダーに同期完了\n　──────────\n　■ 実行日: {current_datetime.replace(microsecond = 0)}\n　■ 新規登録: {regist_count}件"
	# 		}]
	# 	}
	# )

	logging.info(msg = '処理が正常に終了しました。')
