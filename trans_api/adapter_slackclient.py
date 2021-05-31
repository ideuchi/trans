from django.conf import settings
SLACK_VERIFICATION_TOKEN = settings.SLACK_VERIFICATION_TOKEN
SLACK_BOT_TOKEN = settings.SLACK_BOT_TOKEN

from pyee import EventEmitter
from slack_sdk import WebClient
CLIENT = WebClient(SLACK_BOT_TOKEN)

class SlackEventAdapter(EventEmitter):
    def __init__(self, verification_token):
        EventEmitter.__init__(self)
        self.verification_token = verification_token

slack_events_adapter = SlackEventAdapter(SLACK_VERIFICATION_TOKEN)

DEBUG_FILE = 'debug.txt'

# Example responder to greetings
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    time = datetime.datetime.now()
    str_time = time.strftime('%Y/%m/%d %H:%M:%S')
    # If the incoming message contains "hi", then respond with a "Hello" message
    if message.get("subtype") is None and "hi" in message.get('text'):
        channel = message["channel"]
        message = "Hello <@%s>! :tada:" % message["user"]
        with open(DEBUG_FILE, 'a') as f:
            print('\n'+str_time+' response to message event:'+message+'.\n', file=f)
        CLIENT.api_call("chat.postMessage", channel=channel, text=message)


# Example reaction emoji echo
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    event = event_data["event"]
    emoji = event["reaction"]
    channel = event["item"]["channel"]
    time = datetime.datetime.now()
    str_time = time.strftime('%Y/%m/%d %H:%M:%S')
    text = ":%s:" % emoji
    with open(DEBUG_FILE, 'a') as f:
        print('\n'+str_time+' response to reaction_added event:'+text+'.\n', file=f)
    CLIENT.api_call("chat.postMessage", channel=channel, text=text)
