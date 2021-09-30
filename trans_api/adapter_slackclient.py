from django.conf import settings
from django.http import HttpResponse
import os
import datetime
import subprocess as sp
import hashlib

from trans_api.trans_util import trans, lang_detect, slack_flag_langs, check_handled_event, debug_msg

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

# reaction for emoji
@slack_events_adapter.on('reaction_added')
def reaction_added(event_data):
    event_id = event_data['event_id']
    event = event_data['event']
    emoji = event['reaction']
    channel = event['item']['channel']
    ts = event['item']['ts']
    debug_msg('starting handle reaction_added event.')
    # Get target language code from emoji (If emoji is not language code, ignore event)
    tgt_lang = slack_flag_langs.get(emoji.replace('flag-',''))
    if is_available_lang_code(tgt_lang):
        debug_msg('emoji is one of target lang: emoji = '+emoji+', lang = '+tgt_lang)
    else:
        debug_msg('emoji is not in target lang: emoji = '+emoji)
        return HttpResponse('')
    # If same event is already received, ignore event (Slack sends same event in about 2 to 3 sec)
    if check_handled_event(event_id):
        debug_msg('This event is already handled: '+event_id)
        return HttpResponse('')
    debug_msg('new event to handle: '+event_id)
    # Get original message
    message_history = CLIENT.conversations_history(channel=channel, inclusive=True, oldest=ts, limit=1)
    src_message = message_history['messages'][0]['text']
    debug_msg('src message: '+src_message)
    # Detect src lang
    src_lang = lang_detect(src_message)
    # Translate message
    tgt_message = trans(src_message, src_lang, tgt_lang)
    debug_msg('response to reaction_added event:\n  cmd: '+trans_cmd+'\n  res: '+tgt_message)
    if tgt_message != '':
        CLIENT.api_call(api_method='chat.postMessage', json={'channel': channel, 'thread_ts': ts, 'text': tgt_message})
