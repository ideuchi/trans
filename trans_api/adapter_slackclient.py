from django.conf import settings
import os
import datetime

SLACK_VERIFICATION_TOKEN = os.environ.get('SLACK_VERIFICATION_TOKEN','')
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN','')

from pyee import EventEmitter
from slack_sdk import WebClient
CLIENT = WebClient(SLACK_BOT_TOKEN)

class SlackEventAdapter(EventEmitter):
    def __init__(self, verification_token):
        EventEmitter.__init__(self)
        self.verification_token = verification_token

slack_events_adapter = SlackEventAdapter(SLACK_VERIFICATION_TOKEN)

DEBUG_FILE = 'debug.txt'

# reaction for emoji
@slack_events_adapter.on('reaction_added')
def reaction_added(event_data):
    event = event_data["event"]
    emoji = event["reaction"]
    channel = event["item"]["channel"]
    thread_ts = event["item"]["ts"]
    time = datetime.datetime.now()
    str_time = time.strftime('%Y/%m/%d %H:%M:%S')
    text = ':%s:' % emoji
    with open(DEBUG_FILE, 'a') as f:
        print('\n'+str_time+' response to reaction_added event:'+text+'.\n', file=f)
    CLIENT.api_call(api_method='chat.postMessage', json={'channel': channel, 'thread_ts': thread_ts, 'text': text})
