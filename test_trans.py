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
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import requests as req
import json

NAME = 'ideuchi'
KEY = '4cbebaaf87378bce1f1d63e686b47505058ed757a'
SECRET = '4f852612ee5e73f3978d9d7c801ce733'

client = BackendApplicationClient(client_id=KEY)
oauth = OAuth2Session(client=client)

KIND = 'text'               # text/file/lang_detect/word_lookup/bilingual_root/adaptation
SUBKIND = ''                # file: set/status/get, bilingual_root: get, adaptation: set/status/get
SRC = '今日は金曜日です。'
ENGINE = 'generalNT' if (len(sys.argv) <= 7 or sys.argv[7] == '') else sys.argv[7]
SRC_LANG = 'ja' if (len(sys.argv) <= 8 or sys.argv[8] == '') else sys.argv[8]
TGT_LANG = 'en' if (len(sys.argv) <= 9 or sys.argv[9] == '') else sys.argv[9]

## for translation
if KIND == 'text' or KIND == 'file' or KIND == 'lang_detect' or KIND == 'word_lookup':
  SPLIT = '0' if (len(sys.argv) <= 10 or sys.argv[10] == '') else sys.argv[10]
  HISTORY = '0' if (len(sys.argv) <= 11 or sys.argv[11] == '') else sys.argv[11]
  XML = '0' if (len(sys.argv) <= 12 or sys.argv[12] == '') else sys.argv[12]
  DEBUG = '' if (len(sys.argv) <= 13 or sys.argv[13] == '') else sys.argv[13]


URL = ''
URL_BASE = 'https://mt-auto-minhon-mlt.ucri.jgn-x.jp/api/'
if KIND == 'text':
  URL = URL_BASE + 'mt/' + ENGINE + '_' + SRC_LANG + '_' + TGT_LANG + '/'

if KIND == 'lang_detect':
  URL = URL_BASE + 'langdetect/'


token_url = 'https://mt-auto-minhon-mlt.ucri.jgn-x.jp/oauth2/token.php'
token = oauth.fetch_token(token_url=token_url, client_id=KEY, client_secret=SECRET)
TGT = ''

if KIND == 'text':
  params = {
    'access_token': token['access_token'],
    'key': KEY,
    'name': NAME,
    'type': 'json',
    'text': SRC,
    'split': SPLIT,
    'history': HISTORY,
    'xml': XML,
  }

if KIND == 'lang_detect':
  params = {
    'access_token': token['access_token'],
    'key': KEY,
    'name': NAME,
    'type': 'json',
    'text': SRC,
  }

try:
  if KIND == 'text':
    res = req.post(URL, data=params)
  if KIND == 'lang_detect':
    res = req.post(URL, data=params)
  res.encoding = 'utf-8'
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
  if KIND == 'lang_detect':
    d = json.loads(res.text)
    TGT = TGT + d['resultset']['result']['langdetect']['1']['lang']
  print(TGT)
except Exception as e:
  print('=== Error ===')
  print('type:' + str(type(e)))
  print('args:' + str(e.args))
  print('e:' + str(e))


