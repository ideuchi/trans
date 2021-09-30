from django.conf import settings
from django.http import HttpResponse
import os
import datetime
import subprocess as sp
import hashlib

SLACK_VERIFICATION_TOKEN = os.environ.get('SLACK_VERIFICATION_TOKEN','')
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN','')

from trans_api.trans_util import trans, lang_detect, is_available_lang_code, is_already_handled_event, debug_msg
slack_flag_langs = {
    # Extracted contry-lang pairs that has available lang from https://github.com/slackapi/reacjilator/blob/master/langcode.js
    'ae':'ar','bh':'ar','dz':'ar','eg':'ar','eh':'ar','iq':'ar','jo':'ar','kw':'ar','lb':'ar','ly':'ar','ma':'ar','mr':'ar','om':'ar','ps':'ar','qa':'ar','sa':'ar','sd':'ar','sw':'ar','tn':'ar','ye':'ar',
    'at':'de','ch':'de','de':'de','li':'de',
    'ac':'en','ag':'en','ai':'en','as':'en','au':'en','bb':'en','bn':'en','bs':'en','bw':'en','bz':'en','ca':'en','ck':'en','cx':'en','dm':'en','fj':'en','fk':'en','fm':'en','gb':'en','gd':'en','gg':'en','gh':'en','gi':'en','gm':'en','gs':'en','gu':'en','gy':'en','im':'en','io':'en','je':'en','jm':'en','ke':'en','ki':'en','kn':'en','ky':'en','lc':'en','lr':'en','mp':'en','ms':'en','mu':'en','mw':'en','na':'en','nf':'en','ng':'en','nz':'en','pn':'en','pw':'en','sb':'en','sc':'en','sg':'en','sh':'en','sl':'en','ss':'en','ta':'en','tc':'en','tt':'en','ug':'en','um':'en','us':'en','vc':'en','vg':'en','vi':'en','zm':'en','zw':'en',
    'ar':'es','bo':'es','cl':'es','co':'es','cr':'es','cu':'es','do':'es','ea':'es','ec':'es','es':'es','gq':'es','gt':'es','hn':'es','ic':'es','mx':'es','ni':'es','pa':'es','pe':'es','pr':'es','py':'es','sv':'es','uy':'es','ve':'es',
    'ph':'fp',  # added
    'bf':'fr','bi':'fr','bj':'fr','bl':'fr','cd':'fr','cf':'fr','cg':'fr','ci':'fr','cm':'fr','cp':'fr','dj':'fr','fr':'fr','ga':'fr','gf':'fr','gn':'fr','gp':'fr','mc':'fr','ml':'fr','mq':'fr','nc':'fr','ne':'fr','pf':'fr','pm':'fr','re':'fr','sn':'fr','td':'fr','tf':'fr','tg':'fr','wf':'fr','yt':'fr',
    'id':'id',
    'it':'it','sm':'it','va':'it',
    'jp':'ja',
    'kh':'km',
    'kp':'ko','kr':'ko',
    'mn':'mn',
    'mm':'my',  # added
    'np':'ne',
    'ao':'pt','cv':'pt','gw':'pt','mz':'pt','pt':'pt','st':'pt',
    'br':'pt-BR',
    'ru':'ru',
    'th':'th',
    'vn':'vi',
    'cn':'zh-CN',
    'hk':'zh-TW','mo':'zh-TW','tw':'zh-TW',
}

from pyee import EventEmitter
from slack_sdk import WebClient
CLIENT = WebClient(SLACK_BOT_TOKEN)

class SlackEventAdapter(EventEmitter):
    def __init__(self, verification_token):
        EventEmitter.__init__(self)
        self.verification_token = verification_token

slack_events_adapter = SlackEventAdapter(SLACK_VERIFICATION_TOKEN)

# Reaction for emoji
@slack_events_adapter.on('reaction_added')
def reaction_added(event_data):
    event_id = event_data['event_id']
    event = event_data['event']
    emoji = event['reaction']
    channel = event['item']['channel']
    ts = event['item']['ts']
    debug_msg('starting to handle reaction_added event. event_id = '+event_id+', emoji = '+emoji)
    # Get translation target language code from received emoji (If received emoji is not in translation target languages, ignore the event)
    tgt_lang = slack_flag_langs.get(emoji.replace('flag-',''))
    if is_available_lang_code(tgt_lang):
        debug_msg('recieved emoji is one of translation target languages: emoji = '+emoji+', lang = '+tgt_lang)
    else:
        debug_msg('recieved emoji is not in translation target languages: emoji = '+emoji)
        return HttpResponse('')
    # If same event is already received, ignore the event (If a response to the event is not returned, Slack sends same event in about 2 to 3 sec)
    if is_already_handled_event(event_id):
        debug_msg('This event is already handled: '+event_id)
        return HttpResponse('')
    debug_msg('This event is a new event to handle: '+event_id)
    # Get original message
    message_history = CLIENT.conversations_history(channel=channel, inclusive=True, oldest=ts, limit=1)
    src_message = message_history['messages'][0]['text']
    debug_msg('src message: '+src_message)
    # Detect src lang
    src_lang = lang_detect(src_message)
    debug_msg('src_lang: '+src_lang)
    # Translate message
    tgt_message = trans(src_message, src_lang, tgt_lang)
    debug_msg('response to reaction_added event:\n  cmd: '+trans_cmd+'\n  res: '+tgt_message)
    if tgt_message != '':
        CLIENT.api_call(api_method='chat.postMessage', json={'channel': channel, 'thread_ts': ts, 'text': tgt_message})
