from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json
import os
import datetime
import subprocess as sp

from .adapter_slackclient import slack_events_adapter, SLACK_VERIFICATION_TOKEN

# Create your views here.

DEBUG_FILE = 'debug.txt'
def debug_msg(str):
    with open(DEBUG_FILE, 'a') as f:
        time = datetime.datetime.now()
        str_time = time.strftime('%Y/%m/%d %H:%M:%S')
        print('\n'+str_time+' '+str+'\n', file=f)

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
    with open(DEBUG_FILE, 'a') as f:
        print('\n'+str_time+' /slack_events called.\n', file=f)
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
            slack_events_adapter.emit('error', 'invalid verification token')
            message = 'Request contains invalid Slack verification token: %s\n' \
                      'Slack adapter has: %s' % (request_token, SLACK_VERIFICATION_TOKEN)
            raise PermissionDenied(message)
            debug_msg('\n'+message)
        event_type = event_data['event']['type']
        debug_msg(' dispatched to slack_events_adapter.')
        slack_events_adapter.emit(event_type, event_data)
        return HttpResponse('')
    # default case
    return HttpResponse('')

def debug_cat(request):
    message = '/debug_cat called.\n'
    file = DEBUG_FILE
    if 'path' in request.GET:
        file = request.GET.get('path')
    if os.path.isfile(file):
        with open(file, 'r') as f:
            message += '\n\n' + file + ' contents:\n' + f.read()
    debug_msg('/debug_cat result:\n' + message)
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
