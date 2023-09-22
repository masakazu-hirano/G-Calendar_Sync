import json
import logging
import os
import pytz
import requests

from datetime import datetime
from dotenv import load_dotenv

class Notion_DB_Record:
	def __init__(self, id: str, title: str, category: str, start_date: datetime, end_date: datetime, created: datetime, updated: datetime):
		self.id: str = id
		self.title: str = title
		self.category: str = category
		self.start_date: datetime = start_date
		self.end_date: datetime = end_date
		self.created: datetime = created
		self.updated: datetime = updated

def Set_Header_Information() -> dict:
	return {
		'Authorization': f"Bearer {os.getenv(key = 'NOTION_SECRET_KEY')}",
		'accept': 'application/json',
		'content-type': 'application/json',
		'Notion-Version': '2022-06-28'
	}

def Get_Notion_DB_Record() -> list[Notion_DB_Record]:
	loop_count: int = 0
	record_list: list[Notion_DB_Record] = []
	has_more: bool = True
	while has_more:
		if loop_count == 0:
			response = requests.post(
				url = f"https://api.notion.com/v1/databases/{os.getenv(key = 'NOTION_DB_ID')}/query",
				headers = Set_Header_Information(),
				json = {
					'page_size': 100,
					'filter': {
						'property': 'Category',
						'select': { 'equals': 'Calendar（スケジュール管理）' }
					},
					'sorts': [
						{'property': '日時', 'direction': 'ascending'}
					]
				},
			)
		elif loop_count > 0:
			response = requests.post(
				url = f"https://api.notion.com/v1/databases/{os.getenv(key = 'NOTION_DB_ID')}/query",
				headers = Set_Header_Information(),
				json = {
					'start_cursor': start_cursor,
					'page_size': 100,
					'filter': {
						'property': 'Category',
						'select': { 'equals': 'Calendar（スケジュール管理）' }
					},
					'sorts': [
						{'property': '日時', 'direction': 'ascending'}
					]
				},
			)

		if response.status_code == 200:
			for result in json.loads(response.text)['results']:
				try:
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

			if json.loads(response.text)['has_more']:
				start_cursor = json.loads(response.text)['next_cursor']
				loop_count += 1
			else:
				has_more = json.loads(response.text)['has_more']
		else:
			logging.error(msg = f"ステータスコード: {json.loads(response.text)['status']}")
			logging.error(msg = f"エラーメッセージ: {json.loads(response.text)['message']}")
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
