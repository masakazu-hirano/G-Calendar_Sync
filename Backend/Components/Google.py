import json

from googleapiclient import discovery
from google.oauth2.service_account import Credentials

def GET_Google_Credential():
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

	return google_client
