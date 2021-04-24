import slack
import os
from dotenv import load_dotenv
from flask import Flask

# Creating Flask app
app = Flask(__name__)

# Loading environemnt variables from .env
load_dotenv(dotenv_path='slackbot/.env')
# Specifying slack token
SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
SLACK_CLIENT = slack.WebClient(token=SLACK_TOKEN)

# SLACK_CLIENT.chat_postMessage(channel='#tutorial', text="Hello")

if __name__=="__main__":
    app.run(debug=True) # debug=True means flask will automagically update python code as we save, no need to re-run the server