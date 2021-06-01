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
RESPONCE_FILE = 'response.txt'

langs = ['ar', 'de', 'en', 'es', 'fp', 'fr', 'id', 'it', 'ja', 'ko', 'my', 'pt', 'pt-BR', 'ru', 'th', 'vi', 'zh-CN', 'zh-TW']
lang_pairs = ['ar_en', 'de_en', 'de_ja', 'en_ar', 'en_de', 'en_es', 'en_fr', 'en_id', 'en_it', 'en_ja', 'en_ko', 'en_my', 'en_pt', 'en_ru''en_vi', 'en_zh-TW', 'en_th', 'en_zh-CN', 'es_en', 'es_ja', 'fr_en', 'fr_ja', 'id_en', 'id_ja', 'it_en', 'ja_de', 'ja_es', 'ja_en', 'ja_fr', 'ja_id', 'ja_ko', 'ja_my', 'ja_pt', 'ja_th', 'ja_vi', 'ja_zh-CN', 'ja_zh-TW', 'ko_en', 'ko_ja', 'my_en', 'my_ja', 'pt_en', 'pt_ja', 'ru_en', 'th_en', 'th_ja', 'vi_en', 'vi_ja', 'zh-CN_en', 'zh-CN_ja', 'zh-TW_en', 'zh-TW_ja', ]

def is_lang_code(str):
    return str in langs

def get_trans_pairs(lang1, lang2):
    if '_'.join([lang1, lang2]) in lang_pairs:    # direct translation
        return ['_'.join([lang1, lang2])]
    elif ('_'.join([lang1, 'ja']) in lang_pairs) and ('_'.join(['ja', lang2]) in lang_pairs):    # pivot translation via ja
        return ['_'.join([lang1, 'ja']), '_'.join(['ja', lang2])]
    elif ('_'.join([lang1, 'en']) in lang_pairs) and ('_'.join(['en', lang2]) in lang_pairs):    # pivot translation via en
        return ['_'.join([lang1, 'en']), '_'.join(['en', lang2])]
    else:
        return []

# reaction for emoji
def reaction_added(event_data):
    event_id = event_data['event_id']
    event = event_data['event']
    emoji = event['reaction']
    channel = event['item']['channel']
    ts = event['item']['ts']
    with open(DEBUG_FILE, 'a') as f:
        time = datetime.datetime.now()
        str_time = time.strftime('%Y/%m/%d %H:%M:%S')
        print('\n'+str_time+' starting handle reaction_added event\n', file=f)
    # Get target language code from emoji (If emoji is not language code, ignore event)
    if emoji == 'us':
        emoji = 'en'
    if emoji == 'cn':
        emoji = 'zh-CN'
    if emoji == 'flag-tw':
        emoji = 'zh-TW'
    tgt_lang = ''
    if is_lang_code(emoji):
        tgt_lang = emoji
    else:
        time = datetime.datetime.now()
        str_time = time.strftime('%Y/%m/%d %H:%M:%S')
        with open(DEBUG_FILE, 'a') as f:
            print('\n'+str_time+' emoji is not in lang_list: '+emoji+'\n', file=f)
        return HttpResponse('')
    # If same event is already received, ignore event
    with open(RESPONCE_FILE, 'ar') as f:
        time = datetime.datetime.now()
        str_time = time.strftime('%Y/%m/%d %H:%M:%S')
        if event_id in f.read():
            with open(DEBUG_FILE, 'a') as f:
                print('\n'+str_time+' event already handled: '+event_id+'\n', file=f)
            return HttpResponse('')
        else:
            with open(DEBUG_FILE, 'a') as f:
                print('\n'+str_time+' new event to handle: '+event_id+'\n', file=f)
            print(event_id+'\n', file=f)
    # Get original message
    src_message = CLIENT.api_call(api_method='conversations.history', json={'channel': channel, 'inclusive': True, 'oldest': ts, 'limit': 1})['messages'][0]['text']
    proc_lang_detect = sp.Popen('./trans lang_detect "'+src_message+'"', shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    src_lang, proc_lang_std_err = proc_lang_detect.communicate()
    if proc_lang_std_err != '':
        with open(DEBUG_FILE, 'a') as f:
            time = datetime.datetime.now()
            str_time = time.strftime('%Y/%m/%d %H:%M:%S')
            print('\n'+str_time+' trans lang_detect std_err: '+proc_lang_std_err+'.\n', file=f)
        return HttpResponse('')
    # Translate message
    trans_pairs = get_trans_pairs(src_lang, tgt_lang)
    trans_cmd = ''
    if len(trans_pairs) == 0:    # There's no translation pair
        time = datetime.datetime.now()
        str_time = time.strftime('%Y/%m/%d %H:%M:%S')
        with open(DEBUG_FILE, 'a') as f:
            print('\n'+str_time+' trans pairs not found: '+src_lang+' to '+tgt_lang+'\n', file=f)
        return HttpResponse('')
    else:
        for i, pair in enumerate(trans_pairs):
            src_lang, tgt_lang = pair.split('_')
            if i == 0:
                trans_cmd = './trans text "'+src_message+'" generalNT '+src_lang+' '+tgt_lang
            else:
                trans_cmd = ' | ./trans text "" generalNT '+src_lang+' '+tgt_lang
    proc_trans = sp.Popen(trans_cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    tgt_message, proc_trans_std_err = proc_lang_detect.communicate()
    time = datetime.datetime.now()
    str_time = time.strftime('%Y/%m/%d %H:%M:%S')
    if proc_trans_std_err != '':
        with open(DEBUG_FILE, 'a') as f:
            print('\n'+str_time+' '+trans_cmd+' std_err: '+proc_trans_std_err+'.\n', file=f)
        return HttpResponse('')
    with open(DEBUG_FILE, 'a') as f:
        print('\n'+str_time+' response to reaction_added event '+trans_cmd+': '+tgt_message+'.\n', file=f)
    CLIENT.api_call(api_method='chat.postMessage', json={'channel': channel, 'thread_ts': ts, 'text': tgt_message})
