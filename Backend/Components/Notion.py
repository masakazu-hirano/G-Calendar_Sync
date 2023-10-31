import json
import os

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
