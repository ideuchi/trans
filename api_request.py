# -*- coding: utf-8 -*-
"""
Python3 OAuthRequest Module for NICT translation API
  prerequisites:
    creating account via the following URL:
      https://mt-auto-minhon-mlt.ucri.jgn-x.jp/content/register/
      after creating account, you can get "name", "key", "secret" parameters.
  parameters:
    1: name
    2: key
    3: secret
    4: translation kind (text/file/dir/lang_detect)
    5: translation subkind (for file translation)
    6: source text/file/directory
    7: translation engine (for detail, see APIinfo.ini)
    8: source language (for detail, see APIinfo.ini)
    9: target language (for detail, see APIinfo.ini)
"""

import sys
from requests_oauthlib import OAuth1
import requests as req
import json

NAME = sys.argv[1]
KEY = sys.argv[2]
SECRET = sys.argv[3]

KIND = sys.argv[4]          # text/file/dir/lang_detect
SUBKIND = sys.argv[5]       # file: set/status/get, 
SRC = sys.argv[6]
ENGINE = '' if len(sys.argv) <= 7 else sys.argv[7]
SRC_LANG = '' if len(sys.argv) <= 8 else sys.argv[8]
TGT_LANG = '' if len(sys.argv) <= 9 else sys.argv[9]
DEBUG = '' if len(sys.argv) <= 10 else sys.argv[10]

URL = ''
URL_BASE = 'https://mt-auto-minhon-mlt.ucri.jgn-x.jp/api/'
if KIND == 'text':
  URL = URL_BASE + 'mt/' + ENGINE + '_' + SRC_LANG + '_' + TGT_LANG + '/'
if KIND == 'file':
  URL = URL_BASE + 'trans_file/' + SUBKIND + '/'
if KIND == 'lang_detect':
  URL = URL_BASE + 'langdetect/'

consumer = OAuth1(KEY , SECRET)
TGT = ''

if KIND == 'text':
  params = {
    'key': KEY,
    'name': NAME,
    'text': SRC,
    'type': 'json',
  }
if KIND == 'file' and SUBKIND == 'set':
  FILE = {'file': open(SRC, 'rb')}
  TITLE = SRC
  if len(SRC) > 20:
    TITLE = SRC[-20:]
  params = {
    'key': KEY,
    'name': NAME,
    'title': TITLE,
    'file': FILE,
    'mt_id': ENGINE + '_' + SRC_LANG + '_' + TGT_LANG,
    'type': 'json',
  }
if KIND == 'file' and SUBKIND == 'status':
  params = {
    'key': KEY,
    'name': NAME,
    'pid': SRC,
    'type': 'json',
  }
if KIND == 'file' and SUBKIND == 'get':
  params = {
    'key': KEY,
    'name': NAME,
    'pid': SRC,
    'type': 'json',
  }
if KIND == 'lang_detect':
  params = {
    'key': KEY,
    'name': NAME,
    'text': SRC,
    'type': 'json',
  }

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
  res.encoding = 'utf-8'
  if DEBUG == 'print_res':
    print("[res]")
    print(res)
    print(res.text)
  if KIND == 'text':
    d = json.loads(res.text)
    for n in range(len(d['resultset']['result']['information']['sentence'])):
      TGT = TGT + d['resultset']['result']['information']['sentence'][n]['text-t']
      if n != len(d['resultset']['result']['information']['sentence']) - 1:
        TGT = TGT + '\n'
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
    for n in range(len(d['resultset']['result']['langdetect'])):
      TGT = TGT + d['resultset']['result']['langdetect']['1']['lang']
  print(TGT)
except Exception as e:
  print('=== Error ===')
  print('type:' + str(type(e)))
  print('args:' + str(e.args))
  print('e:' + str(e))

