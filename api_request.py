# -*- coding: utf-8 -*-
"""
Python3 OAuthRequest Module for NICT TexTra translation API
  prerequisites:
    creating account via the following URL:
      https://mt-auto-minhon-mlt.ucri.jgn-x.jp/content/register/
      after creating account, you can get "name", "key", "secret" parameters.
  parameters:
    1: name
    2: key
    3: secret
    4: translation kind (text/file/dir/lang_detect/word_lookup/bilingual_root/adaptation)
    5: translation subkind (for file, word_lookup, bilingual_root, adaptation)
    6: source text/file/directory for text/file/dir/lang_detect/word_lookup, id/title for adaptation
    7: translation engine (for detail, see APIinfo.ini)
    8: source language (for detail, see APIinfo.ini)
    9: target language (for detail, see APIinfo.ini)
  (for translation)
   10: sentence split option (0:OFF, 1:ON)
   11: translation with context option (0:OFF, 1/2/3:sentence num, 50:only target context)
   12: xml translation option (0:OFF, 1:ON and escape &'"<> characters, 2:ON and escape <>)
  (for bilingual_root/adaptation get)
   10: comma-separated keys and sort orders (key:update, order: ASC or DESC (e.g. update%2CASC))
   11: limit size for results
   12: offset for results
  (for adaptation set/update)
   10: training method (0:adaptation(default), 1:adaptation+EBMT, 2:EBMT)
   11: bilingual text selection type (0: data selection(default), 1: all belonging group data)
   12: bilingual text (forward direction) IDs for train set, multiple bilingual text IDs must be separated by commas (e.g. 12345%2C12346)
   13: bilingual text (backward direction) IDs for train set, multiple bilingual text IDs must be separated by commas (e.g. 23456%2C23457)
   14: whether to use document data or not (0: without data(default), 1: all belonging group data)
   15: whether to use recycled data or not (0: without data(default), 1: all belonging group data)
   16: bilingual text (forward direction) IDs for dev set, multiple bilingual text IDs must be separated by commas (e.g. 34567%2C34568)
   17: bilingual text (forward direction) IDs for dev set, multiple bilingual text IDs must be separated by commas (e.g. 45678%2C45679)
   18: bilingual text (forward direction) IDs for test set, multiple bilingual text IDs must be separated by commas (e.g. 56789%2C56790)
   19: bilingual text (forward direction) IDs for test set, multiple bilingual text IDs must be separated by commas (e.g. 67890%2C67891)
   20: autoupdate option (0: off, 1: on)
"""

import sys
from requests_oauthlib import OAuth1
import requests as req
import json

NAME = sys.argv[1]
KEY = sys.argv[2]
SECRET = sys.argv[3]

KIND = sys.argv[4]          # text/file/lang_detect/word_lookup/bilingual_root/adaptation
SUBKIND = sys.argv[5]       # file: set/status/get, bilingual_root: get, adaptation: set/status/get
SRC = sys.argv[6]
ENGINE = 'generalNT' if (len(sys.argv) <= 7 or sys.argv[7] == '') else sys.argv[7]
SRC_LANG = 'ja' if (len(sys.argv) <= 8 or sys.argv[8] == '') else sys.argv[8]
TGT_LANG = 'en' if (len(sys.argv) <= 9 or sys.argv[9] == '') else sys.argv[9]

## for translation
if KIND == 'text' or KIND == 'file' or KIND == 'lang_detect' or KIND == 'word_lookup':
  SPLIT = '0' if (len(sys.argv) <= 10 or sys.argv[10] == '') else sys.argv[10]
  HISTORY = '0' if (len(sys.argv) <= 11 or sys.argv[11] == '') else sys.argv[11]
  XML = '0' if (len(sys.argv) <= 12 or sys.argv[12] == '') else sys.argv[12]
  DEBUG = '' if (len(sys.argv) <= 13 or sys.argv[13] == '') else sys.argv[13]

## for bilingual_root/adaptation get
if ( KIND == 'bilingual_root' or KIND == 'adaptation' ) and SUBKIND == 'get':
  ORDER = '0' if (len(sys.argv) <= 10 or sys.argv[10] == '') else sys.argv[10]
  LIMIT = '0' if (len(sys.argv) <= 11 or sys.argv[11] == '') else sys.argv[11]
  OFFSET = '0' if (len(sys.argv) <= 12 or sys.argv[12] == '') else sys.argv[12]
  DEBUG = '' if (len(sys.argv) <= 13 or sys.argv[13] == '') else sys.argv[13]

## for adaptation set/update
if KIND == 'adaptation' and ( SUBKIND == 'get' or 'update' ):
  SIMMAP = '0' if (len(sys.argv) <= 10 or sys.argv[10] == '') else sys.argv[10]
  USEBILINGUAL = '0' if (len(sys.argv) <= 11 or sys.argv[11] == '') else sys.argv[11]
  BILINGUAL_N = '' if (len(sys.argv) <= 12 or sys.argv[12] == '') else sys.argv[12]
  BILINGUAL_R = '' if (len(sys.argv) <= 13 or sys.argv[13] == '') else sys.argv[13]
  USEDOC = '0' if (len(sys.argv) <= 14 or sys.argv[14] == '') else sys.argv[14]
  USELOG = '0' if (len(sys.argv) <= 15 or sys.argv[15] == '') else sys.argv[15]
  DEV_N = '' if (len(sys.argv) <= 16 or sys.argv[16] == '') else sys.argv[16]
  DEV_R = '' if (len(sys.argv) <= 17 or sys.argv[17] == '') else sys.argv[17]
  TEST_N = '' if (len(sys.argv) <= 18 or sys.argv[18] == '') else sys.argv[18]
  TEST_R = '' if (len(sys.argv) <= 19 or sys.argv[19] == '') else sys.argv[19]
  AUTOUPDATE = '0' if (len(sys.argv) <= 20 or sys.argv[20] == '') else sys.argv[20]
  DEBUG = '' if (len(sys.argv) <= 21 or sys.argv[21] == '') else sys.argv[21]


URL = ''
URL_BASE = 'https://mt-auto-minhon-mlt.ucri.jgn-x.jp/api/'
if KIND == 'text':
  URL = URL_BASE + 'mt/' + ENGINE + '_' + SRC_LANG + '_' + TGT_LANG + '/'
if KIND == 'file':
  URL = URL_BASE + 'trans_file/' + SUBKIND + '/'
if KIND == 'lang_detect':
  URL = URL_BASE + 'langdetect/'
if KIND == 'word_lookup':
  URL = URL_BASE + 'lookup/'
if KIND == 'bilingual_root':
  if SUBKIND == 'get':
    URL = URL_BASE + 'bilingual_root/get/'
if KIND == 'adaptation':
  if SUBKIND == 'set':
    URL = URL_BASE + 'mt_adapt/set/'
  elif SUBKIND == 'update':
    URL = URL_BASE + 'mt_adapt/update/'
  elif SUBKIND == 'get':
    URL = URL_BASE + 'mt_adapt/get/'

consumer = OAuth1(KEY , SECRET)
TGT = ''

if KIND == 'text':
  params = {
    'key': KEY,
    'name': NAME,
    'type': 'json',
    'text': SRC,
    'split': SPLIT,
    'history': HISTORY,
    'xml': XML,
  }
if KIND == 'file' and SUBKIND == 'set':
  FILE = {'file': open(SRC, 'rb')}
  TITLE = SRC
  if len(SRC) > 20:
    TITLE = SRC[-20:]
  params = {
    'key': KEY,
    'name': NAME,
    'type': 'json',
    'title': TITLE,
    'file': FILE,
    'mt_id': ENGINE + '_' + SRC_LANG + '_' + TGT_LANG,
    'split': SPLIT,
    'history': HISTORY,
    'xml': XML,
  }
if KIND == 'file' and SUBKIND == 'status':
  params = {
    'key': KEY,
    'name': NAME,
    'type': 'json',
    'pid': SRC,
  }
if KIND == 'file' and SUBKIND == 'get':
  params = {
    'key': KEY,
    'name': NAME,
    'type': 'json',
    'pid': SRC,
  }
if KIND == 'lang_detect':
  params = {
    'key': KEY,
    'name': NAME,
    'type': 'json',
    'text': SRC,
  }
if KIND == 'word_lookup':
  params = {
    'key': KEY,
    'name': NAME,
    'type': 'json',
    'text': SRC,
    'pid': ENGINE,
    'lang_s': SRC_LANG,
  }
if KIND == 'bilingual_root' and SUBKIND == 'get':
  params = {
    'key': KEY,
    'name': NAME,
    'type': 'json',
    'lang_s' : SRC_LANG,
    'lang_t' : TGT_LANG,
    'order':ORDER,
    'limit':LIMIT,
    'offset':OFFSET
  }
  if SRC_LANG == '' :
    params.pop('lang_s')
  if TGT_LANG == '' :
    params.pop('lang_t')
  if ORDER == '' :
    params.pop('order')
  if LIMIT == '' :
    params.pop('limit')
  if OFFSET == '' :
    params.pop('offset')
if KIND == 'adaptation' and SUBKIND == 'set':
  params = {
    'key': KEY,
    'name': NAME,
    'type': 'json',
    'title' : SRC,
    'lang_s' : SRC_LANG,
    'lang_t' : TGT_LANG,
    'base' : ENGINE,
    'simmap' : SIMMAP,
    'usebilingual' : USEBILINGUAL,
    'bilingual_n' : BILINGUAL_N,
    'bilingual_r' : BILINGUAL_R,
    'usedoc' : USEDOC,
    'uselog' : USELOG,
    'dev_n' : DEV_N,
    'dev_r' : DEV_R,
    'test_n' : TEST_N,
    'test_r' : TEST_R,
    'autoupdate' : AUTOUPDATE
  }
if KIND == 'adaptation' and SUBKIND == 'update':
  params = {
    'key': KEY,
    'name': NAME,
    'type': 'json',
    'id': SRC,
    'title' : SRC+'_update',
    'lang_s' : SRC_LANG,
    'lang_t' : TGT_LANG,
    'base' : ENGINE,
    'simmap' : SIMMAP,
    'usebilingual' : USEBILINGUAL,
    'bilingual_n' : BILINGUAL_N,
    'bilingual_r' : BILINGUAL_R,
    'usedoc' : USEDOC,
    'uselog' : USELOG,
    'dev_n' : DEV_N,
    'dev_r' : DEV_R,
    'test_n' : TEST_N,
    'test_r' : TEST_R,
    'autoupdate' : AUTOUPDATE
  }
if KIND == 'adaptation' and SUBKIND == 'get':
  params = {
    'key': KEY,
    'name': NAME,
    'type': 'json',
    'lang_s' : SRC_LANG,
    'lang_t' : TGT_LANG,
    'order':ORDER,
    'limit':LIMIT,
    'offset':OFFSET
  }
  if SRC_LANG == '' :
    params.pop('lang_s')
  if TGT_LANG == '' :
    params.pop('lang_t')
  if ORDER == '' :
    params.pop('order')
  if LIMIT == '' :
    params.pop('limit')
  if OFFSET == '' :
    params.pop('offset')

try:
  if KIND == 'text':
    res = req.post(URL, data=params, auth=consumer)
  if KIND == 'file' and SUBKIND == 'set':
    res = req.post(URL, data=params, params=params, auth=consumer, files=FILE)
  if KIND == 'file' and SUBKIND == 'status':
    res = req.post(URL, data=params, auth=consumer)
  if KIND == 'file' and SUBKIND == 'get':
    res = req.post(URL, data=params, auth=consumer)
  if KIND == 'lang_detect':
    res = req.post(URL, data=params, auth=consumer)
  if KIND == 'word_lookup':
    res = req.post(URL, data=params, auth=consumer)
  if KIND == 'bilingual_root' and SUBKIND == 'get':
    res = req.post(URL, data=params, auth=consumer)
  if KIND == 'adaptation' and SUBKIND == 'set':
    res = req.post(URL, data=params, auth=consumer)
  if KIND == 'adaptation' and SUBKIND == 'update':
    res = req.post(URL, data=params, auth=consumer)
  if KIND == 'adaptation' and SUBKIND == 'get':
    res = req.post(URL, data=params, auth=consumer)
  res.encoding = 'utf-8'
  if DEBUG == 'print_res':
    print('[res]')
    print(res)
    print(res.text)
  if KIND == 'text':
    d = json.loads(res.text)
    if len(d['resultset']['result']['information']) != 0:
      for n in range(len(d['resultset']['result']['information']['sentence'])):
        TGT = TGT + d['resultset']['result']['information']['sentence'][n]['text-t']
        if n != len(d['resultset']['result']['information']['sentence']) - 1:
          TGT = TGT + '\n'
    else:
      TGT = d['resultset']['result']['text']
  if KIND == 'file' and SUBKIND == 'set':
    d = json.loads(res.text)
    TGT = d['resultset']['result']['pid']
  if KIND == 'file' and SUBKIND == 'status':
    d = json.loads(res.text)
    TGT = d['resultset']['result']['list'][0]['state']
  if KIND == 'file' and SUBKIND == 'get':
    with open(ENGINE, mode='wb') as fout:  # use ENGINE parameter as target file name
      fout.write(res.content)
      TGT=ENGINE
  if KIND == 'lang_detect':
    d = json.loads(res.text)
    TGT = TGT + d['resultset']['result']['langdetect']['1']['lang']
  if KIND == 'word_lookup':
    d = json.loads(res.text)
    if len(d['resultset']['result']['lookup']) != 0:
      for n in range(len(d['resultset']['result']['lookup'][0]['term'])):
        TGT = TGT + d['resultset']['result']['lookup'][0]['term'][n]['target'] + '\n'
    else:
      TGT = ''
  if KIND == 'bilingual_root' and SUBKIND == 'get':
    d = json.loads(res.text)
    for n in range(len(d['resultset']['result']['list'])):
      TGT = TGT + json.dumps(d['resultset']['result']['list'][n], ensure_ascii=False) + '\n'
  if KIND == 'adaptation' and SUBKIND == 'set':
    d = json.loads(res.text)
    TGT = d['resultset']['result']['id']
  if KIND == 'adaptation' and SUBKIND == 'update':
    d = json.loads(res.text)
    TGT = d['resultset']['result']['id']
  if KIND == 'adaptation' and SUBKIND == 'get':
    d = json.loads(res.text)
    for n in range(len(d['resultset']['result']['list'])):
      TGT = TGT + json.dumps(d['resultset']['result']['list'][n], ensure_ascii=False) + '\n'
  print(TGT)
except Exception as e:
  print('=== Error ===')
  print('type:' + str(type(e)))
  print('args:' + str(e.args))
  print('e:' + str(e))

