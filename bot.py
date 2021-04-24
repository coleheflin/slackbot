import slack
import os
from dotenv import load_dotenv

# Loading environemnt variables from .env
load_dotenv(dotenv_path='slackbot/.env')
# Specifying slack token
SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
print(SLACK_TOKEN)
SLACK_CLIENT = slack.WebClient(token=SLACK_TOKEN)

SLACK_CLIENT.chat_postMessage(channel='#tutorial', text="Hello")