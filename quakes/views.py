import datetime
from datetime import timedelta
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render_to_response
from django.template import RequestContext
#from quakes.decorators import json, gzip
from quakes.models import Quake


#@gzip
#@json
def earthquakes(request):
    data = {}
    weekago = datetime.datetime.now() - datetime.timedelta(days=7)
    quakes = Quake.objects.filter(datetime__gte=weekago).order_by('-datetime')
    bounds = getattr(settings, 'BOUNDS', None)
    if bounds is not None:
        quakes = quakes.filter(point__contained=bounds)
    for quake in quakes:
        if quake.date > datetime.datetime.now() - timedelta(hours=1):
            timeframe = "h"
        elif quake.date > datetime.datetime.now() - timedelta(days=1):
            timeframe = "d"
        else:
            timeframe = "w"
        if int(quake.magnitude) < 2:
            continue
        data[quake.eqid] = {
            'eqid': quake.eqid,
            'magnitude': quake.magnitude,
            'timeframe': timeframe,
            'lat': quake.point.coords[1],
            'lon': quake.point.coords[0],
        }
    return data


def earthquake_display(request):
    weekago = datetime.datetime.now() - datetime.timedelta(days=7)
    quakes = Quake.objects.filter(datetime__gte=weekago).order_by('-datetime')

    last_check = cache.get('usgs-poll-last-finished', datetime.datetime(2000, 1, 1))
    checking = cache.get('usgs-poll-in-progress', False)
    if not checking:
        cache.set('usgs-poll-in-progress', True)
        latest_quake_ago = datetime.datetime.now() - quakes[0].datetime
        latest_check_ago = datetime.datetime.now() - last_check
        if latest_quake_ago > datetime.timedelta(minutes=5) and latest_check_ago > datetime.timedelta(minutes=5):
            from django.core import management
            management.call_command('load_quakes')
            cache.set('usgs-poll-last-finished', datetime.datetime.now())
        cache.delete('usgs-poll-in-progress')
        checking = False

    return render_to_response('earthquakes.html', {
        'object_list': quakes,
        'checking': checking,
    }, context_instance=RequestContext(request))
