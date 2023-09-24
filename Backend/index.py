import json
import logging
import os
import pytz
import requests

from datetime import datetime
from dotenv import load_dotenv
from Components.Notion_API import SET_Header, SET_Search_Condition

class Notion_DB_Record:
	def __init__(self, id: str, title: str, category: str, start_date: datetime, end_date: datetime, created: datetime, updated: datetime):
		self.id: str = id
		self.title: str = title
		self.category: str = category
		self.start_date: datetime = start_date
		self.end_date: datetime = end_date
		self.created: datetime = created
		self.updated: datetime = updated

def Get_Notion_DB_Record() -> list[Notion_DB_Record]:
	loop_count: int = 0
	has_more: bool = True
	notion_db_url: str = f"https://api.notion.com/v1/databases/{os.getenv(key = 'NOTION_DB_ID')}/query"
	record_list: list[Notion_DB_Record] = []
	while has_more:
		if loop_count == 0:
			response = requests.post(
				url = notion_db_url,
				headers = json.loads(s = SET_Header()),
				json = json.loads(s = SET_Search_Condition()),
			)
		elif loop_count > 0:
			response = requests.post(
				url = notion_db_url,
				headers = json.loads(s = SET_Header()),
				json = json.loads(s = SET_Search_Condition(start_cursor = start_cursor))
			)

		if response.status_code == 200:
			for result in json.loads(s = response.text)['results']:
				try:
					# 日時に、終了時刻が設定されている場合
					record_list.append(
						Notion_DB_Record(
							id = result['id'],
							title = result['properties']['タイトル']['title'][0]['text']['content'],
							category = result['properties']['Category（スケジュール管理）']['multi_select'][0]['name'],
							start_date = datetime.fromisoformat(result['properties']['日時']['date']['start']).astimezone(tz = pytz.timezone('Asia/Tokyo')),
							end_date = datetime.fromisoformat(result['properties']['日時']['date']['end']).astimezone(tz = pytz.timezone('Asia/Tokyo')),
							created = datetime.fromisoformat(result['created_time']).astimezone(tz = pytz.timezone('Asia/Tokyo')),
							updated = datetime.fromisoformat(result['last_edited_time']).astimezone(tz = pytz.timezone('Asia/Tokyo'))
						)
					)
				except TypeError:
					# 終日予定（終了時刻 未設定）の場合
					record_list.append(
						Notion_DB_Record(
							id = result['id'],
							title = result['properties']['タイトル']['title'][0]['text']['content'],
							category = result['properties']['Category（スケジュール管理）']['multi_select'][0]['name'],
							start_date = datetime.fromisoformat(result['properties']['日時']['date']['start']).astimezone(tz = pytz.timezone('Asia/Tokyo')),
							end_date = None,
							created = datetime.fromisoformat(result['created_time']).astimezone(tz = pytz.timezone('Asia/Tokyo')),
							updated = datetime.fromisoformat(result['last_edited_time']).astimezone(tz = pytz.timezone('Asia/Tokyo'))
						)
					)

			if json.loads(s = response.text)['has_more']:
				start_cursor = json.loads(s = response.text)['next_cursor']
				loop_count += 1
			else:
				has_more = json.loads(s = response.text)['has_more']
		else:
			logging.error(msg = f"ステータスコード: {json.loads(s = response.text)['status']}")
			logging.error(msg = f"エラーメッセージ: {json.loads(s = response.text)['message']}")
			break

	return record_list

if __name__ == '__main__':
	load_dotenv()
	logging.basicConfig(
		level = logging.INFO,
		format = '[{levelname}]: {message}',
		style = '{'
	)

	Get_Notion_DB_Record()
	logging.info(msg = '処理が正常に終了しました。')
