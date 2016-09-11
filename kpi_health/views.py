from django.shortcuts import render
from django.http import HttpResponse

from urllib.parse import urlencode, urljoin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import requests
import base64

import os
from .models import FitbitCredentials
import fitbit


FITBIT_CLIENT_ID = os.environ.get('FITBIT_CLIENT_ID', 'redacted')
FITBIT_SECRET_KEY = os.environ.get('FITBIT_SECRET_KEY', 'redacted')
FITBIT_REDIRECT_URI = 'http://192.168.1.23'
FITBIT_REDIRECT_URI = 'http://localhost'

ALL_SCOPES = 'activity heartrate location nutrition profile settings sleep social weight'


def revoke_token(user):
    fc = FitbitCredentials.objects.get(user=user)
    data = {
        'token':fc.access_token,
    }
    token = base64.b64encode('{client}:{secret}'.format(client=FITBIT_CLIENT_ID, 
                                                        secret=FITBIT_SECRET_KEY).encode())
    headers = {
        'Authorization': 'Basic {token}'.format(token=token.decode()),
    }
    print(headers)
    resp = requests.post('https://api.fitbit.com/oauth2/revoke', 
                            headers=headers,
                            data=data).json()
    print(resp)
    fc.delete()

def refresh_token(user):
    fc = FitbitCredentials.objects.get(user=user)
    data = {
        'grant_type':'refresh_token',
        'response_type':'token',
        'client_id': FITBIT_CLIENT_ID,
        'refresh_token': fc.refresh_token
    }
    token = base64.b64encode('{client}:{secret}'.format(client=FITBIT_CLIENT_ID, 
                                                        secret=FITBIT_SECRET_KEY).encode())
    headers = {
        'Authorization': 'Basic {token}'.format(token=token.decode()),
    }
    print(headers)
    resp = requests.post('https://api.fitbit.com/oauth2/token', 
                            headers=headers,
                            data=data).json()
    print(resp)
    try:
        FitbitCredentials.objects.filter(
            user=user,
        ).update(access_token=resp['access_token'])
    except KeyError:
        pass


def get_tokens(user, code):
    data = {
        'code':code,
        'grant_type':'authorization_code',
        'client_id': FITBIT_CLIENT_ID,
        'redirect_uri': FITBIT_REDIRECT_URI,
    }
    token = base64.b64encode('{client}:{secret}'.format(client=FITBIT_CLIENT_ID, 
                                                        secret=FITBIT_SECRET_KEY).encode())
    headers = {
        'Authorization': 'Basic {token}'.format(token=token.decode()),
    }
    print(headers)
    resp = requests.post('https://api.fitbit.com/oauth2/token', 
                            headers=headers,
                            data=data).json()
    print(resp)
    try:
        FitbitCredentials.objects.create(
            user=user,
            fitbit_user_id=resp['user_id'],
            access_token=resp['access_token'],
            refresh_token=resp['refresh_token'],
            scopes=resp['scope'],
        )
    except KeyError:
        pass

@login_required
def index(request):
    data = {
        'client_id':FITBIT_CLIENT_ID,
        'response_type':'code',
        'scope': ALL_SCOPES,
        'redirect_uri': FITBIT_REDIRECT_URI,
        'expires_in':'31536000',
    }


    base_url = 'https://api.fitbit.com/1'
    authorize_url ='https://www.fitbit.com/oauth2/authorize?'
    href = authorize_url+ urlencode(data)
    bttn = '<a name="one" href="{href}">fitbit</a>'.format(href=href)

    code = request.GET.get('code', None)
    content = None
    if code:
        get_tokens(request.user, code)

    sleep_info = ""
    for fc in FitbitCredentials.objects.all():
        yesterday = timezone.now() - timezone.timedelta(days=1)
        fitbit_api = fitbit.Fitbit(FITBIT_CLIENT_ID,
                               FITBIT_SECRET_KEY,
                               access_token=fc.access_token,
                               refresh_token=fc.refresh_token)
        sleep_data = fitbit_api.sleep(date=yesterday)
        time_sleepin = sleep_data['summary']['totalMinutesAsleep'] / 60

        sleep_info += "{user} was asleep for {h} hours. </br>".format(user=fc.user, h=time_sleepin)



    credentials = list(FitbitCredentials.objects.all().values_list('fitbit_user_id', 'user__username'))

    return HttpResponse('{btn} {sleep_info}'.format(
        btn=bttn,
        sleep_info=sleep_info
    ))

    # return HttpResponse('Hello World {user} {fitbit_client_id}'
    #                     ' {btn} {resp} {credentials}'
    #                     ' {sleep_info}'.format(
    #     fitbit_client_id=fitbit_client_id,
    #     btn=bttn,
    #     resp=content,
    #     credentials=credentials,
    #     user=request.user,
    #     sleep_info=sleep_info
    # ))
    #return HttpResponse("No sir!")
# Create your views here.
