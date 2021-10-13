from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json
import os
import time
import datetime
import pytz
import subprocess as sp
import arxiv
import hashlib

from trans_api.trans_util import trans, debug_msg, DEBUG_FILE
from .adapter_slackclient import slack_events_adapter, CLIENT, SLACK_VERIFICATION_TOKEN

# Options to collect latest papers from arXiv
ARXIV_CHECK_CHANNEL = os.environ.get('ARXIV_CHECK_CHANNEL','arxiv')  # This doesn't work because channel ID is needed
ARXIV_CHECK_KEYWORD = os.environ.get('ARXIV_CHECK_KEYWORD','neural machine translation')
ARXIV_CHECK_FROM_DAYS_BEFORE = os.environ.get('ARXIV_CHECK_FROM_DAYS_BEFORE','7')
ARXIV_CHECK_TO_DAYS_BEFORE = os.environ.get('ARXIV_CHECK_TO_DAYS_BEFORE','6')
ARXIV_CHECK_AVOID_DUPLICATED_POSTING = os.environ.get('ARXIV_CHECK_AVOID_DUPLICATED_POSTING','ON')
ARXIV_CHECK_TRANS = os.environ.get('ARXIV_CHECK_TRANS','ja')  # 'none' means no translation

# Create your views here.

def render_json_response(request, data, status=None, support_jsonp=False):
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    callback = request.GET.get('callback')
    if not callback:
        callback = request.POST.get('callback')  # in case of POST and JSONP
    if callback and support_jsonp:
        json_str = '%s(%s)' % (callback, json_str)
        response = HttpResponse(json_str, content_type='application/javascript; charset=UTF-8', status=status)
    else:
        response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=status)
    return response

@csrf_exempt
def slack_events(request, *args, **kwargs):  # cf. https://api.slack.com/events/url_verification
    debug_msg('\n/slack_events called.')
    if request.method == 'GET':
        raise Http404("These are not the slackbots you're looking for.")
    try:
        # https://stackoverflow.com/questions/29780060/trying-to-parse-request-body-from-post-in-django
        event_data = json.loads(request.body.decode('utf-8'))
    except ValueError as e:  # https://stackoverflow.com/questions/4097461/python-valueerror-error-message
        debug_msg('\nValueError: '+str(e))
        return HttpResponse('')
    debug_msg('\nevent_data: '+str(event_data))
    # Echo the URL verification challenge code
    if 'challenge' in event_data:
        return render_json_response(request, {
            'challenge': event_data['challenge']
        })
    # Parse the Event payload and emit the event to the event listener
    if 'event' in event_data:
        # Verify the request token
        request_token = event_data['token']
        if request_token != SLACK_VERIFICATION_TOKEN:
            message = 'Request contains invalid Slack verification token: %s\n' \
                      'Slack adapter has: %s' % (request_token, SLACK_VERIFICATION_TOKEN)
            debug_msg('\n'+message)
            slack_events_adapter.emit('error', 'invalid verification token')
            raise PermissionDenied(message)
        event_type = event_data['event']['type']
        debug_msg('dispatched to slack_events_adapter.')
        slack_events_adapter.emit(event_type, event_data)
        return HttpResponse('')
    # default case
    return HttpResponse('')

ARXIV_MSG_HASHED_FILE = 'arxiv_msg_hashed.txt'

def arxiv_check(request):
    message = '/arxiv_check called.\n'
    dt_now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    # Channel name for posting
    if 'post_channel' in request.GET:
        post_channel = request.GET.get('post_channel')
    else:
        post_channel = ARXIV_CHECK_CHANNEL
    # Keyword for search
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
    else:
        keyword = ARXIV_CHECK_KEYWORD
    # From date of searching papers
    if 'from_days_before' in request.GET:
        from_days_before = int(request.GET.get('from_days_before'))
        dt_from = dt_now - datetime.timedelta(days=from_days_before)
    else:
        dt_from = dt_now - datetime.timedelta(days=int(ARXIV_CHECK_FROM_DAYS_BEFORE))
    # To date of searching papers
    if 'to_days_before' in request.GET:
        to_days_before = int(request.GET.get('to_days_before'))
        dt_to = dt_now - datetime.timedelta(days=to_days_before)
    elif ARXIV_CHECK_TO_DAYS_BEFORE != '':
        dt_to = dt_now - datetime.timedelta(days=int(ARXIV_CHECK_TO_DAYS_BEFORE))
    else:
        dt_to = dt_now
    # Option to avoid duplicated posting
    if 'avoid_duplicated_posting' in request.GET:
        avoid_duplicated_posting = request.GET.get('avoid_duplicated_posting')
    else:
        avoid_duplicated_posting = ARXIV_CHECK_AVOID_DUPLICATED_POSTING
    # Building searching query and getting search result
    arxiv_check_query = 'abs:"'+keyword+'" AND submittedDate:[{} TO {}]'.format(dt_from.strftime('%Y%m%d%H%M%S'), dt_to.strftime('%Y%m%d%H%M%S'))
    message += 'arxiv_check_query: '+arxiv_check_query
    arxiv_search = arxiv.Search(query=arxiv_check_query, sort_by=arxiv.SortCriterion.SubmittedDate)
    # Translation option ('' means on translation)
    if 'trans_tgt_lang' in request.GET:
        trans_tgt_lang = request.GET.get('trans_tgt_lang')
    else:
        trans_tgt_lang = ARXIV_CHECK_TRANS
    # Send search result (one message corresponding to one paper)
    for result in arxiv_search.results():
        paper_info = 'Title: '+result.title+'\n'
        if trans_tgt_lang != 'none':
            paper_info_rep = trans('Title: '+result.title, 'en', trans_tgt_lang)+'\n'
        paper_info += 'Authors: '+', '.join(list(map(str, result.authors)))+'\n'
        paper_info += 'Abstract: '+result.summary.replace('\n', ' ')+'\n'
        if trans_tgt_lang != 'none':
            paper_info_rep += trans('Abstract: '+result.summary.replace('\n', ' '), 'en', trans_tgt_lang)+'\n'
        paper_info += 'PDF URL: '+result.pdf_url+'\n'
        paper_info += 'Published Date: '+result.published.strftime('%Y/%m/%d %H:%M:%S')+'\n'
        # If the same paper_info/channel is already posted recently (recorded in ARXIV_MSG_HASHED_FILE), ignore event
        if avoid_duplicated_posting == 'ON':
            msg_info = 'post_channel: '+post_channel+'\tpaper_info_digest: '+hashlib.sha224(paper_info.encode("utf-8")).hexdigest()
            debug_msg('paper_info_digest created: '+msg_info)
            if os.path.isfile(ARXIV_MSG_HASHED_FILE):
                with open(ARXIV_MSG_HASHED_FILE, 'r') as f:
                    lines = f.readlines()
                    if msg_info+'\n' in lines:
                        debug_msg('This paper_info/channel is already sent: '+msg_info)
                        return HttpResponse('')
            with open(ARXIV_MSG_HASHED_FILE, 'a') as f:
                debug_msg('new paper_info/channel to send: '+msg_info)
                print(msg_info, file=f)
        post_res = CLIENT.api_call(api_method='chat.postMessage', json={'channel': post_channel, 'text': paper_info})
        debug_msg('arXiv english information post_res: '+str(post_res))
        if trans_tgt_lang != 'none':
            CLIENT.api_call(api_method='chat.postMessage', json={'channel': post_channel, 'text': paper_info_rep, 'thread_ts': post_res['ts'] })
        message += '-----\npaper_info_en: \n'+paper_info+'\npaper_info_'+trans_tgt_lang+': '+paper_info_rep+'\n'
    debug_msg('/arxiv_check result:\n' + message)
    return HttpResponse('')

def debug_cat(request):
    message = '/debug_cat called.\n'
    file = DEBUG_FILE
    if 'path' in request.GET:
        file = request.GET.get('path')
    if os.path.isfile(file):
        with open(file, 'r') as f:
            message += '\n\n' + file + ' contents:\n' + f.read()
    debug_msg('/debug_cat result:\n====================\n> ' + message.replace('\n', '\n> ') + '\n====================\n')
    return HttpResponse('<pre>' + message + '</pre>')

def debug_ls(request):
    message = '/debug_ls called.\n'
    message += 'current dir: ' + os.getcwd() + '\n'
    cmd = 'ls -al'
    if 'path' in request.GET:
        cmd += ' ' + request.GET.get('path')
    proc= sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    std_out, std_err = proc.communicate()
    ls_file_name = std_out.decode('utf-8').rstrip()
    message += cmd +' result: ' + '\n' + ls_file_name
    debug_msg('/debug_ls result:\n' + message)
    return HttpResponse('<pre>' + message + '</pre>')

def debug_cmd(request):
    message = '/debug_cmd called.\n'
    cmd = 'echo "debug_cmd called. cmd and params are missing."'
    if 'cmd' in request.GET:
        cmd = request.GET.get('cmd')
    if 'param1' in request.GET:
        cmd += ' ' + request.GET.get('param1')
    if 'param2' in request.GET:
        cmd += ' ' + request.GET.get('param2')
    if 'param3' in request.GET:
        cmd += ' ' + request.GET.get('param3')
    if 'param4' in request.GET:
        cmd += ' ' + request.GET.get('param4')
    if 'param5' in request.GET:
        cmd += ' ' + request.GET.get('param5')
    proc = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    std_out, std_err = proc.communicate()
    message += cmd + ' result: \n  ' + cmd + ' std_out:\n' + std_out.decode('utf-8').rstrip() + '\n  ' + cmd + ' std_err:\n' + std_err.decode('utf-8').rstrip() + '\n'
    debug_msg('/debug_cmd result:\n' + message)
    return HttpResponse('<pre>' + message + '</pre>')

