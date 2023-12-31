import json
import os

from datetime import datetime, timedelta

def SET_Header() -> str:
	return json.dumps(
		obj = {
			'content-type': 'application/json',
			'accept': 'application/json',
			'Authorization': f"Bearer {os.getenv(key = 'NOTION_SECRET_KEY')}",
			'Notion-Version': '2022-06-28'
		},

		indent = 4,
		sort_keys = True,
		ensure_ascii = False,
		allow_nan = False,
		skipkeys = False
	)

def SET_Conditions(current_datetime: datetime, condition: str = 'Create', start_cursor: str = None) -> str:
	if condition == 'Create':
		conditions: dict = {
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
							second = 0
						).isoformat()}
					},
					{
						'property': 'Google カレンダー（ID）',
						'rich_text': {'is_empty': True}
					}
				]
			}
		}
	elif condition == 'Update':
		previous_datetime: datetime = current_datetime - timedelta(days = 3)
		conditions: dict = {
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
						'property': 'Google カレンダー（ID）',
						'rich_text': {'is_not_empty': True}
					},
					{
						'timestamp': 'last_edited_time',
						'last_edited_time': {'after': previous_datetime.replace(
							hour = 0,
							minute = 0,
							second = 0
						).isoformat()}
					}
				]
			}
		}

	if start_cursor != None:
		conditions['start_cursor'] = start_cursor

	return json.dumps(
		obj = conditions,
		indent = 4,
		sort_keys = False,
		ensure_ascii = False,
		allow_nan = False,
		skipkeys = False
	)
