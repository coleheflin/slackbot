import slack
import os
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter


# Loading environemnt variables from .env
load_dotenv(dotenv_path="slackbot/.env")
# Specifying slack token
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
SIGNING_SECRET = os.environ.get("SIGNING_SECRET")
# Creating Flask app
app = Flask(__name__)
# Creating event adapter for handling slack events
SLACK_EVENT_ADAPTER = SlackEventAdapter(SIGNING_SECRET, "/slack/events", app)
# Creating slack client for interfacing with slack
SLACK_CLIENT = slack.WebClient(token=SLACK_TOKEN)
# Grabbing BOT_ID for later use
BOT_ID = SLACK_CLIENT.api_call("auth.test")["user_id"]
# SLACK_CLIENT.chat_postMessage(channel='#tutorial', text="Hello")
message_counts = {}


@SLACK_EVENT_ADAPTER.on("message")
def message(payload):
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")
    # Only process messages from the user, IGNORE THE BOT MESSAGES
    if BOT_ID != user_id:
        if user_id in message_counts:
            message_counts[user_id] += 1
        else:
            message_counts[user_id] = 1


# Slash Commands
@app.route("/message-count", methods=["POST"])
def message_count():
    data = request.form
    user_id = data.get("user_id")
    channel_id = data.get("channel_id")
    message_count = message_counts.get(user_id, 0)
    SLACK_CLIENT.chat_postMessage(
        channel=channel_id, text=f"Message Count: {message_count}"
    )
    return Response(), 200


if __name__ == "__main__":
    # debug=True means flask will automagically update python code as we save, no need to re-run the server
    app.run(debug=True)
