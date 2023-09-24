import json
import os

def SET_Header() -> str:
	return json.dumps(
		obj = 	{
			'Authorization': f"Bearer {os.getenv(key = 'NOTION_SECRET_KEY')}",
			'accept': 'application/json',
			'content-type': 'application/json',
			'Notion-Version': '2022-06-28'
		},

		skipkeys = False,
		indent = 4,
		sort_keys = True,
		ensure_ascii = False,
		allow_nan = False
	)

def SET_Search_Condition(start_cursor: str = None) -> str:
	if start_cursor == None:
		return json.dumps(
			obj = {
				'page_size': 100,
				'sorts': [{'property': '日時', 'direction': 'ascending'}],
				'filter': {
					'property': 'Category',
					'select': {'equals': 'Calendar（スケジュール管理）'}
				},
			},

			skipkeys = False,
			indent = 4,
			sort_keys = True,
			ensure_ascii = False,
			allow_nan = False
		)
	else:
		return json.dumps(
			obj = {
				'page_size': 100,
				'start_cursor': start_cursor,
				'sorts': [{'property': '日時', 'direction': 'ascending'}],
				'filter': {
					'property': 'Category',
					'select': {'equals': 'Calendar（スケジュール管理）'}
				},
			},

			skipkeys = False,
			indent = 4,
			sort_keys = True,
			ensure_ascii = False,
			allow_nan = False
		)
