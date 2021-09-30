import os
import datetime
import pytz
import subprocess as sp

SLACK_VERIFICATION_TOKEN = os.environ.get('SLACK_VERIFICATION_TOKEN','')
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN','')

DEBUG_FILE = 'debug.txt'
def debug_msg(str):
    with open(DEBUG_FILE, 'a') as f:
        dt_now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        str_time = dt_now.strftime('%Y/%m/%d %H:%M:%S')
        print('\n'+str_time+' '+str+'\n', file=f)

RESPONCED_EVENT_ID_FILE = 'responsed_event_id.txt'
TRANSLATED_MSG_HASHED_FILE = 'translated_msg_hashed.txt'

langs = ['ar', 'de', 'en', 'es', 'fp', 'fr', 'id', 'it', 'ja', 'ko', 'pt', 'km', 'mn', 'my', 'ne', 'pt-BR', 'ru', 'th', 'vi', 'zh-CN', 'zh-TW']
lang_pairs = ['ar_en', 'ar_ja', 'de_en', 'de_ja', 'en_ar', 'en_de', 'en_es', 'en_fp', 'en_fr', 'en_id', 'en_it', 'en_ja', 'en_km', 'en_ko', 'en_mn', 'en_my', 'en_ne', 'en_pt', 'en_ru', 'en_th', 'en_vi', 'en_zh-CN', 'en_zh-TW', 'es_en', 'es_ja', 'fp_en', 'fp_ja', 'fr_en', 'fr_ja', 'id_en', 'id_ja', 'it_en', 'it_ja', 'ja_ar', 'ja_de', 'ja_en', 'ja_es', 'ja_fp', 'ja_fr', 'ja_id', 'ja_it', 'ja_km', 'ja_ko', 'ja_mn', 'ja_my', 'ja_ne', 'ja_pt', 'ja_pt-BR', 'ja_ru', 'ja_th', 'ja_vi', 'ja_zh-CN', 'ja_zh-TW', 'km_en', 'km_ja', 'ko_en', 'ko_ja', 'mn_en', 'mn_ja', 'my_en', 'my_ja', 'ne_en', 'ne_ja', 'pt_en', 'pt_ja', 'pt-BR_ja', 'ru_en', 'ru_ja', 'th_en', 'th_ja', 'vi_en', 'vi_ja', 'zh-CN_en', 'zh-CN_ja', 'zh-TW_en', 'zh-TW_ja']
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

def check_handled_event(event_id)
    if os.path.isfile(RESPONCED_EVENT_ID_FILE):
        with open(RESPONCED_EVENT_ID_FILE, 'r') as f:
            lines = f.readlines()
            if event_id+'\n' in lines:
                return True
    with open(RESPONCED_EVENT_ID_FILE, 'a') as f:
        print(event_id, file=f)
        return False

def lang_detect(src_message):
    lang_detect_cmd = './trans lang_detect "'+src_message+'"'
    debug_msg('lang_detect cmd: '+lang_detect_cmd)
    proc_lang_detect = sp.Popen(lang_detect_cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    proc_lang_std_out, proc_lang_std_err = proc_lang_detect.communicate()
    src_lang = proc_lang_std_out.decode('utf-8').rstrip()
    debug_msg('lang_detect src_lang: '+src_lang)
    if proc_lang_std_err.decode('utf-8').rstrip() != '':
        debug_msg('trans lang_detect std_err: '+proc_lang_std_err.decode('utf-8').rstrip())
        return 'en'  # if lang_detect didn't work, treat source message as en
    return src_lang

def trans(src_message, src_lang, tgt_lang):
    debug_msg('call get_trans_pairs('+src_lang+', '+tgt_lang+')')
    trans_pairs = get_trans_pairs(src_lang, tgt_lang)
    debug_msg('get_trans_pairs() result: '+str(trans_pairs))
    trans_cmd = ''
    if len(trans_pairs) == 0:    # There's no translation pair
        debug_msg('trans pairs not found: '+src_lang+' to '+tgt_lang+'\nuse trans pair en to '+tgt_lang)
        if tgt_lang == 'pt-BR':
            trans_cmd = './trans text "'+src_message+'" voicetraNT en '+tgt_lang
        else:
            trans_cmd = './trans text "'+src_message+'" generalNT en '+tgt_lang
    else:
        for i, pair in enumerate(trans_pairs):
            src_lang, tgt_lang = pair.split('_')
            if i == 0:
                if src_lang == 'pt-BR' or tgt_lang == 'pt-BR':
                    trans_cmd = './trans text "'+src_message+'" voicetraNT '+src_lang+' '+tgt_lang
                else:
                    trans_cmd = './trans text "'+src_message+'" generalNT '+src_lang+' '+tgt_lang
            else:
                if src_lang == 'pt-BR' or tgt_lang == 'pt-BR':
                    trans_cmd += ' | ./trans text "" voicetraNT '+src_lang+' '+tgt_lang
                else:
                    trans_cmd += ' | ./trans text "" generalNT '+src_lang+' '+tgt_lang
    proc_trans = sp.Popen(trans_cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    proc_trans_std_out, proc_trans_std_err = proc_trans.communicate()
    tgt_message = proc_trans_std_out.decode('utf-8').rstrip()
    if proc_trans_std_err.decode('utf-8').rstrip() != '':
        debug_msg(trans_cmd+' std_err: '+proc_trans_std_err.decode('utf-8').rstrip())
        return ''  # if lang_detect didn't work, return '' as target message
    return tgt_message

