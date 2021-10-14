import os
import datetime
import pytz
import subprocess as sp
import hashlib


DEBUG_FILE = 'debug.txt'

def debug_msg(str):
    with open(DEBUG_FILE, 'a') as f:
        dt_now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        str_time = dt_now.strftime('%Y/%m/%d %H:%M:%S')
        print('\n'+str_time+' '+str+'\n', file=f)


RESPONCED_EVENT_ID_FILE = 'responsed_event_id.txt'

def is_already_handled_event(event_id):
    if os.path.isfile(RESPONCED_EVENT_ID_FILE):
        with open(RESPONCED_EVENT_ID_FILE, 'r') as f:
            lines = f.readlines()
            if event_id+'\n' in lines:
                return True
    with open(RESPONCED_EVENT_ID_FILE, 'a') as f:
        print(event_id, file=f)
        return False


TRANSLATED_MSG_HASHED_FILE = 'translated_msg_hashed.txt'

langs = ['ar', 'de', 'en', 'es', 'fp', 'fr', 'id', 'it', 'ja', 'ko', 'pt', 'km', 'mn', 'my', 'ne', 'pt-BR', 'ru', 'th', 'vi', 'zh-CN', 'zh-TW']
lang_pairs = ['ar_en', 'ar_ja', 'de_en', 'de_ja', 'en_ar', 'en_de', 'en_es', 'en_fp', 'en_fr', 'en_id', 'en_it', 'en_ja', 'en_km', 'en_ko', 'en_mn', 'en_my', 'en_ne', 'en_pt', 'en_ru', 'en_th', 'en_vi', 'en_zh-CN', 'en_zh-TW', 'es_en', 'es_ja', 'fp_en', 'fp_ja', 'fr_en', 'fr_ja', 'id_en', 'id_ja', 'it_en', 'it_ja', 'ja_ar', 'ja_de', 'ja_en', 'ja_es', 'ja_fp', 'ja_fr', 'ja_id', 'ja_it', 'ja_km', 'ja_ko', 'ja_mn', 'ja_my', 'ja_ne', 'ja_pt', 'ja_pt-BR', 'ja_ru', 'ja_th', 'ja_vi', 'ja_zh-CN', 'ja_zh-TW', 'km_en', 'km_ja', 'ko_en', 'ko_ja', 'mn_en', 'mn_ja', 'my_en', 'my_ja', 'ne_en', 'ne_ja', 'pt_en', 'pt_ja', 'pt-BR_ja', 'ru_en', 'ru_ja', 'th_en', 'th_ja', 'vi_en', 'vi_ja', 'zh-CN_en', 'zh-CN_ja', 'zh-TW_en', 'zh-TW_ja']

def is_available_lang_code(str):
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

def lang_detect(src_message):
    lang_detect_cmd = './trans lang_detect "'+src_message+'"'
    debug_msg('(trans_util) lang_detect cmd: '+lang_detect_cmd)
    proc_lang_detect = sp.Popen(lang_detect_cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    proc_lang_std_out, proc_lang_std_err = proc_lang_detect.communicate()
    src_lang = proc_lang_std_out.decode('utf-8').rstrip()
    debug_msg('(trans_util) lang_detect src_lang: '+src_lang)
    if proc_lang_std_err.decode('utf-8').rstrip() != '':
        debug_msg('(trans_util) trans lang_detect std_err: '+proc_lang_std_err.decode('utf-8').rstrip())
        return 'en'  # if lang_detect didn't work, treat source message as en
    return src_lang

TEXTRA_CUSTOME_ENGINE = 'pt-BR_ja,voicetraNT|ja_pt-BR,voicetraNT|'+os.environ.get('TEXTRA_CUSTOME_ENGINE','')  # custom translation engine for specific lang pair
def get_engine(lang_pair):
    debug_msg('(trans_util) getting a engine for '+lang_pair+' from '+TEXTRA_CUSTOME_ENGINE)
    engine = 'generalNT'
    if TEXTRA_CUSTOME_ENGINE.rfind(lang_pair) >= 0:
        custom_engine_start = TEXTRA_CUSTOME_ENGINE[TEXTRA_CUSTOME_ENGINE.rfind(lang_pair):]
        engine_info = custom_engine_start.split('|')[0]
        debug_msg('(trans_util) custom engine found: '+engine_info)
        if len(engine_info.split(',')) > 1:
            engine = engine_info.split(',')[1]
    return engine

def trans(src_message, src_lang, tgt_lang, record_history=True):
    # If the same message/lang-pair is already translated recently (recorded in TRANSLATED_MSG_HASHED_FILE), ignore event
    msg_info = 'lang_pair: '+src_lang+'_'+tgt_lang+'\tmessage_digest: '+hashlib.sha224(src_message.encode("utf-8")).hexdigest()
    debug_msg('(trans_util) msg_info created: '+msg_info)
    if os.path.isfile(TRANSLATED_MSG_HASHED_FILE):
        with open(TRANSLATED_MSG_HASHED_FILE, 'r') as f:
            lines = f.readlines()
            if msg_info+'\n' in lines:
                debug_msg('(trans_util) This message/lang-pair is already translated: '+msg_info)
                return ''
    with open(TRANSLATED_MSG_HASHED_FILE, 'a') as f:
        debug_msg('(trans_util) new message to translate: '+msg_info)
        print(msg_info, file=f)
    debug_msg('(trans_util) call get_trans_pairs('+src_lang+', '+tgt_lang+')')
    trans_pairs = get_trans_pairs(src_lang, tgt_lang)
    debug_msg('(trans_util) get_trans_pairs() result: '+str(trans_pairs))
    trans_cmd = ''
    if len(trans_pairs) == 0:    # There's no translation pair
        debug_msg('(trans_util) trans pairs not found: '+src_lang+' to '+tgt_lang+'\nuse trans pair en to '+tgt_lang)
        trans_cmd = './trans text "'+src_message+'" '+get_engine('en_'+tgt_lang)+' en '+tgt_lang
    else:
        for i, pair in enumerate(trans_pairs):
            src_lang, tgt_lang = pair.split('_')
            if i == 0:
                trans_cmd = './trans text "'+src_message+'" '+get_engine(pair)+' '+src_lang+' '+tgt_lang
            else:
                trans_cmd = ' | ./trans text "'+src_message+'" '+get_engine(pair)+' '+src_lang+' '+tgt_lang
    proc_trans = sp.Popen(trans_cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    proc_trans_std_out, proc_trans_std_err = proc_trans.communicate()
    tgt_message = proc_trans_std_out.decode('utf-8').rstrip()
    debug_msg('(trans_util) trans_cmd: "'+trans_cmd+'", std_out: '+proc_trans_std_out.decode('utf-8').rstrip())
    if proc_trans_std_err.decode('utf-8').rstrip() != '':
        debug_msg('(trans_util) trans_cmd: "'+trans_cmd+'", std_err: '+proc_trans_std_err.decode('utf-8').rstrip())
        return 'Translation error: '+proc_trans_std_err.decode('utf-8').rstrip()  # if trans didn't work, return error message
    return tgt_message

