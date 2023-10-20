import json
import logging
import os
import pytz
import requests

from datetime import datetime
from googleapiclient.errors import HttpError

def Calendar_Regist(google_client, current_datetime: datetime) -> int:
	def POST_LINE_Message(message):
		response = requests.post(
			url = 'https://api.line.me/v2/bot/message/push',
			headers = {
				'content-type': 'application/json',
				'Authorization': f"Bearer {os.getenv(key = 'LINE_CHANNEL_ACCESS_TOKEN')}",
			},
			json = {
				'to': os.getenv(key = 'LINE_USER_ID'),
				'notificationDisabled': False,
				'messages': [{
					'type': 'text',
					'text': message
				}]
			}
		)

	notion_request_header: dict[str, str] = {
		'content-type': 'application/json',
		'accept': 'application/json',
		'Authorization': f"Bearer {os.getenv(key = 'NOTION_SECRET_KEY')}",
		'Notion-Version': '2022-06-28'
	}

	regist_count: int = 0
	loop_count: int = 0
	has_more: bool = True
	while has_more:
		if loop_count == 0:
			get_records_response = requests.post(
				url = f"https://api.notion.com/v1/databases/{os.getenv(key = 'NOTION_DB_ID')}/query",
				headers = notion_request_header,
				json = {
					'page_size': 100,
					'sorts': [
						{'property': '日時', 'direction': 'ascending'},
						{'property': 'タイトル', 'direction': 'ascending'},
					],

					'filter': {
						'and': [
							{
								'property': 'Category',
								'multi_select': {'contains': 'Calendar（スケジュール管理）'}
							},
							{
								'property': '日時',
								'date': {'after': current_datetime.replace(
									day = 1,
									hour = 0,
									minute = 0,
									second = 0,
									microsecond = 0
								).isoformat()}
							},
							{
								'property': 'Google カレンダー（ID）',
								'rich_text': {'is_empty': True}
							}
						]
					}
				},
			)
		elif loop_count > 0:
			get_records_response = requests.post(
				url = f"https://api.notion.com/v1/databases/{os.getenv(key = 'NOTION_DB_ID')}/query",
				headers = notion_request_header,
				json = {
					'start_cursor': start_cursor,
					'page_size': 100,
					'sorts': [
						{'property': '日時', 'direction': 'ascending'},
						{'property': 'タイトル', 'direction': 'ascending'},
					],

					'filter': {
						'and': [
							{
								'property': 'Category',
								'multi_select': {'contains': 'Calendar（スケジュール管理）'}
							},
							{
								'property': '日時',
								'date': {'after': current_datetime.replace(
									day = 1,
									hour = 0,
									minute = 0,
									second = 0,
									microsecond = 0
								).isoformat()}
							},
							{
								'property': 'Google カレンダー（ID）',
								'rich_text': {'is_empty': True}
							}
						]
					}
				},
			)

		if get_records_response.status_code == 200:
			for record in json.loads(s = get_records_response.text)['results']:
				try:
					end_date = datetime.fromisoformat(record['properties']['日時']['date']['end']).astimezone(tz = pytz.timezone('Asia/Tokyo'))
				except TypeError:
					end_date = None

				try:
					location = record['properties']['場所']['rich_text'][0]['text']['content']
				except IndexError:
					location = ''

				if end_date == None:
					request_body = {
						'start': {
							'date': datetime.fromisoformat(record['properties']['日時']['date']['start']).astimezone(tz = pytz.timezone('Asia/Tokyo')).date().isoformat(),
							'timeZone': 'Asia/Tokyo'
						},
						'end': {
							'date': datetime.fromisoformat(record['properties']['日時']['date']['start']).astimezone(tz = pytz.timezone('Asia/Tokyo')).date().isoformat(),
							'timeZone': 'Asia/Tokyo'
						},

						'summary': record['properties']['タイトル']['title'][0]['text']['content'],
						'location': location,
						'description': record['url'],
						'transparency': 'opaque',
						'visibility': 'private',
						'guestsCanSeeOtherGuests': False,
						'guestsCanModify': False,
						'anyoneCanAddSelf': False,
						'guestsCanInviteOthers': False
					}
				else:
					request_body = {
						'start': {
							'dateTime': datetime.fromisoformat(record['properties']['日時']['date']['start']).astimezone(tz = pytz.timezone('Asia/Tokyo')).isoformat(),
							'timeZone': 'Asia/Tokyo'
						},
						'end': {
							'dateTime': end_date.isoformat(),
							'timeZone': 'Asia/Tokyo'
						},

						'summary': record['properties']['タイトル']['title'][0]['text']['content'],
						'location': location,
						'description': record['url'],
						'transparency': 'opaque',
						'visibility': 'private',
						'guestsCanSeeOtherGuests': False,
						'guestsCanModify': False,
						'anyoneCanAddSelf': False,
						'guestsCanInviteOthers': False
					}

				try:
					google_calendar_response = google_client.events().insert(
						calendarId = os.getenv(key = 'GOOGLE_CALENDAR_ID'),
						sendUpdates = 'none',
						body = request_body
					).execute()
				except HttpError as error:
					POST_LINE_Message(
						message = f"※ ERROR ※\n　■ 実行日: {current_datetime.replace(microsecond = 0)}\n　■ URL: {error.uri}\n　■ ステータスコード: {error.status_code}\n　■ エラーメッセージ: {error.error_details[0]['message']}"
					)

				update_record_response = requests.patch(
					url = f"https://api.notion.com/v1/pages/{record['id']}",
					headers = notion_request_header,
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

				if update_record_response.status_code != 200:
					POST_LINE_Message(
						message = f"※ ERROR ※\n　■ 実行日: {current_datetime.replace(microsecond = 0)}\n　■ URL: {update_record_response.url}\n　■ ステータスコード: {update_record_response.status_code}\n　■ エラーメッセージ: {json.loads(s = update_record_response.text)['message']}"
					)
					exit()

				regist_count += 1

			if json.loads(s = get_records_response.text)['has_more']:
				start_cursor = json.loads(s = get_records_response.text)['next_cursor']
				loop_count += 1
			else:
				has_more = json.loads(s = get_records_response.text)['has_more']

		else:
			POST_LINE_Message(
				message = f"※ ERROR ※\n　■ 実行日: {current_datetime.replace(microsecond = 0)}\n　■ URL: {get_records_response.url}\n　■ ステータスコード: {get_records_response.status_code}\n　■ エラーメッセージ: {json.loads(s = get_records_response.text)['message']}"
			)

			has_more = False

	return regist_count
