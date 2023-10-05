import google.auth
import calendar
import json
import logging
import os
import pytz
import requests
import googleapiclient.discovery

from datetime import datetime
from dotenv import load_dotenv
from googleapiclient import discovery
from google.oauth2.service_account import Credentials

from Components.Notion_API import SET_Header, SET_Search_Condition

class Notion_DB_Record:
	def __init__(self, id, title, location, start_date, end_date, url):
		self.id = id
		self.title = title
		self.location = location
		self.start_date = start_date
		self.end_date = end_date
		self.url = url

# 現在時刻，月初，月末を Datetime 型で取得
def Current_Datetime(condition: str = 'current') -> datetime:
	current: datetime = datetime.now().astimezone(tz = pytz.timezone(zone = 'Asia/Tokyo'))

	if condition == 'current':
		return current.replace(microsecond = 0)
	elif condition == 'begin':
		return current.replace(
			day = 1,
			hour = 0,
			minute = 0,
			second = 0,
			microsecond = 0
		)
	elif condition == 'end':
		return current.replace(
			day = calendar.monthrange(year = current.year, month = current.month)[1],
			hour = 23,
			minute = 59,
			second = 59,
			microsecond = 00
		)
	else:
		logging.error(msg = "以下、いずれかの値を指定してください。\n→ 現在時刻: 'current', 月初: 'begin', 月末: 'end'")
		exit()

# 現在 Google カレンダーに登録されている予定の ID, ETag を取得
# def GET_Schedule_List(google_client) -> list:
# 	page_token = None
# 	results = []
# 	while True:
# 		schedule_list = google_client.events().list(
# 			calendarId = '6f03f4dba68734aab6ee5c2dbd6244603ac19064a23d11025370af7628514507@group.calendar.google.com',
# 			timeMin = Current_Datetime('begin').isoformat(),
# 			orderBy = 'startTime',
# 			timeZone = 'Asia/Tokyo',
# 			maxResults = 2500,
# 			singleEvents = True,
# 			pageToken = page_token
# 		).execute()

# 		if len(schedule_list['items']) == 0:
# 			logging.error(msg = '取得件数が 0件です。')
# 		else:
# 			for schedule in schedule_list['items']:
# 				results.append({
# 					'ID': schedule['id'],
# 					'ETag': schedule['etag']
# 				})

# 			try:
# 				page_token = schedule_list['nextPageToken']
# 			except KeyError:
# 				return results

# Notion API を実行する際の条件
def SET_Notion_Condition(value, start_cursor = None) -> str:
	if value == 'Header':
		data = {
			'content-type': 'application/json',
			'accept': 'application/json',
			'Authorization': f"Bearer {os.getenv(key = 'NOTION_SECRET_KEY')}",
			'Notion-Version': '2022-06-28'
		}
	elif value == 'Insert':
		data = {
			'page_size': 100,
			'sorts': [
				{'property': '日時', 'direction': 'ascending'},
				{'property': 'タイトル', 'direction': 'ascending'},
			],
			'filter': {
				'and': [
					{
						'property': 'Category',
						'select': {'equals': 'Calendar（スケジュール管理）'}
					},
					{
						'property': '日時',
						'date': {'after': Current_Datetime('begin').isoformat()}
					},
					{
						'property': 'Google カレンダー（ID）',
						'rich_text': {'is_empty': True}
					}
				]
			}
		}

		if start_cursor != None:
			data['start_cursor'] = start_cursor
	else:
		logging.error(msg = 'エラーが発生しました。')
		exit()

	return data

# NotionDB から、必要なレコード取得
def Get_Notion_DB_Record() -> list[Notion_DB_Record]:
	notion_db_url: str = f"https://api.notion.com/v1/databases/{os.getenv(key = 'NOTION_DB_ID')}/query"

	loop_count: int = 0
	has_more: bool = True
	start_cursor = None
	record_list: list[Notion_DB_Record] = []
	while has_more:
		if loop_count == 0:
			response = requests.post(
				url = notion_db_url,
				headers = SET_Notion_Condition('Header'),
				json = SET_Notion_Condition('Insert'),
			)
		elif loop_count > 0:
			response = requests.post(
				url = notion_db_url,
				headers = SET_Notion_Condition('Header'),
				json = SET_Notion_Condition('Insert', start_cursor)
			)

		if response.status_code == 200:
			for result in json.loads(s = response.text)['results']:
				try:
					end_date = datetime.fromisoformat(result['properties']['日時']['date']['end']).astimezone(tz = pytz.timezone('Asia/Tokyo'))
				except TypeError:
					end_date = None

				try:
					location = result['properties']['場所']['rich_text'][0]['text']['content']
				except IndexError:
					location = ''

				record_list.append(
					Notion_DB_Record(
						id = result['id'],
						title = result['properties']['タイトル']['title'][0]['text']['content'],
						location = location,
						start_date = datetime.fromisoformat(result['properties']['日時']['date']['start']).astimezone(tz = pytz.timezone('Asia/Tokyo')),
						end_date = end_date,
						url = result['url']
					)
				)

			if json.loads(s = response.text)['has_more']:
				start_cursor = json.loads(s = response.text)['next_cursor']
				loop_count += 1
			else:
				has_more = json.loads(s = response.text)['has_more']
		# else:
			# TODO: Notion API からエラーが返却された際の処理

	return record_list

def Regist_Google_Calendar(google_client, record):
	request = {
		'summary': record.title,
		'location': record.location,
		'description': record.url,
		'transparency': 'opaque',
		'visibility': 'private',
		'guestsCanSeeOtherGuests': False,
		'guestsCanModify': False,
		'anyoneCanAddSelf': False,
		'guestsCanInviteOthers': False
	}

	if record.end_date == None:
		request['start'] = {
			'date': record.start_date.date().isoformat(),
			'timeZone': 'Asia/Tokyo'
		}

		request['end'] = {
			'date': record.start_date.date().isoformat(),
			'timeZone': 'Asia/Tokyo'
		}

		google_calendar_response = google_client.events().insert(
			calendarId = os.getenv(key = 'GOOGLE_CALENDAR_ID'),
			sendUpdates = 'none',
			body = request
		).execute()
	else:
		request['start'] = {
			'dateTime': record.start_date.isoformat(),
			'timeZone': 'Asia/Tokyo'
		}

		request['end'] = {
			'dateTime': record.end_date.isoformat(),
			'timeZone': 'Asia/Tokyo'
		}

		google_calendar_response = google_client.events().insert(
			calendarId = os.getenv(key = 'GOOGLE_CALENDAR_ID'),
			sendUpdates = 'none',
			body = request
		).execute()

	requests.patch(
		url = f"https://api.notion.com/v1/pages/{record.id}",
		headers = SET_Notion_Condition('Header'),
		json = {
			'properties': {
				'Google カレンダー（ID）': {
					'rich_text': [{
							'text': {'content': google_calendar_response['id']}
					}]
				}
			}
		}
	)

if __name__ == '__main__':
	load_dotenv()
	logging.basicConfig(
		level = logging.INFO,
		format = '[{levelname}]: {message}',
		style = '{'
	)

	with open(
		file = './Google-Cloud_Secrets.json',
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

	count = 1
	records = Get_Notion_DB_Record()
	for record in records:
		Regist_Google_Calendar(google_client, record)
		logging.info(msg = f"進捗状況: {count}/{len(records)}\n新規登録 完了: {record.title}")
		count += 1



	logging.info(msg = '処理が正常に終了しました。')
