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



ALL_SCOPES = 'activity heartrate location nutrition profile settings sleep social weight'


@login_required
def index(request):
    fitbit_client_id = os.environ.get('FITBIT_CLIENT_ID', 'redacted')
    fitbit_secret_key = os.environ.get('FITBIT_SECRET_KEY', 'redacted')
    fitbit_redirect_uri = 'http://192.168.1.23'
    data = {
        'client_id':fitbit_client_id,
        'response_type':'code',
        'scope': ALL_SCOPES,
        'redirect_uri': fitbit_redirect_uri,
        'expires_in':'31536000',
    }


    base_url = 'https://api.fitbit.com/1'
    authorize_url ='https://www.fitbit.com/oauth2/authorize?'
    href = authorize_url+ urlencode(data)
    bttn = '<a name="one" href="{href}">fitbit</a>'.format(href=href)

    code = request.GET.get('code', None)
    content = None
    if code:
        data = {
            'code':code,
            'grant_type':'authorization_code',
            'client_id': fitbit_client_id,
            'redirect_uri': fitbit_redirect_uri,
        }
        token = base64.b64encode('{client}:{secret}'.format(client=fitbit_client_id, secret=fitbit_secret_key).encode())
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
                user=request.user,
                fitbit_user_id=resp['user_id'],
                access_token=resp['access_token'],
                refresh_token=resp['refresh_token'],
                scopes=resp['scope'],
            )
        except KeyError:
            pass
        content = resp

    sleep_info = ""
    for fc in FitbitCredentials.objects.all():
        yesterday = timezone.now() - timezone.timedelta(days=1)
        fitbit_api = fitbit.Fitbit(fitbit_client_id,
                               fitbit_secret_key,
                               access_token=fc.access_token,
                               refresh_token=fc.refresh_token)
        sleep_data = fitbit_api.sleep(date=yesterday)
        time_sleepin = sleep_data['summary']['totalMinutesAsleep'] / 60

        sleep_info += "{user} was asleep for {h} hours. </br>".format(user=fc.user, h=time_sleepin)



    credentials = list(FitbitCredentials.objects.all().values_list('fitbit_user_id', 'user__username'))

    return HttpResponse('{sleep_info}'.format(
        fitbit_client_id=fitbit_client_id,
        btn=bttn,
        resp=content,
        credentials=credentials,
        user=request.user,
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
