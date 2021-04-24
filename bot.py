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
welcome_messages = {}


class WelcomeMessage:
    START_TEXT = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "Welcome to this awesome channel! \n\n"
                "*Get started by completing the tasks!*"
            ),
        },
    }

    DIVIDER = {"type": "divider"}

    def __init__(self, channel, user):
        self.channel = channel
        self.user = user
        self.icon_emoji = ":robot_face:"
        self.timestamp = ""
        self.completed = False

    def get_message(self):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": "Welcome Robot!",
            "icon_emoji": self.icon_emoji,
            "blocks": [self.START_TEXT, self.DIVIDER, self._get_reaction_task()],
        }

    def _get_reaction_task(self):
        checkmark = ":white_check_mark:"
        if not self.completed:
            checkmark = ":white_large_square:"

        text = f"{checkmark} *React to this message!*"

        return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


def send_welcome_message(channel, user):
    welcome = WelcomeMessage(channel, user)
    message = welcome.get_message()
    response = SLACK_CLIENT.chat_postMessage(**message)
    welcome.timestamp = response["ts"]

    if channel not in welcome_messages:
        welcome_messages[channel] = {}
    welcome_messages[channel][user] = welcome


@SLACK_EVENT_ADAPTER.on("message")
def message(payload):
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")
    # Only process messages from the user, IGNORE THE BOT MESSAGES
    if user_id != None and BOT_ID != user_id:
        if user_id in message_counts:
            message_counts[user_id] += 1
        else:
            message_counts[user_id] = 1

        if text.lower() == "start":
            send_welcome_message(f"@{user_id}", user_id)


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
